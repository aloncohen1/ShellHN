import fire
import pandas as pd
import os
from sklearn.feature_extraction.text import CountVectorizer

import logging

TECH_LIST = ["kubernetes", "linux", "windows", "solarwinds", "garmin", "aws", "docker", "github", "wordpress", "rundeck"]


class FileNotExists(Exception):
  pass


def get_terms_bow(tech_df):

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


def calc_term_prob(df):

    """

    :param df:
    :return:
    """

    logging.info('calc_term_prob - START')

    article_count_df = df.groupby('month')[TECH_LIST].count()
    terms_count_df = df.groupby('month')[TECH_LIST].sum()
    terms_share_df = terms_count_df / article_count_df
    prob_df = 1.0 - (1.0-terms_share_df).pow(terms_count_df)

    logging.info('calc_term_prob - END')

    return prob_df


def main(import_path='/Users/aloncohen/Downloads/Home Assignment Data Scientist/hacker_news_data.json'):

    """
    This code will predict the probability of a technology to appear in HN
    :param import_path: path to assignment json file of past (hacker_news_data.json)
    :return:
    """

    if not os.path.exists(import_path):
        raise FileNotExists(f'it looks like the path you provided is not valid, path - {import_path}')

    df = pd.read_json(import_path)  # check if term in title
    df['timestamp'] = pd.to_datetime(df['time'], unit='s')
    df['month'] = df['timestamp'].dt.month

    df['contains_tech'] = df.title.str.lower().str.contains('|'.join(TECH_LIST)).fillna(False)  # check if term in title

    tech_df = df[df['contains_tech']]  # filter to articles contains at least one term

    bow_df = get_terms_bow(tech_df)

    df = df.merge(bow_df, left_index=True, right_index=True, how='left')
    df[TECH_LIST] = df[TECH_LIST].fillna(0)

    final_df = calc_term_prob(df)

    return final_df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)