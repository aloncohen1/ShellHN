import fire
import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
from datetime import timedelta
import datetime

import logging


class FileNotExists(Exception):
    pass


def turn_to_20pm(timestamp: datetime.datetime, hour: int = 20) -> datetime.datetime:
    """
    functions that replace datetime
    :param timestamp: datetime object
    :param hour: hour to replace instead of the original hour
    :return:
    """
    return datetime.datetime.combine(timestamp.date(), datetime.time(hour, 00))


def time_to_nearest_20pm(timestamp: datetime.datetime) -> float:
    """
    function that calculates time to 20pm
    :param timestamp: datetime object
    :return:
    """

    hours = [turn_to_20pm(timestamp), (turn_to_20pm(timestamp + timedelta(days=-1)))]

    return min([abs(timestamp - t) for t in hours]).total_seconds() / 60


def main(import_path: str) -> None:

    """
    This code will predict the probability of a technology to appear in HN
    :param import_path: path to assignment json file of past (hacker_news_data.json)
    :return:
    """

    if not os.path.exists(import_path):
        raise FileNotExists(f'it looks like the path you provided is not valid, path - {import_path}')

    export_path = '/'.join(import_path.split('/')[0:-1]) + '/time_correlation.png'  # export path for plot output

    logging.info('read data')
    df = pd.read_json(import_path)  # load data
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')

    df['timestamp_est'] = df['timestamp'] + pd.Timedelta(hours=+5)  # correct EST time
    df['hour_est'] = df['timestamp_est'].dt.hour  # extract hour

    logging.info('calculate proximity to 20pm...')
    df['hours_to_20pm'] = df.apply(lambda x: time_to_nearest_20pm(x['timestamp_est']), axis=1) # add hours to nearest 20pm col
    df['proximity_to_20pm'] = df['hours_to_20pm'] * -1.0  # multiple hours_to_20pm in -1 to convert time to "proximity"

    logging.info('aggregate and plot')
    corr_df = df.groupby('hour_est').agg({'descendants': 'sum', 'proximity_to_20pm': 'mean'})
    corr_df['20pm_proximity_normed'] = MinMaxScaler().fit_transform((corr_df['proximity_to_20pm']).values.reshape(-1, 1))  # rescale to 0 ->1
    corr_df['descendants_normed'] = MinMaxScaler().fit_transform(corr_df['descendants'].values.reshape(-1, 1))  # rescale to 0 ->1

    # plot
    corr_value = round(corr_df.corr().loc['20pm_proximity_normed', 'descendants_normed'], 3)
    plot_title = f'Proximity to 20pm Vs. # descendants (Normalized)\nCorrelation: {corr_value}'
    corr_df[['20pm_proximity_normed', 'descendants_normed']].plot(kind='line', style='-o', figsize=(16, 8),
                                                                  title=plot_title).get_figure().savefig(export_path)

    logging.info(f'all done! output can be found here - {export_path}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
