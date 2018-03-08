import numpy as np
import pandas as pd
from time import sleep
import re
from bs4 import BeautifulSoup
from selenium import webdriver

# DO NOT FORGET TO UPDATE THE YEAR!!!
short_url = '/scholar?start={}&q={}&hl=en&as_sdt=4,107,122&as_ylo=2009&as_yhi=2009cd G'
# DO NOT FORGET TO UPDATE THE PATH!!!
file_name = '2ndcir2009X1.csv'

def google_scholar_case_logger(search_url, file_name='case_log.csv', debug=0):
    """Web scrapes google scholar for cases, needs just the /scholar? question
    link. Makes a DataFrame of the case_name, case_id, judge and unpublished
    and writes that out to a csv."""

    # UPDATE JUDGE LIST ACCORDING TO YEAR!!!
    Judges = ['Katzmann', 'Newman', 'Kearse', 'Winter', 'Walker', 'Leval',\
    'Calabresi', 'Straub', 'Sack', 'Parker', 'Wesley', 'Lynch', 'Cabranes',\
    'Raggi', 'Chin', 'Lohier', 'Droney', 'Carney', 'Livingston', 'Hall',\
    'Pooler', 'Jacobs', 'Miner', 'McLaughlin']

    google = 'https://scholar.google.com'
    driver = webdriver.Chrome('./chromedriver')

    y = []
    final_feature = []
    citation_list = []
    results_list = []

    for j in Judges:
        c = 0 # Page Count
        print 'Searching for Cases with {} on the Panel'.format(j)

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
    results_df.to_csv('./scrape_results.csv', index=False)
    print 'Writing Citation DataFrame to .csv'
    df.to_csv(file_name, encoding='utf-8', index=False)
    return 'Job Done'

google_scholar_case_logger(short_url, file_name=file_name, debug=0)
