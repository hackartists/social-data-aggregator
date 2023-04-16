import os
import pickle
import re
from pprint import pprint
# import logging

import gensim
import gensim.corpora as corpora
from gensim.models import Phrases
from gensim.models.coherencemodel import CoherenceModel
from gensim.utils import simple_preprocess
from gensim.corpora.dictionary import Dictionary

import nltk
import pandas as pd
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
from nltk.corpus import stopwords
from wordcloud import WordCloud

import text_processor as tp

# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')

class LdaTopicModeling(tp.TextProcessor):
    def __init__(self, start_date, end_date, base='raw-data'):
        self.start_date = start_date
        self.end_date = end_date
        self.base = base
        self.coherence={
            'c_v':[],
            'u_mass':[],
            'c_uci':[],
            'c_npmi':[],
        }
        self.coherence_per_topics={
            'c_v':[],
            'u_mass':[],
            'c_uci':[],
            'c_npmi':[],
        }

    def load_from_bin(self, filename):
        self.lda_model = pickle.load(filename)

    def load(self):
        start_date = self.start_date
        end_date = self.end_date

        month = start_date % 100
        end_month = end_date % 100
        year = int(start_date / 100)
        date = start_date
        lines = ""
        df = []
        while date <= end_date:
            filename = "{2}/pd-{0}-{1:02d}.csv".format(year,month,self.base)
            d = pd.read_csv(filename, engine='python' )
            d= d[d['language'] == 'en']
            df.append(d)

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
        self.data = pd.concat(df)

    def preprocessing(self):
        self.data = self.data['text'].map(self.preproc)

    def wordcloud(self):
        long_string = ','.join(list(self.data.values))
        wordcloud = WordCloud(background_color="white", max_words=1000, contour_width=3, contour_color='steelblue')

        wordcloud.generate(long_string)
        wordcloud.to_image()

    def prepare(self):
        stop_words = self.stopwords()
        stop_words.extend(['ethereum','bitcoin','binance','solana','blockchain'])

        def sent_to_words(sentences):
            for sentence in sentences:
                yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

        def remove_stopwords(texts):
            return [[ self.lemmatization(word) for word in simple_preprocess(str(doc))
                     if word not in stop_words] for doc in texts]


        data = self.data.values.tolist()
        data_words = list(sent_to_words(data))
        data_words = remove_stopwords(data_words)

        self.id2word = corpora.Dictionary(data_words)
        self.texts = data_words
        self.corpus = [self.id2word.doc2bow(text) for text in self.texts]

    def analysis(self, num_topics):
        lda_model = gensim.models.LdaMulticore(corpus=self.corpus,
                                                    id2word=self.id2word,
                                                    num_topics=num_topics,workers=7)
        return lda_model

    def visualize(self, filename, lda_model):
        LDAvis_data_filepath = os.path.join(filename)

        LDAvis_prepared = gensimvis.prepare(lda_model, self.corpus, self.id2word)
        with open(LDAvis_data_filepath, 'wb') as f:
            pickle.dump(LDAvis_prepared, f)

        pyLDAvis.save_html(LDAvis_prepared, f'{filename}.html')

    def run(self, min_topics, max_topics, filename):
        self.load()
        self.preprocessing()
        self.prepare()
        print('finished preparing')

        for n in range(min_topics, max_topics+1, 1):
            lda_model = self.analysis(n)
            self.visualize(f'{filename}_{n}', lda_model)
            for t in ['c_v','u_mass','c_uci','c_npmi']:
                coherencemodel = CoherenceModel(model=lda_model, texts=self.texts, dictionary=self.id2word, coherence=t)
                self.coherence[t].append(coherencemodel.get_coherence())
                self.coherence_per_topics[t].append(coherencemodel.get_coherence_per_topic())
                print(f'finished {t} coherence measurement')
            print(self.coherence)
            print(self.coherence_per_topics)
            print(f'finished {n}-topics analysis')
