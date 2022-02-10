from bs4 import BeautifulSoup
from datetime import datetime
import json
import pandas as pd
import pytz
import re
import requests


import pywhatkit
import smtplib, ssl
from apscheduler.schedulers.blocking import BlockingScheduler

def punter():
	# Timing 
	sydney_tz = pytz.timezone('Australia/Sydney')
	DATE = datetime.now(sydney_tz)
	DATE = DATE.replace(tzinfo=None)
	print(DATE)

	# Scrape 
	url="https://www.punters.com.au/form-guide/"
	path ="https://www.punters.com.au"

	html_text = requests.get(url).text
	soup = BeautifulSoup(html_text, 'html.parser')

	url=[]
	timestamp=[]
	location=[]
	country=[]
	race_number=[]
	distance=[]
	#trainer_name =[]
	#jockey_name =[]
	horse_name=[]
	horse_number=[]
	odd=[]
	rows = soup.findAll('tr',{'class':'upcoming-race__row upcoming-race__row--country'})

	for row in rows:
		country_list = row.findChildren('td',{'class':'upcoming-race__country-title'})[0].text
		if country_list =='Australia':
			#print(country_list)
			row_country = row.find_next_siblings("tr", {"class": "upcoming-race__row"})
			#print(row_country)
			for row_ in row_country:
				try:
					m= row_.findChildren('td',{'class':'upcoming-race__country-title'})[0].text

					break
				except IndexError:			
					tables = row_.findAll('td', {'class': 'upcoming-race__event'})
					for table in tables:
						link =table.findAll('a', {'class': 'upcoming-race__event-link'})[0]
						link1= link['href']
						#print(link)
						url2= path + link1


						print("-------------")
						#print(link1)
						#print(time)
						#print(length)
						html_text2= requests.get(url2).text
						soup2 = BeautifulSoup(html_text2, 'html.parser')
						#print("-------------")
						#print(soup2)class="upcoming-race__td upcoming-race__meeting-name upcoming-races__show-pdfs"
						a=row_.findAll('td',{'class':'upcoming-race__td upcoming-race__meeting-name upcoming-races__show-pdfs'})[0].text
						a = re.split('; |, |\*|\n',a)[1].strip()
						b=soup2.findAll('div',{'class':'form-header__race-dist'})[0].text
						c =soup2.findAll('span',{'class':'form-header__distance'})[0].text

						for i in range(0,30):
							try:
								#d=soup2.findAll('a',{'class':'form-guide-overview__jockey-link'})[i].text
								#e=soup2.findAll('a',{'class':'form-guide-overview__trainer-link'})[i].text

								d=soup2.findAll('td',{'class':"form-guide-overview__competitor-number"})[i].text
								f=soup2.findAll('a',{'class':'form-guide-overview__horse-link'})[i].text
								g=soup2.findAll('span',{'class': 'ppodds'})[i].text
					
								location.append(a)
								race_number.append(b.split(' ')[1])
								distance.append(c[0:-1])
								country.append(country_list)
								
								#jockey_name.append(d)
								#trainer_name.append(e)
								horse_name.append(f)
								horse_number.append(d)
								odd.append(g)
								try:
									timestamp_list=soup2.find('abbr')['data-utime']
									time = datetime.fromtimestamp(int(timestamp_list))		
									#length = time - DATE
									#print(soup)
									timestamp.append(time)
								except TypeError:
									continue
								print(f'{time}|{a}|{country_list}|{b}|{c}|{d}|{f}|{g}')
								

								
							except IndexError:
								continue				
		else:
			continue

	file = list(zip(location,country,timestamp,race_number,distance,horse_number,horse_name,odd))
	df = pd.DataFrame(file,columns = ['Location','Country','Timestamp','Race_number','Distance','Horse_number','Horse_name','Odd'])
	#df.to_csv(r'sheet.csv', index=False, encoding ='utf-8' )
	df.to_excel(r'sheet.xlsx', sheet_name='Sheet1',index=False, encoding ='utf-8' )


	#Combine two spreadsheets
	open_file='beryl_'+str(DATE.year)+'_'+str(DATE.strftime("%m"))+'_'+str(DATE.strftime("%d"))+'.xlsx'
	df_excel = pd.read_excel(open_file,'Sheet3')

	df = pd.read_excel('sheet.xlsx')

	#rename columns, drop columns
	df.rename(
	columns={'Location': 'track_name_text', 'Race_number': 'race_number_text',
	         'Horse_name': 'horse_name','Horse_number':'horse_number'},
	inplace=True)

	df.drop(['Country'], axis=1, inplace=True)
	df_excel.drop(['Distance'], axis=1, inplace=True)
	df_excel['horse_number']=df_excel['horse_number'].astype(object)


	df['x']= df.track_name_text.astype(str)+df.race_number_text.astype(str)+df.horse_number.astype(str)
	df_excel['x']= df_excel.track_name_text.astype(str)+df_excel.race_number_text.astype(str)+df_excel.horse_number.astype(str)

	result = df_excel.merge(df,how='left',on=['x'])
	result.drop(['x','track_name_text_y','race_number_text_y','horse_number_y'],axis=1,inplace=True)
	result.to_excel(r'sheet2.xlsx', index=False, encoding ='utf-8' )

	#Today Potential List
	sum =df_excel['diff Closing'].std() + df_excel['diff Closing'].mean()
	timing = []
	msg = []
	print(sum)
	for t in range(0,len(result['diff Closing'])):

		track_name = result['track_name_text_x'][t]
		race_number = result['race_number_text_x'][t]
		horse_name = result['horse_name_x'][t]
		distance = result['Distance'][t]
		timestamp = result['Timestamp'][t]
		odd = result['Odd'][t]
		diff_closing = result['diff Closing'][t]
		closing_quintile = result['Closing quintile'][t]

		if (result['diff Closing'][t]>sum) and distance<=1600 and closing_quintile==5:

			#print(f'Track name: {track_name}| Horse name: {horse_name}|Distance: {distance}| Starting time: {timestamp}| Latest Odd: {odd}| diff_closing: {diff_closing}| Closing quintile: {closing_quintile}')
			

			msg_list=f"""\n
			
			    SELECTION
			----------------------------------------
			Track name: {track_name}|
			Race number: {race_number}|
			Horse name: {horse_name}|Distance: {distance}|
			Starting time: {timestamp}|
			Latest Odd: {odd}|
			diff_closing: {diff_closing}|
			Closing quintile: {closing_quintile}
			--------------------------------------\n"""
			msg.append(msg_list)
			timing.append(timestamp)

		else:
			msg_list = f"""\n
			NO POTENTIAL LIST TODAY
			\n"""
			msg.append(msg_list)

			break
		





