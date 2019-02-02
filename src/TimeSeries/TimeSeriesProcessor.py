from datetime import datetime

import pymongo
from pymongo.database import Database


class TimeSeriesProcessor:

    def __init__(self):
        pass

    def getMktDataTimeSeries(self, mongoDbCollection : Database, stockTicker, fromDate, toDate):
        mkt_data = mongoDbCollection.find(
            {"stockTicker": stockTicker, "date": {"$gte": fromDate, "$lt": toDate}},
            {"date": 1, "volume": 1})

        mkt_data = sorted(mkt_data, key=lambda k: k['date'])
        # date_volume_list = date_volume_list[:-1]
        date_volume_list = []
        for entry in mkt_data:
            point = {}
            point['date'] = entry['date']
            point['volume'] = entry['volume']
            date_volume_list.append(point)

        return date_volume_list


    def getTweetsTimeSeries(self, mongoDbCollection : Database, stockTicker, fromDate, toDate):
        raw_tweets = mongoDbCollection.aggregate([
            {"$match": {"stockTicker": stockTicker, "date": {"$gte": fromDate, "$lt": toDate}}},
            {"$group": { "_id": {"day": {"$dayOfMonth": "$date"}, "month": {"$month": "$date"}, "year": {"$year": "$date"}},
            "count": {"$sum": 1}}}])
        raw_tweets = list(raw_tweets)

        date_count_tweets = []
        # extract tweets to be in list of dictionaries of form date and tweets
        # TODO upgrade mongo DB to 3.6 to do a projection with $dateFromParts
        for tweet in raw_tweets:
            entry = {}
            entry['date'] = datetime(year=tweet["_id"]["year"], month=tweet["_id"]["month"], day=tweet["_id"]["day"])
            entry['tweets'] = tweet['count']
            date_count_tweets.append(entry)
        date_count_tweets = sorted(date_count_tweets, key=lambda k: k['date'])

        return date_count_tweets


    def fillMissingDataPointsWithPrevValues(self, time_series_a, time_series_b, keyword):
        mkt_dates = []
        for mkt_point in time_series_a:
            mkt_dates.append(mkt_point['date'])

        missing_mkt_dates = []
        for point in time_series_b:
            if point['date'] not in mkt_dates:
                missing_mkt_dates.append(point['date'])

        for missing_mkt_date in missing_mkt_dates:
            entry = {}
            entry['date'] = missing_mkt_date
            time_series_a.append(entry)
        time_series_a = sorted(time_series_a, key=lambda k: k['date'])

        # add average volume in between missing dates - could change approach to remove tweets if we miss mkt data instead
        for idx, point in enumerate(time_series_a):
            if keyword not in point.keys():
                if idx == 0 and time_series_a[idx + 1] is not None:
                    point[keyword] = time_series_a[idx + 1][keyword]
                else:
                    point[keyword] = time_series_a[idx - 1][keyword]

        return time_series_a

    def removeMissingPoints(self, mkt_series, tweets_series):
        mkt_dates = []
        for mkt_point in mkt_series:
            mkt_dates.append(mkt_point['date'])

        tweets_idx_to_remove = []
        for idx, point in enumerate(tweets_series):
            if point['date'] not in mkt_dates:
                tweets_idx_to_remove.append(idx)

        tweets_series = [i for j, i in enumerate(tweets_series) if j not in tweets_idx_to_remove]
        return tweets_series

    def getDataTimeSeriesAxisLists(self, time_series, x_axis_keyword, y_axis_keyword):
        x_axis = []
        y_axis = []
        for point in time_series:
            x_axis.append(point[x_axis_keyword])
            y_axis.append(point[y_axis_keyword])
        return x_axis, y_axis