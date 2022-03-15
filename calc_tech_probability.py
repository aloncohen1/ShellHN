import fire
import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer
from typing import Tuple

import logging

TECH_LIST = ["kubernetes", "linux", "windows", "solarwinds", "garmin", "aws", "docker", "github", "wordpress", "rundeck"]


class FileNotExists(Exception):
    pass


def get_terms_bow(tech_df: pd.DataFrame) -> pd.DataFrame:

    """
    this function will calculate bag of words and filter it to the TECH_LIST only
    :param tech_df: df filtered to titles contains tech string
    :return: bow_df
    """

    logging.info('get_terms_bow - START')

    # create bag of words
    vectorizer = CountVectorizer(binary=True)  # set binary=True to count term per article only once
    tech_vectorizer = vectorizer.fit_transform(tech_df['title'])
    bow_df = pd.DataFrame(tech_vectorizer.toarray(), columns=vectorizer.get_feature_names(), index=tech_df.index)

    # address situations with no appearances
    missing_terms = set(TECH_LIST) - set(bow_df.columns)  # find terms with 0 appearances in data
    if missing_terms:
        for term in missing_terms:
            bow_df[term] = 0  # add zero columns for terms with 0 appearances

    bow_df = bow_df[TECH_LIST]

    logging.info('get_terms_bow - END')

    return bow_df


def calc_terms_dfs(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    """
    This function will calculate term count, term share, total article count per month & tech
    :param df: original df with terms columns
    :return:
    """

    logging.info('calc_term_prob - START')

    articles_count_df = df.groupby('month')[TECH_LIST].count()  # total article count per month & tech
    terms_count_df = df.groupby('month')[TECH_LIST].sum()  # total term count per month & tech
    terms_share_df = terms_count_df / articles_count_df  # term share per month & tech
    prob_df = 1.0 - (1.0-terms_share_df).pow(articles_count_df)  # term prob per month & tech

    logging.info('calc_term_prob - END')

    return articles_count_df, terms_count_df, terms_share_df, prob_df


def main(import_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    """
    This code will predict the probability of a technology to appear in HN
    :param import_path: path to assignment json file of past (hacker_news_data.json)
    :return: articles_count_df, terms_count_df, terms_share_df, prob_df
    """

    if not os.path.exists(import_path):
        raise FileNotExists(f'it looks like the path you provided is not valid, path - {import_path}')

    logging.info('read data')
    df = pd.read_json(import_path)  # load data
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df['month'] = df['timestamp'].dt.month

    logging.info('search for substrings in titles')
    df['contains_tech'] = df.title.str.lower().str.contains('|'.join(TECH_LIST)).fillna(False)  # check if term in title

    tech_df = df[df['contains_tech']]  # filter to articles contains at least one term

    bow_df = get_terms_bow(tech_df)

    df = df.merge(bow_df, left_index=True, right_index=True, how='left')
    df[TECH_LIST] = df[TECH_LIST].fillna(0)

    articles_count_df, terms_count_df, terms_share_df, prob_df = calc_terms_dfs(df)

    return articles_count_df, terms_count_df, terms_share_df, prob_df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
