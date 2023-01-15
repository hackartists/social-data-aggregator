import os

from langdetect import detect


def d(line):
    try:
        return detect(line)
    except:
        return "unknown"

def convert(file):
    f = open(file)
    lines = f.read()
    f.close()
    lines = [ (l, d(l)) for l in lines.split('\n') ]
    dic = {}
    for (line, lang) in lines:
        val = dic.get(lang,[])
        dic[lang] = val + [line]
    for k in dic.keys():
        dir= f"lang/{k}"
        os.makedirs(dir, exist_ok=True)
        wf=open(f"{dir}/{file}", "w")
        wf.write("\n".join(dic[k]))
        wf.close()
        print(f"finished on {dir}/{file}")

files = [f for f in os.listdir(".") if os.path.isfile(f) & f.endswith(".txt") & f.startswith("20")]
print(files)
for f in files:
    print(f"starting to parse {f}")
    convert(f)
    print(f"finished parsing {f}")

print("finished all")
