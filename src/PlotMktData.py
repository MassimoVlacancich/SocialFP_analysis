import pprint
import sys
from argparse import ArgumentParser
from _datetime import datetime
import time
import numpy as np
from matplotlib.ticker import FuncFormatter
from sshtunnel import BaseSSHTunnelForwarderError
from matplotlib.font_manager import FontProperties
from src.ShhUtils.ShhUtils import ShhUtils
from src.MongoUtils.MongoServices import MongoServices
from src.TimeSeries.TimeSeriesProcessor import TimeSeriesProcessor
from src.TimeSeries.PearsonCorrelator import PearsonCorrelator
import matplotlib.pyplot as plt
import matplotlib

#######################
#### PARSE ARGS #######
#######################
parser = ArgumentParser()
parser.add_argument("-ho",    "--host",          required=True, help="ip address to host")
parser.add_argument("-u",     "--username",      required=True, help="username for host access")
parser.add_argument("-pwd",   "--password",      required=True, help="password for host access")
parser.add_argument("-pk",    "--pkey_path",     required=True, help="private key file path for host access")
parser.add_argument("-pkpwd", "--pkey_password", required=True, help="private key passowrd")
args = parser.parse_args()

#######################
#### SSH TO SERVER ####
#######################
# server = ShhUtils().getShhServerConnection(args.host, args.username, args.password, args.pkey_path, args.pkey_password, '127.0.0.1', 27017)

# for attempt in range(5):
#     try:
#         server.start()
#         server._check_is_started()
#     except BaseSSHTunnelForwarderError as e:
#         print('Error (trying again in five seconds)')
#         time.sleep(5)
#     else:
#         break
# else:
#     print('Failed to setup a connection to the gateway')
#     sys.exit(1)
#
# server.start()

######################################
##### INSTANCIATE MONGO AND TSP ######
######################################
mongo_services = MongoServices()
# db = mongo_services.getServerDb(server, "socialfp")
timeSeriesProcessor = TimeSeriesProcessor()
# local connection is a lot faster, keep this until needed to do otherwise
db = mongo_services.getDb("socialfp")

correlator = PearsonCorrelator()
lags = [-3, -2, -1, 0, 1, 2, 3]
pearson_corr = True
fromDate = datetime(2018, 11, 27)
toDate = datetime(2019, 1, 29)
tickers = ['AAPL','MSFT','AMZN','GOOGL','JNJ','JPM','XOM','TM','BA','DIS','MCD', 'DWDP', 'NFLX', 'NVDA', 'NEE', 'SBUX', 'AMT', 'TSLA', 'GM', 'AMD']

correlations = {}
for ticker in tickers:
    print("Computing correlation for " + ticker)
    # query all volume entries among 2 dates for a stock symbol
    mkt_time_series = timeSeriesProcessor.getMktDataTimeSeries(db.market_data, ticker, fromDate, toDate)
    # query tweets
    tweets_time_series = timeSeriesProcessor.getTweetsTimeSeries(db.raw_tweets, ticker, fromDate, toDate)

    # # adjust market time series
    # mkt_time_series = timeSeriesProcessor.fillMissingDataPointsWithPrevValues(mkt_time_series, tweets_time_series, 'volume')
    # # adjust tweets if for a date we have mkt but no tweets
    # tweets_time_series = timeSeriesProcessor.fillMissingDataPointsWithPrevValues(tweets_time_series, mkt_time_series, 'tweets')
    tweets_time_series = timeSeriesProcessor.removeMissingPoints(mkt_time_series, tweets_time_series)

    # get time series axis list
    mkt_data_dates, mkt_data_volumes = timeSeriesProcessor.getDataTimeSeriesAxisLists(mkt_time_series, 'date', 'volume')
    tweets_dates, tweets_totals = timeSeriesProcessor.getDataTimeSeriesAxisLists(tweets_time_series, 'date', 'tweets')

    r_lagged = {}
    for lag in lags:
        r_lagged[lag] = correlator.getRforLag(lag, mkt_data_volumes, tweets_totals)

    correlations[ticker] = r_lagged


correlation_map = {}
for corr in correlations.keys():
    for lag in lags:
        rl = correlations[corr][lag]
        # # normalize
        # if pearson_corr:
        #     rl = (rl-(-1))/2

        if lag in correlation_map.keys():
            tmp = list(correlation_map[lag])
            tmp.append(rl)
            correlation_map[lag] = tmp
        else:
            correlation_map[lag] = [rl]

