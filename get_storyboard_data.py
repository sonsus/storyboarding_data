from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import os
import codecs
import pickle
import requests
import json

from  ftfy import fix_text


class Crawler(object):
    def __init__(self):
        self.instructable_ids = []
        self.snapguide_ids = []

    def get_instructable_ids(self):
        for i in range(562):
            page = "https://www.instructables.com/cooking/projects/?offset="+str(i*59)
            try:
                os.system('wget -O index.html '+ page)
            except Exception as e:
                print (e)
                continue
            soup = BeautifulSoup(codecs.open("index.html", "r",encoding='utf-8', errors='ignore'), "html.parser")
            for hit in soup.findAll('div', attrs={'class' : 'category-projects-ible'}):
                for a in hit.find_all('a', attrs={'class' : 'ible-title'}):
                    self.instructable_ids.append( a['href'] )
                    print (a['href'])
        return self.instructable_ids

    def get_instructables_data(self, ids):
        recipes = []
        for idd in ids:
            recipe = {}
            context = []
            url = "https://www.instructables.com"+ idd
            '''
            try:
                os.system('wget -O index.html '+ url)
            except Exception as e:
                print (e)
                continue
            soup = BeautifulSoup(codecs.open("index.html", "r",encoding='utf-8', errors='ignore'), "html.parser")
            '''
            try:
                soup = BeautifulSoup(requests.get(url).text, "html.parser")
            except requests.exceptions.RequestException as e:  # for invalid HTTP, Timeout, Toomany redirects
                print(e)
                continue
            title = "None"
            try:
                title = soup.select('h1.header-title')[0].text.strip()
            except Exception as e:
                print (e)
            for stepi, hit in enumerate(soup.findAll('section', attrs={'class' : 'step'})):
                step = {}
                step_title = "None"
                try:
                    step_title = hit.find(attrs={'class' : 'step-title'}).text
                except Exception as e:
                    print (e)
                step['step_title'] = fix_text(step_title)
                try:
                    step_body = hit.find(attrs={'class' : 'step-body'}).text
                except Exception as e:
                    print(e)
                    continue
                step['step_text'] = fix_text(step_body)
                step['step_images'] = []
                imgi = 0
                for el in hit.findAll('img'):
                    if hit.find('div', attrs={'class': 'author-promo'}):
                        continue
                    rename = idd.strip().split("/")[2] + '_' + str(stepi) + '_' + str(imgi)+ ".jpg"
                    rename = fix_text(rename)
                    try:
                        step['step_images'].append( (el['src'], rename ))
                    except Exception as e:
                        step['step_images'].append(("None", rename))
                    imgi += 1
                context.append(step)
            recipe['title'] = title
            recipe['context'] = context
            recipes.append(recipe)
        return recipes

    def get_snapguide_ids(self):
        for i in range(1069):
            page = "https://snapguide.com/guides/topic/food/recent/?page=" + str(i)
            try:
                os.system('wget -O index.html '+ page)
            except Exception as e:
                print(e)
                continue
            soup = BeautifulSoup(codecs.open("index.html", "r",encoding='utf-8', errors='ignore'), "html.parser")
            for hit in soup.findAll('ul', attrs={'class' : 'sg-card-list'}):
                for a in hit.find_all('a'):
                    self.snapguide_ids.append( a['href'] )
                    print (a['href'])
        return self.snapguide_ids

    def get_snapguide_data(self, snapguide_ids):
        recipes = []
        for idd in snapguide_ids:
            recipe = {}
            context = []
            url = "https://snapguide.com"+ idd
            '''
            try:
                os.system('wget -O index.html '+ url)
            except:
                continue
            try:
                soup = BeautifulSoup(codecs.open("index.html", "r",encoding='utf-8', errors='ignore'), "html.parser")
            except Exception as e:  
                print(e)
                continue
            '''
            try:
                soup = BeautifulSoup(requests.get(url).text, "html.parser")
            except requests.exceptions.RequestException as e:  # for invalid HTTP, Timeout, Toomany redirects
                print(e)
                continue
            title = "None"
            try:
                title = soup.select('title')[0].text.strip()
            except Exception as e:
                print (e)
            recipe['title'] = title
            for stepi, hit in enumerate(soup.findAll('div', attrs={'class' : 'step-content'})):
                step = {}
                try:
                    step_title = hit.find(attrs={'class' : 'step-title'}).text
                except:
                    step_title = "None"
                step['step_title'] = fix_text(step_title)
                step_body = "None"
                try:
                    step_body = hit.find(attrs={'class' : 'caption'}).text
                except Exception as e:
                    print (e)
                    continue
                step['step_text'] = fix_text(step_body)
                step['step_images'] = []
                imgi = 0
                for el in hit.findAll('img'):
                    if hit.find('img', attrs={'class': 'step-media'}):
                        if 'auto=webp' not in el['data-src']:
                            rename = (idd.strip().split("/")[2] + '_' + str(stepi) + '_' + str(imgi)+ ".jpg")
                            rename = fix_text(rename)
                            step['step_images'].append( ("https:"+el['data-src'], rename) )
                        imgi += 1
                context.append(step)
            recipe['context'] = context
            recipes.append(recipe)
            #os.system('rm index.html')
        return recipes



def main():
    crawler = Crawler()
    if os.path.exists("./snapguide_ids.pkl"):
        snapguide_ids = pickle.load(open("./snapguide_ids.pkl", 'rb'))
        snapguide_ids = [fixt_text(id) for id in snapguide_ids]
    else:
        snapguide_ids = list(set(crawler.get_snapguide_ids()))
        snapguide_ids = [fix_text(id) for id in snapguide_ids]
        pickle.dump(snapguide_ids, open("snapguide_ids.pkl", 'wb'))
    if not os.path.exists("./snapguide_data.json"):
        snapguide_data = crawler.get_snapguide_data(snapguide_ids)
        with open("snapguide.json", 'w') as fp:
            json.dump(snapguide_data, fp, indent=4)

    if os.path.exists("./instructable_ids.pkl"):
        instructable_ids = pickle.load(open("./instructable_ids.pkl", 'rb'))
        instructable_ids = [fix_text(id) for id in instructable_ids]
    else:
        instructable_ids = crawler.get_instructable_ids()
        instructable_ids = [fix_text(id) for id in instructable_ids]

        pickle.dump(instructable_ids, open("instructable_ids.pkl", 'wb'))
    if not os.path.exists("./instructable_data.json"):
        instructables_data = crawler.get_instructables_data(instructable_ids)
        with open("instructables.json", 'w') as fp:
            json.dump(instructables_data, fp, indent=4)






if __name__== "__main__":
    main()
