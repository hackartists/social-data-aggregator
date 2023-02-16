import pandas as pd
import numpy as np
import csv

class DataPool:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.monthly_file = 'output/monthly.csv'

    def load(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        df = []
        csvfile = open(self.monthly_file, 'w', newline='')
        fieldnames = ['date', 'count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        total = 0

        while date <= end_date:
            filename = "raw-data/pd-{0}-{1:02d}.csv".format(year,month)
            d = pd.read_csv(filename, engine='python' )
            d= d[d['language'] == 'en']
            df.append(d)
            l = d.shape[0]
            total += l
            writer.writerow({'date': "{0}-{1:02d}".format(year,month), 'count': '{0}'.format(l)})
            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
        self.data = pd.concat(df)
        print(total)