percent_correlation_lag = {}
for lag in correlation_map.keys():
    values = correlation_map[lag]
    values_per_range = {0.0: [], 0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [], 0.9: []}
    for value in values:
        for idx, range in enumerate(values_per_range.keys()):
            tmp = list(values_per_range.get(range))
            if idx == 0:
                if value < range or range < value < list(values_per_range.keys())[idx + 1]:
                    tmp.append(value)
                    values_per_range[range] = tmp
            elif idx == len(values_per_range.keys()) - 1:
                if value > range:
                    tmp.append(value)
                    values_per_range[range] = tmp
            else:
                if range < value < list(values_per_range.keys())[idx + 1]:
                    tmp.append(value)
                    values_per_range[range] = tmp

    percent_per_range = []
    for v in values_per_range.keys():
        percent = 100 * len(values_per_range[v]) / len(values)
        if percent < 0.01:
            percent = 0.01
        percent_per_range.append(percent)

    percent_correlation_lag[lag] = percent_per_range

percent_correlation_r = {0.0: [], 0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [], 0.9: []}
for lag in percent_correlation_lag.keys():
    for idx, r in enumerate(percent_correlation_lag[lag]):
        r_key = list(percent_correlation_r.keys())[idx]
        temp = list(percent_correlation_r[r_key])
        temp.append(r)
        percent_correlation_r[r_key] = temp


#######################
######## PLOT #########
#######################
# plt.figure(1
# plt.subplot(211)
# plt.plot(matplotlib.dates.date2num(mkt_data_dates), mkt_data_volumes)
# plt.ylabel('volume')
# plt.xlabel('time')
#
# plt.subplot(212)
# plt.plot(matplotlib.dates.date2num(tweets_dates), tweets_totals)
# plt.ylabel('tweets')
# plt.xlabel('time')
# plt.show()

# change to be 0.0 to 0.9


ind = np.arange(7)
width = 0.7

test = tuple(percent_correlation_r[0.0])

p0 = plt.bar(ind, percent_correlation_r[0.0], width)
p1 = plt.bar(ind, percent_correlation_r[0.1], width, bottom=percent_correlation_r[0.0])
p2 = plt.bar(ind, percent_correlation_r[0.2], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] for i in ind])
p3 = plt.bar(ind, percent_correlation_r[0.3], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] for i in ind])
p4 = plt.bar(ind, percent_correlation_r[0.4], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] for i in ind])
p5 = plt.bar(ind, percent_correlation_r[0.5], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] for i in ind])
p6 = plt.bar(ind, percent_correlation_r[0.6], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] for i in ind])
p7 = plt.bar(ind, percent_correlation_r[0.7], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] + percent_correlation_r[0.6][i] for i in ind])
p8 = plt.bar(ind, percent_correlation_r[0.8], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] + percent_correlation_r[0.6][i] + percent_correlation_r[0.7][i] for i in ind])
p9 = plt.bar(ind, percent_correlation_r[0.9], width, bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] + percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] + percent_correlation_r[0.6][i] + percent_correlation_r[0.7][i] + percent_correlation_r[0.8][i] for i in ind])

plt.ylabel('Stocks %')
plt.title('Correlation of stocks volume to tweets volume with lags')
plt.xticks(ind, ('-3', '-2', '-1', '0', '1', '2', '3'))
plt.yticks(np.arange(0, 101, 10))
plt.legend((p9[0], p8[0], p7[0], p6[0], p5[0], p4[0], p3[0], p2[0], p1[0], p0[0]), ('0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.2', '0.1', '0.0'),loc='center left', bbox_to_anchor=(1, 0.5))


plt.show()


# fig, ax = plt.subplots()
# rects0 = ax.bar(ind + width, percent_correlation_r[0.0], width)
# rects1 = ax.bar(ind + width, percent_correlation_r[0.1], width)
# rects2 = ax.bar(ind + width, percent_correlation_r[0.2], width)
# rects3 = ax.bar(ind + width, percent_correlation_r[0.3], width)
# rects4 = ax.bar(ind + width, percent_correlation_r[0.4], width)
# rects5 = ax.bar(ind + width, percent_correlation_r[0.5], width)
# rects6 = ax.bar(ind + width, percent_correlation_r[0.6], width)
# rects7 = ax.bar(ind + width, percent_correlation_r[0.7], width)
# rects8 = ax.bar(ind + width, percent_correlation_r[0.8], width)
# rects9 = ax.bar(ind + width, percent_correlation_r[0.9], width)
#
# ax.set_ylabel('Stocks %')
# ax.set_title('Correlation of stocks volume to tweets volume with lags')
# ax.set_xticks(ind + width /2)
# ax.set_xticklabels(('-3', '-2', '-1', '0', '1', '2', '3'))
# ax.set_yticks(np.arange(0, 101, 10))
# ax.legend((rects9[0], rects8[0], rects7[0], rects6[0], rects5[0], rects4[0], rects3[0], rects2[0], rects1[0], rects0[0]), ('0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.2', '0.1', '0.0'),loc='center left', bbox_to_anchor=(1, 0.5))
#
# plt.show()



print("done")