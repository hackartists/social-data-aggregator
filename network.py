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

    def load_from_base(self,from_rank):
        f = open(f'network-data/{self.base}-{from_rank}.txt', 'r')
        self.texts = f.read().split('\n')
        f.close()
        if self.rank != from_rank:
            self.texts = [self.preprocessing(t) for t in self.texts]
            self.save()

        return self.texts

    def load(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = []
        while date <= end_date:
            filename = "{2}/pd-{0}-{1:02d}.csv".format(year,month,self.base)
            d = pd.read_csv(filename, engine='python' )
            d= d[d['language'] == 'en']
            for l in d['text'].map(self.preproc).values.tolist():
                l = self.preprocessing(l)
                if l != '':
                    lines = lines + [l]

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
            print(f'finished loading {date}')

        self.texts = lines

        return lines

    def preprocessing(self, text):
        return ' '.join([ w for w in text.split(' ') if w in self.filter and self.filter[w] ]) 

    def save(self):
        f = open(f'network-data/{self.base}-{self.rank}.txt', 'w')
        f.write('\n'.join(self.texts))
        f.close()

    def make_graph_from_base(self):
        corpus = tn.Corpus(pd.Series(self.texts))
        t = tn.Textnet(corpus.tokenized(stem=False,remove_stop_words=False,remove_urls=False,remove_numbers=True,remove_punctuation=False,lower=False))
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
