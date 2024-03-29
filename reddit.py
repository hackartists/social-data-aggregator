import requests
import json
import subprocess
import time
import detector
import csv
import datetime

class Reddit:
    def __init__(self, start_date, end_date, keyword):
        self.start_date = start_date
        self.end_date = end_date
        self.keyword = keyword

    def extract_subreddit(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        while date <= end_date:
            base_filename = "RS_{0}-{1:02d}".format(year,month)
            filename = "reddit/{0}.zst".format(base_filename)
            print("Extracting {0}".format(filename))
            start = time.time()
            subprocess.getoutput('zstd -d {0} --long=31'.format(filename))
            elapsed = time.time() - start
            print("{1}s: Successful extraction ({0})".format(filename,elapsed))
            print("Starting to filter {0} from {0}".format(self.keyword, base_filename))
            start = time.time()
            with open('reddit/{0}'.format(base_filename)) as f:
                # k = '"subreddit":"{0}"'.format(self.keyword)
                k = '{0}'.format(self.keyword)
                t = 0
                with open('reddit/python-{0}.txt'.format(base_filename), 'w') as w:
                    for line in f:
                        t += 1
                        obj = json.loads(line)
                        meetsTitle = 'title' in obj and 'DAO' in obj['title']
                        meetsSubreddit = 'subreddit' in obj and k in obj['subreddit']

                        if meetsTitle or meetsSubreddit:
                            w.write(line)
                print('total lines: {0}'.format(t))
            elapsed = time.time() - start
            print("{1}s: Saved the filtered output to reddit/python-{0}.txt".format(base_filename, elapsed))
            subprocess.getoutput('sudo rm -rf reddit/{0}'.format(base_filename))

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

    def download(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        while date <= end_date:
            filename = "RS_{0}-{1:02d}.zst".format(year,month)
            local_filename = "reddit/{0}".format(filename)
            url = "http://files.pushshift.io/reddit/submissions/{0}".format(filename)
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=104857600): 
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        #if chunk: 
                        f.write(chunk)
                print("downloaded {0}".format(local_filename))


            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

    def toCsv(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        df = []
        ll = detector.LanguageDetector()
        while date <= end_date:
            filename = 'reddit/python-RS_{0}-{1:02d}.txt'.format(year,month)
            output = 'reddit/pd-{0}-{1:02d}.csv'.format(year,month)
            with open(filename) as f:
                with open(output, 'w') as w:
                    fieldnames = ['timestamp', 'date', 'text', 'language']
                    cf = csv.DictWriter(w, fieldnames=fieldnames)
                    cf.writeheader()

                    for line in f:
                        obj = json.loads(line)
                        text = obj['title']
                        if obj['selftext'] != "":
                            text = text + " " + obj['selftext']
                            text = text.replace('\n',' ')
                        (langs,distance) = ll.model.predict(text)
                        langs = [ l.replace('__label__', "") for l in langs ]
                        cf.writerow({'timestamp': '{0}'.format(obj['created_utc']), 'date':'2000-01-01','text':'{0}'.format(text),'language':','.join(langs) })

            print(f'{filename} -> {output} was completed\n')

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

    def toText(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        ll = detector.LanguageDetector()
        while date <= end_date:
            filename = 'reddit/python-RS_{0}-{1:02d}.txt'.format(year,month)
            output = 'reddit/{0}-{1:02d}.txt'.format(year,month)
            with open(filename) as f:
                with open(output, 'w') as w:
                    for line in f:
                        obj = json.loads(line)
                        text = obj['title']
                        if obj['selftext'] != "":
                            text = text + " " + obj['selftext']
                            text = text.replace('\n',' ')
                        (langs,distance) = ll.model.predict(text)
                        langs = [ l.replace('__label__', "") for l in langs ]
                        if langs.__contains__('en'):
                            w.write('{0}\n'.format(text))

            print(f'{filename} -> {output} was completed\n')

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
