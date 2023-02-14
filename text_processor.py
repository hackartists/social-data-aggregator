import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer, SnowballStemmer

class TextProcessor:
    def stopwords(self):
        stop_words = stopwords.words('english')
        stop_words.extend([
            'amp', 'dao', 'daos', 'rt', 'us', 'one',
            'via', 'great', 'good','back','get','best',
            'based','today','like','theres','dont',
            'anywhere','done','time'
        ])
        return stop_words

    def lemmatization(self,text):
        # lemmatizer = WordNetLemmatizer()
        # return lemmatizer.lemmatize(text)
        return text

    def preproc(self, text):
        lines = [ l for l in text.split('\n') ]
        lines = ' '.join(lines)
        converts = [
            ('', ['[^a-zA-Z0-9 ]'], False),
            ('smartcontract', [
                'smart contract',
                'smart contracts',
                'smartcontracts',
            ], True),
            ('companion', ['cmpn'], True),
            ('hypernation8', ['hypernation'], True),
            ('whitelist', ['wl'], True),
            ('world', ['worlds'], True),
            ('luna', ['lunac'], True),
            ('tag', ['tg'], True),
            ('event', ['events'], True),
            ('',[r'http\S+', r'https\S+', '[0-9]+',],True),
            ('dapp',['dapps'],True),
            ('solana',['sol'],True),
            ('reward',['rewards'],True),
            ('token',['tokens'],True),
            ('nft',['nfts'],True),
            ('binance',['bsc'],True),
            ('ethereum',[
                'eth',
                'ether'
            ], True),
            ('coin',['coins'],True),
            ('project', ['projects'], True),
            ('bitcoin', ['btc'], True),
            (' ',['[ ]+'], False),
        ]

        for (dst,srcs,isWord) in converts:
            if isWord:
                for src in srcs:
                    lines = re.sub(f'^{src} ',f'{dst} ',lines, flags=re.IGNORECASE)
                    lines = re.sub(f' {src} ',f' {dst} ',lines, flags=re.IGNORECASE)
                    lines = re.sub(f' {src}$',f' {dst}',lines, flags=re.IGNORECASE)
            else:
                for src in srcs:
                    lines = re.sub(src,dst,lines, flags=re.IGNORECASE)

        lines = re.findall('\w{2,}', lines)
        lines = ' '.join([x for x in lines])

        return lines
