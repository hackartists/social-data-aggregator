import textnets as tn
import pandas as pd
import text_processor as tp

class Network(tp.TextProcessor):
    def __init__(self, start_date, end_date, base="raw-data"):
        self.start_date = start_date
        self.end_date = end_date
        self.text = ""
        self.base = base
        if base == 'raw-data':
            self.filter = tp.twitter
        else:
            self.filter = tp.reddit_top

    def load_from_base(self):
        f = open(f'network-data/{self.base}.txt', 'r')
        self.text = f.read().split('\n')
        f.close()

        return self.text

    def load_from_files(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = []
        while date <= end_date:
            filename = "{2}/{0}-{1:02d}.txt".format(year,month,self.base)
            f = open(filename,"r")
            lines = lines + f.read().split('\n')
            f.close()

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month

        self.text = lines

        return lines

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

        self.text = lines

        return lines

    def preprocessing(self, text):
        t = self.preproc_line(text)
        return ' '.join([ w for w in t.split(' ') if w in self.filter ])

    def save(self):
        f = open(f'{self.base}.txt', 'w')
        f.write('\n'.join(self.text))
        f.close()

    def run(self):
        corpus = tn.Corpus(pd.Series(self.text))
        t = tn.Textnet(corpus.tokenized())
        words = t.project(node_type="term")
        words.plot(label_nodes=True, scale_nodes_by='strength', target=f'{self.base}.svg', drl_layout=True)

    def make_graph(self):
        corpus = tn.Corpus(pd.Series(self.text))
        t = tn.Textnet(corpus.tokenized())
        words = t.project(node_type="term")
        g = words.graph
        g.vs["label"] = g.vs["id"]
        g.write_gml('network-data/{0}.gml'.format(self.base))
        # words.save_graph(target=f'network-data/{self.base}.gml')
