import pandas as pd
import textnets as tn
import logging

import text_processor as tp
import lda

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


class Network(lda.LdaTopicModeling):
    def __init__(self, start_date, end_date, base="raw-data", rank=100):
        self.start_date = start_date
        self.end_date = end_date
        self.text = ""
        self.base = base
        self.rank = rank
        if base == 'raw-data':
            self.filter = tp.dict_by_rank('twitter', self.rank)
        else:
            self.filter = tp.dict_by_rank('reddit', self.rank)
        super().__init__(start_date, end_date, base)

    def load_from_base(self):
        f = open(f'network-data/{self.base}.txt', 'r')
        self.texts = f.read().split('\n')
        f.close()
        if self.rank != 100:
            self.texts = [self.preprocessing(t) for t in self.texts]
            self.save()

        return self.texts

    def load_from_files(self):
        self.load()
        self.preprocessing()

    def load(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = []
        while date <= end_date:
            filename = "{2}/{0}-{1:02d}.txt".format(year,month,self.base)
            f = open(filename,"r")
            for l in f.read().split('\n'):
                l = self.preprocessing(l)
                if l != '' and ' ' in l:
                    lines = lines + [l]
            f.close()

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

        self.texts = lines

        return lines

    def preprocessing(self, text):
        t = self.preproc_line(text)
        return ' '.join([ w for w in t.split(' ') if w in self.filter and self.filter[w] ]) 

    def save(self):
        f = open(f'network-data/{self.base}-{self.rank}.txt', 'w')
        f.write('\n'.join(self.texts))
        f.close()

    def make_graph_from_base(self):
        corpus = tn.Corpus(pd.Series(self.texts))
        t = tn.Textnet(corpus.tokenized(stem=False))
        print('completed tokenization')
        words = t.project(node_type="term")
        g = words.graph
        g.vs["label"] = g.vs["id"]
        print('it will make a graph model')
        g.write_gml('network-data/{0}-top-{1}.gml'.format(self.base, self.rank))

    def make_graph(self):
        self.prepare()
        self.texts = [' '.join(text) for text in self.texts]
        self.make_graph_from_base()
