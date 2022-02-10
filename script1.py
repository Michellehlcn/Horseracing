from bs4 import BeautifulSoup
from datetime import datetime
import json
import pandas as pd
import pytz
import re
import requests

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import NoSuchElementException, TimeoutException

def script1_run():
    sydney_tz = pytz.timezone('Australia/Sydney')
    DATE = datetime.now(sydney_tz)
    url = 'https://www.racenet.com.au'

    url_1 = url + '/form-guide/horse-racing'
    html_text_1 = requests.get(url_1).text
    soup_1 = BeautifulSoup(html_text_1, 'html.parser')
    big_table = soup_1.findAll('div', {'class': 'upcoming-race-table__container desktop-class'})[0]

    divs = big_table.findChildren("div", recursive=False)
    regions, append_next_iter = {}, False
    for div in divs:
        if append_next_iter:
            append_next_iter = False
            regions[region] = div
            continue
        h3 = div.findChildren("h3", recursive=False)
        if h3 and h3[0].text.strip() in ['Australia']:
            region = h3[0].text.strip()
            append_next_iter = True

    open_race_info_list = []
    for region, div in regions.items():
        grids = div.findAll('div', {'class': 'upcoming-race-table__grid'})
        for grid in grids: #1 grid is 1 track
            track_info, _, races = grid.children
            track_name, _, track_condition = track_info.children
            track_name = track_name.text.strip()
            track_name_split = track_name.split('\n')
            track_name_text, track_state_text = track_name_split[:2]
            tab_race_flag = True
            if len(track_name_split) > 2: #and track_name_split[2].strip() == 'Non-TAB':
                tab_race_flag = False
            track_state_text = track_state_text.strip().replace('(','').replace(')','')
            track_condition_text = track_condition.text.strip()

            if track_condition_text.startswith('Heavy'):
                continue
            print(f'{track_name_text} | {track_state_text} | {track_condition_text}')
            for a in races.findChildren('a', recursive=True): #1 iteration is 1 race
                race_number_text = a.findChildren('div', {'class': 'upcoming-race-table__event-number'})[0].text.strip()
                race_results_list = a.findChildren('div', {'class': 'resulted-selections__container'}, recursive=True)
                race_complete_flag = len(race_results_list) > 0
                
                # if race_complete_flag:
                    # pass
                    # continue

                url_2 = url + a['href']
                print(f'{race_number_text} | {url_2}')
                open_race_info_list.append({
                    'tab_race?': 'yes' if tab_race_flag else 'no',
                    'race_complete?': 'yes' if race_complete_flag else 'no',
                    'region': region,
                    'track_name_text': track_name_text,
                    'track_state_text': track_state_text,
                    'track_condition_text': track_condition_text,
                    'race_number_text': race_number_text.replace('R', ''),
                    'url': url_2,
                    'speedmap_data': {},
                })
            print()


    ERRORS = []
    options = Options()
    options.headless = True
    timeout = 10
    window_x, window_y = 1280, 720
    closing_speed_xpath = "//div[contains(@class, 'form-guide-speed-map-horse-item__run ')]"
    closing_regex = r"(\d+)\. (.*) \((.*)\)(\|.+?(\d*) Bet)?"
    settling_positions = ['backMarker', 'offMidfield', 'midfield', 'offPace', 'pace', 'leader']
    # open_race_info_list = open_race_info_list[:1] #REMOVE AFTER TESTING

    for index_1, race in enumerate(open_race_info_list):
        
        driver = webdriver.Firefox(executable_path="/Users/michelle/Downloads/Airtaskers/Horseracing/geckodriver")
        #driver = webdriver.Firefox(options=options)
        driver.set_window_size(window_x, window_y)
        driver.get(race['url'])
        print()
        print('test1', race['url'])
        try:
            speed_map_button = driver.find_element_by_xpath("//a[@class='form-guide-tab speedmap ']")
            speed_map_button.click()
        except TimeoutException:
            print("time out 1", race['url'])
            ERRORS.append(race['url'])
            driver.quit()
            continue
        except NoSuchElementException:
            print("missing element 1", race['url'])
            ERRORS.append(race['url'])
            driver.quit()
            continue


        url_3 = race['url'] + '/speedmap/closing-speed'
        closing_speed_button_xpath = f"//a[@href='{url_3.replace(url, '')}']"
        print('test2', url_3)
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, closing_speed_button_xpath)))
            closing_speed_button = driver.find_element_by_xpath(closing_speed_button_xpath)
            closing_speed_button.click()
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, closing_speed_xpath)))
        except TimeoutException:
            print("time out 2", url_3)
            ERRORS.append(url_3)
            driver.quit()
            continue
        except NoSuchElementException:
            print("missing element 2", url_3)
            ERRORS.append(url_3)
            driver.quit()
            continue

        DATE_closing_speed = datetime.now(sydney_tz)
        horses_details_1 = driver.find_elements_by_xpath(closing_speed_xpath)
        for horse_details_1 in horses_details_1:
            html_text_3 = horse_details_1.get_attribute('outerHTML')
            soup_3 = BeautifulSoup(html_text_3, 'html.parser')
            width = float(soup_3.find('div', {'class': 'form-guide-speed-map-horse-item__run'})['style'].replace('width: ', '').replace('px;', ''))
            barrier = int(soup_3.find('div', {'class': 'form-guide-speed-map-horse-item__run__no'}).text.strip() or '0')
            number_name_country_odds = soup_3.find('div', {'class': 'form-guide-speed-map-horse-item__run__label'}).text.strip().replace('\n', '|')
            matches = re.finditer(closing_regex, number_name_country_odds, re.MULTILINE)
            for matchNum, match in enumerate(matches, start=1):
                horse_number, horse_name, horse_country, horse_odds = int(match.group(1)), match.group(2), match.group(3), match.group(5) or ''
            open_race_info_list[index_1]['speedmap_data'][horse_number] = {
                'horse_number': horse_number,
                'horse_name': horse_name,
                'horse_country': horse_country,
                'horse_odds': horse_odds,
                'barrier': barrier,
                'closing_speed': width,
                'closing_speed_scrape_datetime': str(DATE_closing_speed),
            }
        

        url_4 = race['url'] + '/speedmap/settling-position'
        settling_position_button_xpath = f"//a[@href='{url_4.replace(url, '')}']"
        print('test3', url_4)
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, settling_position_button_xpath)))
            settling_position_button = driver.find_element_by_xpath(settling_position_button_xpath)
            settling_position_button.click()
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='form-guide-speed-map--settling__slot']")))
        except TimeoutException:
            print("time out 3", url_4)
            ERRORS.append(url_4)
            driver.quit()
            continue
        except NoSuchElementException:
            print("missing element 3", url_4)
            ERRORS.append(url_4)
            driver.quit()
            continue

        DATE_settling_position = datetime.now(sydney_tz)
        dropzone = driver.find_element_by_xpath("//div[@class='form-guide-speed-map--settling__dropzone']")
        html_text_4 = dropzone.get_attribute('outerHTML')
        driver.quit()
        soup_4 = BeautifulSoup(html_text_4, 'html.parser')
        horses_details_2 = soup_4.findAll('div', {'class': 'form-guide-speed-map--settling__slot'})
        for index_2, horse_details_2 in enumerate(horses_details_2):
            if len(horse_details_2['class']) > 1:
                continue
            settling_position_rank = 12 - index_2%12
            settling_position_text = settling_positions[index_2%12//2]
            settling_position_text += '_front' if index_2%2 else '_back'
            horse_number = int(horse_details_2.find('span').text.strip())
            try:
                open_race_info_list[index_1]['speedmap_data'][horse_number]['settling_position_rank'] = settling_position_rank
                open_race_info_list[index_1]['speedmap_data'][horse_number]['settling_position_text'] = settling_position_text
                open_race_info_list[index_1]['speedmap_data'][horse_number]['settling_position_scrape_datetime'] = str(DATE_settling_position)
            except KeyError:
                pass
        


    print()
    print(f'ERRORS: {ERRORS}')
    # print(json.dumps(open_race_info_list, indent=4))
    # print()

    OUTPUT = []
    for race in open_race_info_list:
        race_base = {i:race[i] for i in race if i!='speedmap_data'}
        for horse in race['speedmap_data']:
            OUTPUT.append({
                **race_base,
                **race['speedmap_data'][horse],
            })
    # print(json.dumps(OUTPUT, indent=4))
    df = pd.DataFrame(OUTPUT)
    # print(df)

    date = DATE.strftime("%d")
    month = DATE.strftime("%m")
    year = DATE.strftime("%Y")

    df.to_excel(f"./racenet_speedmap_scrape_{year}_{month}_{date}.xlsx")
