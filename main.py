import os
# import logging
# import re

# import nltk
# import nltk.corpus
# import numpy as np
# import pandas as pd
# from nltk.tokenize import word_tokenize
import frequency
import datapool
import detector
import lda
import warnings
import reddit
import network

# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')

warnings.filterwarnings("ignore",category=DeprecationWarning)
# files = [f for f in os.listdir(".") if os.path.isfile(f) & f.endswith(".txt") & f.startswith("20")]
# print(files)
# for f in files:
#     print(f"starting to parse {f}")
#     convert(f)
#     print(f"finished parsing {f}")

# print("finished all")

# f = FrequencyMining(201604, 201801)
# ret = f.run("test-gen1.csv")

# l = LanguageDetector('raw-data/2016-04.csv')

# l = LdaTopicModeling(201604, 201801)
# l.run(10, 'lda_gen1')

# def convert():
#     start_date = 201605
#     end_date = 202212

#     month = start_date % 100
#     end_month = end_date % 100
#     year = int(start_date / 100)
#     date = start_date
#     lines = ""
#     df = []
#     ll = detector.LanguageDetector()
#     while date <= end_date:
#         filename = "raw-data/{0}-{1:02d}.csv".format(year,month)
#         output = "raw-data/pd-{0}-{1:02d}.csv".format(year,month)
#         ll.convert(filename, output)
#         print(f'{filename} -> {output} was completed\n')

#         month = month + 1
#         if month == 13:
#             month = 1
#             year = year + 1
#         date = (year*100) + month
#     data = pd.concat(df)

# generations = [('gen1',201604,201801),('gen2',201802,202003),('gen3',202004,202212)]
# generations = [('gen3',202004,202212)]
generations = [('gen',201604,202212)]
if os.environ['ENV'] == 'TEST':
    generations = [('gen',201604,201604)]
    # logging.info('For testing-purpose, generations will be restricted to 201604')

# d = datapool.DataPool(201604,202212)
# d.load()
min_topics=2
max_topics=20


for (g,s,e) in generations:
    for base in ['reddit', 'raw-data']:
        start_date = s
        end_date = e

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        while date <= end_date:
            n=network.Network(date,date,base)
            n.load_from_files()
            n.make_graph()
            print(f'Finished making a graph for {date}')

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
            print(f'Finished making a graph for {base}')

        # f = frequency.FrequencyMining(s, e, base)
        # f.run(f'output/freq-{base}-{g}.csv')
        # print(f'{g}: frequency has been completed.\n')

        # l = lda.LdaTopicModeling(s, e, base)
        # l = l.run(min_topics,max_topics, f'output/lda-{base}-{g}')
        # print(f'{g}: LDA topic modeling has been completed.\n')

# r = reddit.Reddit(201604, 202212, "dao")
# r.toCsv()
# r.toText()
