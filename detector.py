import pandas as pd
import fasttext

class LanguageDetector:
    def __init__(self):
        self.model = fasttext.load_model('lid.176.bin')

    def d(self, line):
        try:
            return detect(line)
        except:
            return "unknown"

    def convert(self, filename, output):
        df = pd.read_csv(filename, header=None, names=['timestamp','date','text'])
        data = [d.replace("\n"," ") for d in df['text'].to_list() ]
        (langs,distance) = self.model.predict(data)
        langs = [ ' '.join(l).replace('__label__', "") for l in langs ]
        df['language'] = langs
        df.to_csv(output)

        return langs

        # f = open(file)
        # lines = f.read()
        # f.close()
        # lines = [ (l, d(l)) for l in lines.split('\n') ]
        # dic = {}
        # for (line, lang) in lines:
        #     val = dic.get(lang,[])
        #     dic[lang] = val + [line]
        # for k in dic.keys():
        #     dir= f"lang/{k}"
        #     os.makedirs(dir, exist_ok=True)
        #     wf=open(f"{dir}/{file}", "w")
        #     wf.write("\n".join(dic[k]))
        #     wf.close()
        #     print(f"finished on {dir}/{file}")
