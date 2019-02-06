import json
import sys

# check in json file
from MongoUtils.MongoServices import MongoServices

# make sure json file is in scope of git to go online

tickers = ['AAPL','MSFT','AMZN','GOOGL','JNJ','JPM','XOM','TM','BA','DIS','MCD', 'DWDP', 'NFLX', 'NVDA', 'NEE', 'SBUX', 'AMT', 'TSLA', 'GM', 'AMD']
batch_size = 250
mongo_services = MongoServices()
db = mongo_services.getDb("socialfp")
path_to_data = '../resources/to_be_labelled.json'
with open(path_to_data) as f:
    try:
        tweets_to_label = json.loads(f.read())
    except TypeError:
        tweets_to_label = []


# read from db if json is empty
if len(tweets_to_label) == 0:

    # get a random tweets for all stock symbols
    for ticker in tickers:
        pipeline = [{"$match": {"stockTicker": ticker}}, {"$sample": {"size": batch_size}}]
        cursor = list(db.raw_tweets.aggregate(pipeline))
        # tweets = []
        # for tweet in cursor:
        #     temp = {}
        #     temp["_id"] = tweet["_id"]
        #     temp["text"] = tweet["text"]
        #     temp["stockTicker"] = tweet["stockTicker"]
        #     tweets.append(temp)

        tweets_to_label.extend(cursor)

    # store in json file
    with open(path_to_data, "w") as outfile:
        json.dump(tweets_to_label, outfile)


# present to user
print("Tweets classification started, type 1 for positive, 2 for negative, for 3 neutral, 4 undefined, 6 to exit")
for tweet in tweets_to_label:
    print(str(tweet))
    valid = False
    polarity = -1
    undefined = False
    finish = False
    while not valid:
        choice = input("enter choice: ")
        if choice == '1':
            polarity = 1
            valid = True
        if choice == '2':
            polarity = -1
            valid = True
        if choice == '3':
            polarity = 0
            valid = True
        if choice == '4':
            undefined = True
            valid = True
        if choice == '6':
            finish = True
            valid = True

    if finish:
        # store in json file
        with open(path_to_data, "w") as outfile:
            json.dump(tweets_to_label, outfile)
        sys.exit()

    if undefined:
        # remove from current tweets without adding to db
        tweets_to_label.remove(tweet)
    else:
        classified_tweet = {"_id": tweet["_id"], "polarity": polarity}
        tweets_to_label.remove(tweet)
        db.classified_tweets.insert_one(classified_tweet)