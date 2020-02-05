#! /usr/bin/env python

import json
import os
import sys
import urllib
import urllib.request
import urllib.parse
import random
import time

from bs4 import BeautifulSoup
import requests


class Scraper:
    def __init__(self):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0'})

    def search(self, keyword, maximum):
        print('begin searching', keyword)
        query = self.query_gen(keyword)
        return self.image_search(query, maximum)

    def query_gen(self, keyword):
        page = 0
        while True:
            params = urllib.parse.urlencode({
                'q': keyword,
                'tbm': 'isch',
                'ijn': str(page)})
            yield self.GOOGLE_SEARCH_URL + '?' + params
            page += 1

    def image_search(self, query_gen, maximum):
        result = []
        total = 0
        page = 0

        while True:
            # googleからのban対策で一応
            random_tempo = random.randrange(10)
            time.sleep(random_tempo)

            query_url = next(query_gen)

            print("start page {} download".format(page))
            res = self.session.get(query_url)
            if res.status_code != 200:
                print("Error occur!\n")
                print(res.text)
                exit(1)

            print("end page {} download".format(page))

            html = res.text
            soup = BeautifulSoup(html, 'lxml')
            elements = soup.select('.rg_meta.notranslate')
            jsons = [json.loads(e.get_text()) for e in elements]
            imageURLs = [js['ou'] for js in jsons]
            page += 1

            if not len(imageURLs):
                print('-> no more images')
                break
            elif len(imageURLs) > maximum - total:
                result += imageURLs[:maximum - total]
                break
            else:
                result += imageURLs
                total += len(imageURLs)

        print('-> found', str(len(result)), 'images')
        return result


def main():
    google = Scraper()
    if len(sys.argv) != 3:
        print('invalid argument')
        print('> ./image_collector_cui.py [target name] [download number]')
        sys.exit()
    else:
        name = sys.argv[1]
        data_dir = 'data/'
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('data/' + name, exist_ok=True)

        result = google.search(name, maximum=int(sys.argv[2]))

        download_error = []
        for i in range(len(result)):

            # googleからのban対策で一応
            random_tempo = random.randrange(10)
            time.sleep(random_tempo)

            print('-> downloading image', str(i + 1).zfill(5))
            try:
                urllib.request.urlretrieve(
                    result[i], data_dir + name + '/' + str(i + 1).zfill(5) + '.jpg')
            except:
                print('--> could not download image', str(i + 1).zfill(5))
                download_error.append(i + 1)
                continue

        print('complete download')
        print('├─ download', len(result) - len(download_error), 'images')
        print('└─ could not download', len(
            download_error), 'images', download_error)


if __name__ == '__main__':
    main()
