from bs4 import BeautifulSoup
from datetime import datetime
import json
import pandas as pd
import pytz
import re
import requests
from punter_speedmap import punter
from script2 import Process_file
from script1 import script1_run

from threading import Timer
import pywhatkit
import smtplib, ssl
from apscheduler.schedulers.blocking import BlockingScheduler

timing = []
msg = []
def process():
	# Timing 
	sydney_tz = pytz.timezone('Australia/Sydney')
	DATE = datetime.now(sydney_tz)
	DATE = DATE.replace(tzinfo=None)
	print(DATE)
	#datetime_object = datetime.strptime(DATE, "%m")
	#month_name = datetime_object.strftime("%b")

	#print(DATE.year)
	#print(DATE.strftime("%m"))
	#print(DATE.strftime("%d"))


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
	
	print(sum)
	print(result)
	for t in range(0,len(result['diff Closing'])):
		
		track_name = result['track_name_text_x'][t]
		race_number = result['race_number_text_x'][t]
		horse_name = result['horse_name_x'][t]
		distance = result['Distance'][t]
		timestamp = result['Timestamp'][t]
		odd = result['Odd'][t]
		diff_closing = result['diff Closing'][t]
		closing_quintile = result['Closing quintile'][t]
		print(horse_name)

		if (result['diff Closing'][t]>=18) and distance<=1600 and closing_quintile==5:

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
			'''msg_list = f"""\n
			NO POTENTIAL LIST TODAY
			\n"""
			msg.append(msg_list)'''

			continue
		
	return timing,msg

def confirmed():
	# Timing 
	sydney_tz = pytz.timezone('Australia/Sydney')
	DATE = datetime.now(sydney_tz)
	DATE = DATE.replace(tzinfo=None)
	print(DATE)
	#datetime_object = datetime.strptime(DATE, "%m")
	#month_name = datetime_object.strftime("%b")

	#print(DATE.year)
	#print(DATE.strftime("%m"))
	#print(DATE.strftime("%d"))


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
	
	print(sum)
	print(result)
	for t in range(0,len(result['diff Closing'])):
		
		track_name = result['track_name_text_x'][t]
		race_number = result['race_number_text_x'][t]
		horse_name = result['horse_name_x'][t]
		distance = result['Distance'][t]
		timestamp = result['Timestamp'][t]
		odd = result['Odd'][t]
		diff_closing = result['diff Closing'][t]
		closing_quintile = result['Closing quintile'][t]
		print(horse_name)

		if (result['diff Closing'][t]>=18) and distance<=1600 and closing_quintile==5 and float(odd.strip('$'))<=3.2:

			#print(f'Track name: {track_name}| Horse name: {horse_name}|Distance: {distance}| Starting time: {timestamp}| Latest Odd: {odd}| diff_closing: {diff_closing}| Closing quintile: {closing_quintile}')
			

			msg_list=f"""\n
			
			    CONFIRMED SELECTION
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
			'''msg_list = f"""\n
			NO POTENTIAL LIST TODAY
			\n"""
			msg.append(msg_list)'''

			continue
		
	return timing,msg
	
sydney_tz = pytz.timezone('Australia/Sydney')
D = datetime.now(sydney_tz)
D = D.replace(tzinfo=None)
hour = D.strftime("%H")
minute = D.strftime("%M")


def text():
	print(*msg, sep ="\n")

#SEND EMAIL ALERT 
def email_alert():
	msg_=' '.join([str(elem) for elem in msg])
	sender_email = "YOUR EMAIL"
	receiver_email = "YOUR EMAIL"

	port = 465 #for SSL
	password = "YOUR PASSWORD"

	#create a secure SSL context
	context =ssl.create_default_context()

	with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, msg_)


#SEND WHATSAPP ALERT
def whatsapp_alert():
	msg_=' '.join([str(elem) for elem in msg])
	sydney_tz = pytz.timezone('Australia/Sydney')
	D = datetime.now(sydney_tz)
	D = D.replace(tzinfo=None)
	hour = D.strftime("%H")
	minute = D.strftime("%M")
	
	pywhatkit.sendwhatmsg("MOBILE PHONE NUMBER",str(msg_),int(hour),int(minute)+1) #FOR SOMEONE


def main():
	#SEND ALERT AT 12PM
	print('------SCRIPT 1-----')
	script1_run()
	print('------SCRIP 2------')
	Process_file()
	print('------SCRIPT 3-----')
	punter()
	process()
	text()
	
	email_alert()
	whatsapp_alert()

	timing.sort()


	#SEND ALERT AT 20-30 MIN BEFORE THE RACE STARTS	
	for ti in range(0,len(timing)):
		sydney_tz = pytz.timezone('Australia/Sydney')
		D = datetime.now(sydney_tz)
		D = D.replace(tzinfo=None)
		print(D)
		delta_t=timing[ti]-D
		print(delta_t)
		secs=delta_t.seconds-1800 #30MIN
		print(secs)
		if delta_t.days==0: #--fix the code here--
			print(f'Time for waiting:{secs}')
			#time.sleep()
			t1 = Timer(secs, punter)
			t1.start()
			t2 = Timer(secs+600, confirmed)
			t2.start()
			t3 = Timer(secs+700, whatsapp_alert)
			t3.start()
		else:
			continue

if __name__ == "__main__":
	main()



