import numpy as np
import matplotlib.pyplot as plt

class Plotter:

    def __init__(self):
        pass

    def plotBarGraph(self, percent_correlation_r):
        ind = np.arange(7)
        width = 0.7
        width = 0.7

        test = tuple(percent_correlation_r[0.0])

        p0 = plt.bar(ind, percent_correlation_r[0.0], width)
        p1 = plt.bar(ind, percent_correlation_r[0.1], width, bottom=percent_correlation_r[0.0])
        p2 = plt.bar(ind, percent_correlation_r[0.2], width,
                     bottom=[percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] for i in ind])
        p3 = plt.bar(ind, percent_correlation_r[0.3], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] for i in ind])
        p4 = plt.bar(ind, percent_correlation_r[0.4], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] for i in ind])
        p5 = plt.bar(ind, percent_correlation_r[0.5], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] for i in ind])
        p6 = plt.bar(ind, percent_correlation_r[0.6], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] for i in ind])
        p7 = plt.bar(ind, percent_correlation_r[0.7], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] +
            percent_correlation_r[0.6][i] for i in ind])
        p8 = plt.bar(ind, percent_correlation_r[0.8], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] +
            percent_correlation_r[0.6][i] + percent_correlation_r[0.7][i] for i in ind])
        p9 = plt.bar(ind, percent_correlation_r[0.9], width, bottom=[
            percent_correlation_r[0.0][i] + percent_correlation_r[0.1][i] + percent_correlation_r[0.2][i] +
            percent_correlation_r[0.3][i] + percent_correlation_r[0.4][i] + percent_correlation_r[0.5][i] +
            percent_correlation_r[0.6][i] + percent_correlation_r[0.7][i] + percent_correlation_r[0.8][i] for i in ind])

        plt.ylabel('Stocks %')
        plt.title('Correlation of stocks volume to tweets volume with lags')
        plt.xticks(ind, ('-3', '-2', '-1', '0', '1', '2', '3'))
        plt.yticks(np.arange(0, 101, 10))
        plt.legend((p9[0], p8[0], p7[0], p6[0], p5[0], p4[0], p3[0], p2[0], p1[0], p0[0]),
                   ('0.9', '0.8', '0.7', '0.6', '0.5', '0.4', '0.3', '0.2', '0.1', '0.0'), loc='center left',
                   bbox_to_anchor=(1, 0.5))

        plt.show()
