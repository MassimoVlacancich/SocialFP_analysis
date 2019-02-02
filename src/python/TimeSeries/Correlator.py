from src.python.TimeSeries.TimeSeriesProcessor import TimeSeriesProcessor
from src.python.TimeSeries.PearsonCorrelator import PearsonCorrelator
from src.python.Plotting.Plotter import Plotter

class Correlator:

    def __init__(self):
        self.timeSeriesProcessor = TimeSeriesProcessor()
        self.personCorrelator = PearsonCorrelator()
        self.plotter = Plotter()
        self.lags = [-3, -2, -1, 0, 1, 2, 3]

    def plotVoumeCorrelationTweetsStocks(self, db, tickers, fromDate, toDate):
        correlations = {}
        for ticker in tickers:
            print("Computing correlation for " + ticker)
            # query all volume entries among 2 dates for a stock symbol
            mkt_time_series = self.timeSeriesProcessor.getMktDataTimeSeries(db.market_data, ticker, fromDate, toDate)
            # query tweets
            tweets_time_series = self.timeSeriesProcessor.getTweetsTimeSeries(db.raw_tweets, ticker, fromDate, toDate)
            tweets_time_series = self.timeSeriesProcessor.removeMissingPoints(mkt_time_series, tweets_time_series)
            # get time series axis list
            mkt_data_dates, mkt_data_volumes = self.timeSeriesProcessor.getDataTimeSeriesAxisLists(mkt_time_series, 'date','volume')
            tweets_dates, tweets_totals = self.timeSeriesProcessor.getDataTimeSeriesAxisLists(tweets_time_series, 'date','tweets')

            r_lagged = {}
            for lag in self.lags:
                r_lagged[lag] = self.personCorrelator.getRforLag(lag, mkt_data_volumes, tweets_totals)

            correlations[ticker] = r_lagged

        correlation_map = {}
        for corr in correlations.keys():
            for lag in self.lags:
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
            values_per_range = {0.0: [], 0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [],
                                0.9: []}
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

        percent_correlation_r = {0.0: [], 0.1: [], 0.2: [], 0.3: [], 0.4: [], 0.5: [], 0.6: [], 0.7: [], 0.8: [],
                                 0.9: []}
        for lag in percent_correlation_lag.keys():
            for idx, r in enumerate(percent_correlation_lag[lag]):
                r_key = list(percent_correlation_r.keys())[idx]
                temp = list(percent_correlation_r[r_key])
                temp.append(r)
                percent_correlation_r[r_key] = temp

        self.plotter.plotBarGraph(percent_correlation_r)