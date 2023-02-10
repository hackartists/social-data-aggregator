import pandas as pd
import numpy as np
import nltk
import os
import nltk.corpus
from nltk.tokenize import word_tokenize
import re
from nltk import word_tokenize
from nltk.corpus import stopwords
# from nltk.stem import PorterStemmer
from nltk.probability import FreqDist
import csv
import text_processor as tp

class FrequencyMining(tp.TextProcessor):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.text = ""

    def load(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        while date <= end_date:
            filename = "raw-data/{0}-{1:02d}.txt".format(year,month)
            f = open(filename,"r")
            lines = lines + f.read()
            f.close()

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

        self.text = lines
        return lines

    def preprocessing(self, text):
        return self.preproc(text)

    def tokenization(self, text):
        token = [ self.lemmatization(x) for x in word_tokenize(text.lower()) if x not in self.stopwords() ]

        return token

    def frequency(self, tokens):
        ignore_words = ["dao","http","https", "rt", "via", "amp", "great", "good", "back", "con","get","go","based","become","today","like"]
        tokens = [x for x in tokens if x not in ignore_words]
        fdist = FreqDist(tokens)
        fdist1 = fdist.most_common(60)
        return fdist1

    def text_mining(self):
        text = self.load()
        text = self.preprocessing(text)
        tokens = self.tokenization(text)

        return self.frequency(tokens)

    def write_csv(self, filename, data):
        f=open(filename, "w")
        writer=csv.writer(f)
        writer.writerow(["keyword","count"])
        [ writer.writerow([x,y]) for (x,y) in data ]
        f.close()

    def run(self, filename):
        data = self.text_mining()
        self.write_csv(filename, data)
        return data
