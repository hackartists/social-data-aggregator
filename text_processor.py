import re

from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer, WordNetLemmatizer

reddit_top_100 = [
    "nft",
    "game",
    "token",
    "project",
    "airdrop",
    "community",
    "launch",
    "cryptocurrency",
    "bnb",
    "ethereum",
    "solana",
    "usdq",
    "astrosphere",
    "field",
    "apollo",
    "discord",
    "smartcontract",
    "join",
    "website",
    "holders",
    "defi",
    "governance",
    "price",
    "blockchain",
    "july",
    "decentralized",
    "chain",
    "reward",
    "victory",
    "platform",
    "telegram",
    "liquidity",
    "buy",
    "event",
    "usa",
    "gas",
    "ecosystem",
    "bitcoin",
    "value",
    "kaiba",
    "locked",
    "access",
    "mint",
    "staking",
    "market",
    "official",
    "coin",
    "links",
    "world",
    "system",
    "utility",
    "live",
    "tech",
    "makerdao",
    "development",
    "protocol",
    "exclusive",
    "voting",
    "server",
    "investment",
    "assets",
    "story",
    "wallet",
    "vote",
    "twitter",
    "stablecoin",
    "space",
    "latest",
    "ownership",
    "lost",
    "cards",
    "connections",
    "network",
    "ape",
    "dex",
    "majority",
    "dai",
    "tackle",
    "introduce",
    "host",
    "tournaments",
    "metaverse",
    "momentum",
    "listed",
    "charges",
    "promotions",
    "rage",
    "medical",
    "members",
    "fueled",
    "captain",
    "snippet",
    "rushes",
    "chance",
    "astrospherenft",
    "earn",
    "presale",
    "supply",
    "exchange",
    "marketing"
]

twitter_top_100 = [
    "nft",
    "airdrop",
    "cryptocurrency",
    "defi",
    "ethereum",
    "community",
    "web3",
    "blockchain",
    "bnb",
    "metaverse",
    "token",
    "join",
    "bitcoin",
    "solana",
    "launch",
    "hypernation8",
    "reward",
    "binance",
    "gamefi",
    "whitelist",
    "xhashtag",
    "decentralized",
    "luna",
    "event",
    "cmpn",
    "staking",
    "winners",
    "glodao",
    "ido",
    "utc",
    "top",
    "eventdao",
    "cisla",
    "tag",
    "game",
    "chance",
    "governance",
    "people",
    "random",
    "discord",
    "lets",
    "floki",
    "bullish",
    "mint",
    "earn",
    "sale",
    "buy",
    "wallet",
    "campaign",
    "ecosystem",
    "fortprotocol",
    "p2e",
    "altcoin",
    "swap",
    "exchange",
    "usdt",
    "utility",
    "dapp",
    "development",
    "coin",
    "participate",
    "price",
    "companionto",
    "elonmusk",
    "support",
    "holders",
    "avax",
    "money",
    "presale",
    "gaming",
    "market",
    "vote",
    "ama",
    "socialfi",
    "glodaoofficial",
    "meme",
    "finance",
    "protocol",
    "coinmarketcap",
    "yoleeuniverse",
    "trading",
    "ada",
    "listing",
    "shib",
    "polygon",
    "tipmeacoffee",
    "read",
    "doge",
    "invite",
    "vidt",
    "technology",
    "social",
    "claim",
    "public",
    "profits",
    "opensea",
    "daoverse",
    "meta",
    "thedaomaker",
    "czbinance"
]

top_100 = {
    "reddit": reddit_top_100,
    "twitter": twitter_top_100
}

def dict_by_rank(typ,count):
    ret = {}
    for i in range(0,count,1):
        ret[top_100[typ][i]] = True

    return ret

class TextProcessor:
    def stopwords(self):
        stop_words = stopwords.words("english")
        stop_words.extend(
            [
                "amp",
                "dao",
                "daos",
                "rt",
                "us",
                "one",
                "via",
                "great",
                "good",
                "back",
                "get",
                "best",
                "based",
                "today",
                "like",
                "theres",
                "dont",
                "anywhere",
                "done",
                "time",
                "hello",
                "im",
                "retweet",
            ]
        )
        return stop_words

    def lemmatization(self, text):
        # lemmatizer = WordNetLemmatizer()
        # return lemmatizer.lemmatize(text)
        return text

    def preproc_line(self, line):
        converts = [
            ("", ["[^a-zA-Z0-9 ]"], False),
            ("cryptocurrency", ["crypto", "cryptocurrencies"], True),
            ("cisla", ["cryptoislanddao", "crypto island dao"], True),
            ("profit", ["profits"], True),
            (
                "airdrop",
                ["giveaway", "nftgiveaway", "give away", "airdrops", "giveaways"],
                True,
            ),
            ("bnb", ["bnbchain", "bsc"], True),
            ("xhashtag", ["xtag", "xhashtagio"], True),
            (
                "smartcontract",
                [
                    "smart contract",
                    "smart contracts",
                    "smartcontracts",
                ],
                True,
            ),
            ("elonmusk", ["elon musk"], True),
            ("launch", ["launched", "launching"], True),
            ("companion", ["cmpn"], True),
            ("hypernation8", ["hypernation"], True),
            ("whitelist", ["wl"], True),
            ("world", ["worlds"], True),
            ("luna", ["lunac", "lunc"], True),
            ("tag", ["tg"], True),
            ("event", ["events"], True),
            (
                "",
                [
                    r"http\S+",
                    r"https\S+",
                    "[0-9]+",
                ],
                True,
            ),
            ("dapp", ["dapps"], True),
            ("solana", ["sol"], True),
            ("reward", ["rewards"], True),
            ("token", ["tokens"], True),
            ("nft", ["nfts"], True),
            ("community", ["nftcommunity"], True),
            ("ethereum", ["eth", "ether"], True),
            ("coin", ["coins"], True),
            ("project", ["projects"], True),
            ("bitcoin", ["btc"], True),
            (" ", ["[ ]+"], False),
        ]

        for dst, srcs, isWord in converts:
            if isWord:
                for src in srcs:
                    line = re.sub(f"^{src} ", f"{dst} ", line, flags=re.IGNORECASE)
                    line = re.sub(f" {src} ", f" {dst} ", line, flags=re.IGNORECASE)
                    line = re.sub(f" {src}$", f" {dst}", line, flags=re.IGNORECASE)
            else:
                for src in srcs:
                    line = re.sub(src, dst, line, flags=re.IGNORECASE)

        line = re.findall("\w{2,}", line)
        line = " ".join([x for x in line])

        return line

    def preproc(self, text):
        lines = [l for l in text.split("\n")]
        lines = " ".join(lines)

        return self.preproc_line(lines)
