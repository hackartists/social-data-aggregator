import command
import requests
import json
import subprocess
import time

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
            res = command.run(['zstd', '-d', filename])
            elapsed = time.time() - start
            if res.exit == 0:
                print("{1}s: Successful extraction ({0})".format(filename,elapsed))
                print("Starting to filter {0} from {0}".format(self.keyword, base_filename))
                start = time.time()
                res = subprocess.getoutput('cat reddit/{0} | grep \'"subreddit":"dao"\' > reddit/{0}.txt'.format(base_filename))
                elapsed = time.time() - start
                print("{1}s: Saved the filtered output to reddit/{0}.txt".format(base_filename, elapsed))
                subprocess.getoutput('sudo rm -rf reddit/{0}'.format(base_filename))
            else:
                print("Failed to extract {0}".format(filename))

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


