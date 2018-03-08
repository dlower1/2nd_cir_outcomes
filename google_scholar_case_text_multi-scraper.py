import numpy as np
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver

# DO NOT FORGET TO CHANGE THE PATH!!!
file_2014 = './data/2014/2ndcir2014X1_clean.csv'
file_2015 = './data/2015/2ndcir2015X1_clean.csv'
file_2016 = './data/2016/2ndcir2016X1_clean.csv'
file_2017 = './data/2017/2ndcir2017X1_clean.csv'

def google_case_text_scraper(cite_file, sleep_time=35, dbug=0):
    """Takes in a csv and uses the google case id to scrape the urls with the
    case text. It then appends the raw_text to a DataFrame. Finally, it writes
    out a final csv after it has scraped as many texts as it can. """

    google = 'https://scholar.google.com/scholar_case?case='

    df = pd.read_csv(cite_file)

    case_driver = webdriver.Chrome('./chromedriver')
    case_driver.get(google[:-18]) # To test to see if We have been blocked
    sleep(sleep_time)

    raw_opinions = []
    total_cases = len(df)
    print 'Begin Scraping Cases...\n{} Cases to Scrape'.format(total_cases)

    c = 0 # Counter
    for url in df['google_case_id']:
        case_driver.get(google+str(url))
        if dbug > 0:
            print 'Scraping: {}'.format(df['case_name'][c])

        sleep(sleep_time)
        sub_soup = BeautifulSoup(case_driver.page_source, 'lxml')

        try:
            raw_text = sub_soup.find('div', {'id':'gs_opinion'}).get_text()
            raw_opinions.append(raw_text)
            if dbug > 1:
                print 'Good Scrape! {} is {} characters long.'.format(df['case_name'][c],len(raw_text))
        except:
            block = raw_input('NO TEXT! DID GOOGLE BLOCK?!? [yes/no] ')
            if block == 'no':
                case_driver.refresh()
                sleep(sleep_time)
                sub_soup = BeautifulSoup(case_driver.page_source, 'lxml')
                raw_text = sub_soup.find('div', {'id':'gs_opinion'}).get_text()
                raw_opinions.append(raw_text)
            elif block == 'yes':
                break
            else:
                print '{} Not a Valid Command.\nEnding Scraping Session...'.format(block)
                break
        c = c + 1 # Next Case

    case_driver.close()

    raw_len = len(raw_opinions)
    print 'Opinions Scraped: {}\n{} Cases were not scraped.'.format(raw_len,(total_cases-raw_len))

    df = df.iloc[:raw_len] # In case or if they are uneaven in length
    df['raw_text'] = raw_opinions

    print 'Sending Dataframe to .csv'
    # DO NOT FORGET TO CHANGE THE PATH!!!
    df.to_csv(cite_file[:22]+'_scraped{}.csv'.format(raw_len),encoding='utf-8',index=False)

    return 'Job Done'

google_case_text_scraper(file_2014, dbug=1)
google_case_text_scraper(file_2015, dbug=1)
google_case_text_scraper(file_2016, dbug=1)
google_case_text_scraper(file_2017, dbug=1)
