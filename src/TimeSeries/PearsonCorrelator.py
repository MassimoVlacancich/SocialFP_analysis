from math import pow
from math import sqrt
class PearsonCorrelator:

    def __init__(self):
        pass

    # time series must be same length
    def getRforLag(self, lag, time_series_a, time_series_b):

        if len(time_series_a) != len(time_series_b):
            raise ValueError('Time series must have the same length to compute Pearson R')

        a_mean = self._getSeriesSampleAverage(time_series_a)
        b_mean = self._getSeriesSampleAverage(time_series_b)

        numerator = 0
        for idx, a in enumerate(time_series_a):
            if idx + lag < len(time_series_b):
                numerator += (time_series_a[idx] - a_mean) * (time_series_b[idx + lag] - b_mean)

        den_left = 0
        for a in time_series_a:
            den_left += pow((a - a_mean),2)
        den_left = sqrt(den_left)

        den_right = 0
        for b in time_series_b:
            den_right += pow((b - b_mean),2)
        den_right = sqrt(den_right)

        denominator = den_left*den_right

        r_lag = numerator / denominator
        return r_lag

    def _getSeriesSampleAverage(self, time_series):
        return sum(time_series)/len(time_series)