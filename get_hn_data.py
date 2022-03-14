import fire
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from bs2json import bs2json
import pandas as pd

import logging

HN_HOME_PATH = 'https://news.ycombinator.com/news'

HN_API_PATH_TOP_STORIES = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty&orderBy="$priority"&limitToFirst=%s'
HN_API_PATH_ITEM = 'https://hacker-news.firebaseio.com/v0/item/'


GRAVITY = 1.8


class ApiError(Exception):
  pass


class ScrapingError(Exception):
  pass


def get_records_metadata(article_metadata):

  """
  extract items from nested dict
  :param article_metadata:
  :return:
  """

  article_metadata = sorted(article_metadata, key=lambda k: k.keys(), reverse=True)  # sort dict list
  rank = article_metadata[0].get('span').get('text')
  title = article_metadata[2].get('a').get('text')
  article_link = article_metadata[2].get('a').get('attributes').get('href')
  return rank, title, article_link


def scrape_hn_news(p=1):

  """
  this function will scrape
  :param p: news site page
  :return:
  """

  logging.info(f'scrape_hn_news page: {p} - START')

  hn_homepage = requests.get(f"{HN_HOME_PATH}?p={p}")

  if hn_homepage.status_code != 200:
    raise ScrapingError(f"get request failed, reason - {hn_homepage.reason}")

  soup = BeautifulSoup(hn_homepage.content, "html.parser")  # parse HTML page

  converter = bs2json()  # initiate converter object
  hack_news = converter.convertAll(soup.find_all("tr", class_='athing'))

  hn_df = pd.DataFrame(i['tr'] for i in hack_news)
  ids_df = hn_df.apply(lambda x: x['attributes'].get('id'), axis=1)  # extract ids from dict

  hn_df = hn_df.apply(lambda x: pd.Series(x['td']), axis=1)

  hn_df[['rank', 'title', 'link']] = hn_df.apply(lambda x: pd.Series(get_records_metadata(x)), axis=1)
  hn_df['id'] = ids_df
  hn_df = hn_df[['rank', 'id', 'title', 'link']]

  logging.info(f'scrape_hn_news page: {p} - END')

  return hn_df


def calc_rank(article):

  """
  function that rank article based on comments, time since publication and gravity constant (1.8)
  Rank = (P-1) / (T+2)^G
  :param article: pd rows
  :return:
  """

  return (article['descendants'] - 1) / (article['time_since_sub'] + 2) ** GRAVITY


def hn_news_api(stories_limit=40):

  """

  note - can be speed-up using multi threading
  :param stories_limit:
  :return:
  """

  logging.info(f'hn_news_api - START')

  hn_request = requests.get(HN_API_PATH_TOP_STORIES % stories_limit, timeout=10)  # send request to hacker news AIP
  if hn_request.status_code != 200:
    raise ApiError(f"api request failed, reason - {hn_request.reason}")

  top_articles = eval(hn_request.text)  # convert content (str) to list

  logging.info(f'API query completed, received {len(top_articles)} articles!')

  now = datetime.now()  # calc current time

  articles_list = []

  for index, article_id in enumerate(top_articles):

    try:
      article_request = requests.get(f'{HN_API_PATH_ITEM}/{str(article_id)}.json')
      if article_request.status_code != 200:
        raise ApiError(f"api request failed, reason - {article_request.reason}")
      article_info = eval(article_request.content)  # convert content to list
      articles_list.append(article_info)

      if index % 10 == 0 and index != 0:
        logging.info(f'{index} articles processed')

    except Exception as e:
      logging.info(e)

  hn_df = pd.DataFrame(articles_list)
  hn_df['timestamp'] = pd.to_datetime(hn_df['time'], unit='s')  # convert to timestamp
  hn_df['time_since_sub'] = hn_df.apply(lambda x: (now - x['timestamp']).total_seconds() / 3600, axis=1)  # calc time since publish
  hn_df['rank'] = hn_df.apply(lambda x: calc_rank(x), axis=1)  # add rank column
  hn_df = hn_df.sort_values('rank', ascending=False)  # sort by rank

  hn_df = hn_df[['id', 'title', 'url', 'rank']]

  logging.info(f'hn_news_api - END')

  return hn_df


def main(method: str = "api") -> pd.DataFrame:

    """

    This code will return a data frame of top 40 articles published by Hacker News, ranked by their popularity
    ref - https://news.ycombinator.com/

    :param method: "api" / "scraping"
    :return: hn_df
    """

    method = method.lower()

    assert method in ['api', "scraping"], f"Oops, method must be 'api' OR 'scraping', received %s {method}"

    if method == 'scraping':
      df1 = scrape_hn_news(p=1)  # scrape page 1
      df2 = scrape_hn_news(p=2)  # scrape page 2
      hn_df = pd.concat([df1, df2])[0:40]  # filter to top 40

    else:
      hn_df = hn_news_api()

    return hn_df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
