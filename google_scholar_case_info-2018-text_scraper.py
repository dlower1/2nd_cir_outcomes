import numpy as np
import pandas as pd
from time import sleep
import re
from bs4 import BeautifulSoup
from selenium import webdriver

# DO NOT FORGET TO UPDATE THE YEAR!!!
short_url = '/scholar?start={}&q={}&hl=en&as_sdt=4,107,122&as_ylo=2018'
# DO NOT FORGET TO UPDATE THE PATH!!!
file_name = './data/2018/2ndcir2018X1.csv'
results = './data/2018/info_results.csv'

def google_scholar_case_logger(search_url, file_name, results_name, debug=0):
    """Web scrapes google scholar for cases, needs just the /scholar? question
    link. Makes a DataFrame of the case_name, case_id, judge and unpublished
    and writes that out to a csv."""

    # UPDATE JUDGE LIST ACCORDING TO YEAR!!!
    Search = ['court']

    google = 'https://scholar.google.com'
    driver = webdriver.Chrome('./chromedriver')

    y = []
    final_feature = []
    citation_list = []
    results_list = []

    for j in Search:
        c = 0 # Page Count
        print 'Searching for Cases with {} in the citation'.format(j)

        driver.get(google+search_url.format((c * 10),j))
        sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')

        try:
            result_list=soup.findAll('div',{'class':"gs_ab_mdw"})[1].get_text().split()
            if debug > 1:
                print result_list
        except:
            block = raw_input('No Page info! Did GOOGLE Block ?!? [yes/no] ')
            if block == 'no':
                driver.refresh()
                sleep(25)
                soup = BeautifulSoup(driver.page_source, 'lxml')
                result_list=soup.findAll('div',{'class':"gs_ab_mdw"})[1].get_text().split()
            else:
                print 'Ending Web Scraping...'
                break
        for x in result_list:
            try:
                result_count = int(x)
                print '{} Cases for Judge {}'.format(result_count, j)
                break
            except:
                pass

        n_pages = (result_count / 10) + (result_count % 10 > 0) #This is for rounding up the Pages
        results_list.append([j, result_count])

        for p in range(0, n_pages):
            print 'Page: {} of {}'.format(p + 1, n_pages)
            try:
                first_case = soup.find('div', {'class':'gs_a'}).get_text()
                if debug > 1:
                    print 'First Case on Page {}: {}'.format(p + 1, first_case)
            except:
                block=raw_input('No next Page! Did GOOGLE Block ?!? [yes/no] ')
                if block == 'no':
                    driver.refresh()
                    sleep(30)
                    soup = BeautifulSoup(driver.page_source, 'lxml')
                else:
                    print 'Pages NOT Scraped:',(n_pages - p)
                    break

            for cite in soup.findAll('div', {'class':'gs_a'}): #is the citation for the case
                try:
                    int(cite.get_text()[0]) #if the citation starts with a number, it is published
                    citation_list.append(cite.get_text())
                    y.append(1)
                except:
                    citation_list.append(cite.get_text())
                    y.append(0)

            for case in soup.findAll('h3', {'class':"gs_rt"}):
                title = case.get_text()
                if debug > 1:
                    print 'Scraping Case: '+title
                case_id = re.findall(r"\d{9}\d+", case.a['href'])[0]
                final_feature.append([title, case_id, j])

            if n_pages == p + 1:
                print 'Pages Done'
                break
            sleep(25)

            c = c + 1 # Done with this page
            # next_button = soup.find('td', {'align':'left'}).a['href'] # the next button on the search page, links to the next page
            driver.get(google+search_url.format((c * 10), j))
            sleep(5)
            soup = BeautifulSoup(driver.page_source, 'lxml')

        sleep(25)

    driver.close()

    print 'Making Result and Citation DataFrames...'
    if debug > 0:
        print 'Cases Scraped',len(final_feature)

    results_df = pd.DataFrame(results_list, columns=['Judge', 'raw_results'])
    df=pd.DataFrame(final_feature,columns=['case_name','google_case_id','judge'])
    df['published'] = y
    df['case_citation'] = citation_list

    print 'Writing Results DataFrame to .csv'
    results_df.to_csv(results_name, index=False)
    print 'Writing Citation DataFrame to .csv'
    df.to_csv(file_name, encoding='utf-8', index=False)
    return 'Job Done'

def google_case_text_scraper(cite_file, sleep_time=30, dbug=0):
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
    df.to_csv('./data/2018/2ndcir2018X1_scraped{}.csv'.format(raw_len),encoding='utf-8',index=False)

    return 'Job Done'

google_scholar_case_logger(short_url, file_name, results, debug=0)
google_case_text_scraper(file_name, sleep_time=35, dbug=1)
