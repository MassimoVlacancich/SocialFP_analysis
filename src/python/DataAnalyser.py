import collections
from _datetime import datetime
from argparse import ArgumentParser
from src.python.MongoUtils.MongoServices import MongoServices
from src.python.TimeSeries.Correlator import Correlator

#######################
#### PARSE ARGS #######
#######################
# parser = ArgumentParser()
# parser.add_argument("-ho",    "--host",          required=True, help="ip address to host")
# parser.add_argument("-u",     "--username",      required=True, help="username for host access")
# parser.add_argument("-pwd",   "--password",      required=True, help="password for host access")
# parser.add_argument("-pk",    "--pkey_path",     required=True, help="private key file path for host access")
# parser.add_argument("-pkpwd", "--pkey_password", required=True, help="private key passowrd")
# args = parser.parse_args()

#######################
#### SSH TO SERVER ####
#######################
# server = ShhUtils().getShhServerConnection(args.host, args.username, args.password, args.pkey_path, args.pkey_password, '127.0.0.1', 27017)
#
# # for attempt in range(5):
# #     try:
# #         server.start()
# #         server._check_is_started()
# #     except BaseSSHTunnelForwarderError as e:
# #         print('Error (trying again in five seconds)')
# #         time.sleep(5)
# #     else:
# #         break
# # else:
# #     print('Failed to setup a connection to the gateway')
# #     sys.exit(1)
# #
# # server.start()

######################################
##### INSTANTIATE MONGO AND TSP ######
######################################
mongo_services = MongoServices()
correlator = Correlator()
# db = mongo_services.getServerDb(server, "socialfp")
# local connection is a lot faster, keep this until needed to do otherwise
db = mongo_services.getDb("socialfp")
fromDate = datetime(2018, 11, 27)
toDate = datetime(2019, 1, 29)
tickers = ['AAPL','MSFT','AMZN','GOOGL','JNJ','JPM','XOM','TM','BA','DIS','MCD', 'DWDP', 'NFLX', 'NVDA', 'NEE', 'SBUX', 'AMT', 'TSLA', 'GM', 'AMD']

# Plot tweets volume VS stock volume
correlator.plotVoumeCorrelationTweetsStocks(db, tickers, fromDate, toDate)

# Find most frequent words by ticker

def excludedTwitterWords(word):
    if len(word) > 0:
        if word[0] == '$' or word[0] == '@':
            return True
    return False


# do a first test with one stock only
tweets = list(db.raw_tweets.find({"stockTicker": "TSLA", "date": {"$gte": fromDate, "$lt": toDate}}))
print("Retrieved tweets from db: " + str(len(tweets)))

tweets_text = []
for tweet in tweets:
    tweets_text.append(tweet['text'])

stopwords = set(line.strip() for line in open('C:/Users/Massimo/Documents/University/Masters/SocialFP_analysis/src/resources/stopwords.txt'))
stopwords = stopwords.union({'apple', 'rt', ' ', 'link', 'week', 'us', 'just', '2019', '2018', 'pennystocks', 'de', 'l', '3', '...', "2", "bmm"})
wordcount = {}
for line in tweets_text:
    for word in str(line).lower().split():
        word = word.replace(".", "")
        word = word.replace(",", "")
        word = word.replace(":", "")
        word = word.replace("\"", "")
        word = word.replace("!", "")
        word = word.replace("â€œ", "")
        word = word.replace("â€˜", "")
        word = word.replace("*", "")
        word = word.replace("#", "")

        if word not in stopwords and not excludedTwitterWords(word):
            if word not in wordcount.keys():
                wordcount[word] = 1
            else:
                wordcount[word] += 1

# Print most common word
n_print = 100
top3 = []
topN = []
word_counter = collections.Counter(wordcount)
for word, count in word_counter.most_common(n_print):
    print(word, ": ", count)
    topN.append(word)



financewords = ['buy', 'sell', 'high','low','bear','bearish','bull','bullish','good','bad','entry','enter','short','long','earnings','hold','holding','surprise','eps','dividend']

finance_tweets = []
finance_tweets_count = {}
for tweet in tweets_text:
    for finance_word in financewords:
        if finance_word in tweet:
            finance_tweets.append(tweet)
            if finance_word not in finance_tweets_count.keys():
                finance_tweets_count[finance_word] = 1
            else:
                finance_tweets_count[finance_word] += 1

print("done")
