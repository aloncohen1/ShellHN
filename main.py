import fire
import pandas as pd

import logging
from get_hn_data import main as run_get_hn_articles
from calc_tech_rpobability import main as run_get_tech_prob, TECH_LIST
from pprint import pprint


def main():

    run_program = True
    prob_df = pd.DataFrame()
    while run_program:
        print('Hello, end welcome to ShellHN')
        user_input = input(
            """what would you like to do:
            to get Hacker News top 40 articles - press 1
            to calculate the probability of tech to appear in future Hacker News - press 2
            to analyze correlation (proximity to 8PM Vs. # of comments) - press 3
            to quit - press 4""")

        if user_input not in ['1', '2', '3', '4']:
            print(f'Oops {user_input} is not an option, please select option between 1-4')

        else:
            print(f'{user_input}!! great choice!')

        if user_input == '1':
            try:
                hn_df = run_get_hn_articles()
                print(hn_df.to_string())
            except Exception as e:
                print(f'Failed to get articles df, reason - {e}')

        if user_input == '2':

            data_path = input('please provide full path to your hacker_news_data.json file')

            tech = input('select technology:')
            pprint(list(zip(range(len(TECH_LIST)), TECH_LIST)))

            month = input("""select month: \n
            1 - use Jan 2021 to predict Feb 2021 \n
            2 - use Feb 2021 to predict March 2021 \n
            3 - use March 2021 to predict Apr 2021 \n
            4 - use Apr 2021 to predict May 2021 (note: partial month)""")

            if prob_df.empty:
                try:
                    prob_df = run_get_tech_prob(data_path)
                except Exception as e:
                    print(f'Failed to calculate probabilities df, reason - {e}')
            prob = prob_df.loc[int(month), TECH_LIST[int(tech)]]
            print(f'proba')

            print()

        if user_input == '3':
            print('Ok, bye bye!')
            run_program = False

        if user_input == '4':
            print('Ok, bye bye!')
            run_program = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    fire.Fire(main)
