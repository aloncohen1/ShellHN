import logging
from get_hn_data import main as run_get_hn_articles
from calc_tech_probability import main as run_get_tech_prob, TECH_LIST
from pprint import pprint

MONTH_DICT = {1: 'Jan 2021', 2: 'Feb 2021', 3: 'March 2021', 4: 'Apr 2021', 5: 'May 2021'}


def get_prob_calculation_string(articles_count_df, terms_count_df, terms_share_df, month, tech):

    """
    this function will predict the probability to appear in the following month for specific month & technology
    and print an explanation string
    :param articles_count_df: df with articles count per month and technology
    :param terms_count_df: df with terms count per month and technology
    :param terms_share_df: df with terms share our of total articles per month and technology
    :param month: month (str) 1,2,3,4
    :param tech: tech index (str) 1-9
    :return:
    """

    month = int(month)
    tech = int(tech)

    total_articles_in_month = articles_count_df.loc[month, TECH_LIST[tech]]
    total_term_appearances_in_month = terms_count_df.loc[month, TECH_LIST[tech]]
    term_appearances_share_in_month = terms_share_df.loc[month, TECH_LIST[tech]]

    final_prob = 1.0 - (1.0 - term_appearances_share_in_month) ** total_articles_in_month

    print(f"""The probability for a term to appear at least one time is:
    1 - (1-T)^Q 
    Where:
    T is the relative appearances share of the term out of all the articles
    Q is the count of total articles
         
    Total articles in {MONTH_DICT.get(month)} - {"{:,}".format(total_articles_in_month)}
    Total appearances of the term '{TECH_LIST[tech]}' in {MONTH_DICT.get(month)} - {total_term_appearances_in_month}
    
    Therefore probability for a term to appear at least one time at {MONTH_DICT[month+1]} is: 
    1.0 - (1.0 - {total_term_appearances_in_month} / {"{:,}".format(total_articles_in_month)}) ^ {"{:,}".format(total_articles_in_month)} = ~{final_prob}""")


def main():

    run_program = True
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

            pprint(list(zip(range(len(TECH_LIST)), TECH_LIST)))
            tech = input('select technology:')

            if int(tech) not in range(len(TECH_LIST)):
                print(f'Oops {tech} is not an option, please select option between 1-{len(TECH_LIST)}')
                pass

            month = input("""select month:
            1 - use Jan 2021 to predict Feb 2021
            2 - use Feb 2021 to predict March 2021
            3 - use March 2021 to predict Apr 2021
            4 - use Apr 2021 to predict May 2021 (note: partial month)""")

            if month not in ['1', '2', '3', '4']:
                print(f'Oops {month} is not an option, please select option between 1-4')
                pass

            try:
                articles_count_df, terms_count_df, terms_share_df, prob_df = run_get_tech_prob(data_path)
                get_prob_calculation_string(articles_count_df, terms_count_df, terms_share_df, month, tech)
            except Exception as e:
                    print(f'Failed to calculate probabilities df, reason - {e}')

        if user_input == '3':
            print('Ok, bye bye!')
            run_program = False

        if user_input == '4':
            print('Ok, bye bye!')
            run_program = False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
