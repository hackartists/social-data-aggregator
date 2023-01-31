import pandas as pd
import os
from wordcloud import WordCloud
import gensim
from gensim.utils import simple_preprocess
import nltk
from nltk.corpus import stopwords
import gensim.corpora as corpora
from pprint import pprint
import pyLDAvis.gensim_models as gensimvis
import pickle 
import pyLDAvis


class LdaTopicModeling:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

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
            filename = "raw-data/pd-{0}-{1:02d}.csv".format(year,month)
            df.append(pd.read_csv(filename, header=None, names=['ts','date','text']))

            month = month + 1
            if month == 13:
                month = 1
                year = year + 1
            date = (year*100) + month
        self.data = pd.concat(df)

    def preproc(self, text):
        lines = [ l for l in text.split('\n') ]
        lines = ' '.join(lines)
        lines = re.sub("(http|ftp|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])"," ",lines.lower())
        lines = re.sub("[^a-zA-Z]"," ",lines.lower())
        lines = re.sub("[ ]+"," ",lines.lower())
        lines = re.sub("smart contract","smartcontract",lines.lower())
        lines = re.sub("smart contracts","smartcontract",lines.lower())
        lines = re.findall('\w{2,}', lines)
        lines = ' '.join([x for x in lines])

        return lines

    def preprocessing(self):
        self.data['text'].map(self.preproc)

    def wordcloud(self):
        long_string = ','.join(list(self.data['text'].values))
        wordcloud = WordCloud(background_color="white", max_words=1000, contour_width=3, contour_color='steelblue')

        wordcloud.generate(long_string)
        wordcloud.to_image()

    def analysis(self, num_topics):
        stop_words = stopwords.words('english')
        stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

        def sent_to_words(sentences):
            for sentence in sentences:
                yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

        def remove_stopwords(texts):
            return [[word for word in simple_preprocess(str(doc)) 
                    if word not in stop_words] for doc in texts]


        data = self.data.text.values.tolist()
        data_words = list(sent_to_words(data))
        data_words = remove_stopwords(data_words)

        self.id2word = corpora.Dictionary(data_words)
        self.texts = data_words
        self.corpus = [self.id2word.doc2bow(text) for text in self.texts]

        self.lda_model = gensim.models.LdaMulticore(corpus=self.corpus,
                                            id2word=self.id2word,
                                            num_topics=num_topics)
        # pprint(lda_model.print_topics())
        # doc_lda = lda_model[corpus]

    def visualize(self, filename):
        # pyLDAvis.enable_notebook()

        LDAvis_data_filepath = os.path.join(filename)

        if 1 == 1:
            LDAvis_prepared = gensimvis.prepare(self.lda_model, self.corpus, self.id2word)
            with open(LDAvis_data_filepath, 'wb') as f:
                pickle.dump(LDAvis_prepared, f)

        with open(LDAvis_data_filepath, 'rb') as f:
            LDAvis_prepared = pickle.load(f)

        pyLDAvis.save_html(LDAvis_prepared, f'{filename}.html')

    def run(self, num_topics, filename):
        self.load()
        self.preprocessing()
        self.analysis(num_topics)
        self.visualize(filename)

