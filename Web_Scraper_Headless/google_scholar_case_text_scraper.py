import numpy as np
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from pyvirtualdisplay import Display

#DO NOT FORGET TO CHANGE THE PATH!!!
file_name = './Data/2ndcir{}X1_clean.csv'.format(raw_input('Year to be Processed: '))

def case_text_scraper(cite_file, short_df=1, sleep_time=30, dbug=0):
    """Takes in a DataFrame either as an python object scrapes the urls and appends the raw_text
    to the DataFrame. """

    google = 'https://scholar.google.com/scholar_case?case='
    df = pd.read_csv(cite_file)
    display = Display(visible=0, size=(800, 600))
    display.start()
    #df = df.reindex(np.random.permutation(df.index)) # To throw the BOT dogs off...
    profile = webdriver.FirefoxProfile()
    profile.native_events_enabled = False
    case_driver = webdriver.Firefox(firefox_profile=profile, executable_path='./geckodriver')
    raw_opinions = []
    print 'Begin Scraping Cases'
    print '{} Cases to Scrape'.format(len(df))
    c = 0

    for url in df['google_case_id']:
        case_driver.get(google+str(url))
        if dbug > 0:
            print 'Scraping {} ...'.format(df['case_name'][c])
        sleep(sleep_time)
        sub_soup = BeautifulSoup(case_driver.page_source, 'lxml')
        try:
            raw_text = sub_soup.find('div', {'id':'gs_opinion'}).get_text()
            raw_opinions.append(raw_text)
            if dbug > 1:
                print 'Good Scrape...{} is {} characters long.'.format(df['case_name'][c], len(raw_text))
        except:
            if short_df == 1:
                print 'No more text?!? Building short DataFrame...'
                break
            print "{} HAS NO TEXT!?! DID GOOGLE BLOCK!??".format(df['cae_name'][c])
            raw_opinions.append('THIS CELL IS BLANK?')
        c = c + 1

    case_driver.close()
    display.stop()
    print 'Opinions Scraped:', len(raw_opinions)
    if short_df == 1:
        print  '{} Cases were not scraped.'.format(len(df)-len(raw_opinions))
        df = df.iloc[:len(raw_opinions)]
    df['raw_text'] = raw_opinions
    copy = '_final'
    if short_df == 1:
        copy = '_short'
    print 'Writing {} Dataframe to .csv'.format(copy)
    df.to_csv((cite_file+copy), encoding='utf-8', index=False)
    return 'Job Done'

case_text_scraper(file_name, short_df=1, sleep_time=30, dbug=1)
