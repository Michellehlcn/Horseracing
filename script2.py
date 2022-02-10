from datetime import datetime
import subprocess
import sys
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import math
import os
import pytz

import pandas as pd

file_name = ' '
saved_file = ' '


# setting input file parameters is in this part
def upload_and_process_file():
    global file_name
    label3.config(text="")
    file_name = filedialog.askopenfilename()
    name = file_name.split('/')
    label2.config(text=name[-1])
    print(file_name)


# All the processing happens in this part
def Process_file():
    # Reading the xlsx file for formatting and processing
    #global file_name
    sydney_tz = pytz.timezone('Australia/Sydney')
    DATE = datetime.now(sydney_tz)
    date = DATE.strftime("%d")
    month = DATE.strftime("%m")
    year = DATE.strftime("%Y")
    file_name = f"racenet_speedmap_scrape_{year}_{month}_{date}.xlsx"
    print(file_name)
    df_excel = pd.read_excel(file_name)

    # filter all the columns where tab_race=yes

    column_listchk = df_excel.columns  # make a list of the columns

    # Check the "tab_race?" column if exist or not
    if "tab_race?" in column_listchk:
        tab_check = True
    else:
        tab_check = False

    if tab_check:
        if df_excel['tab_race?'][0] == 'yes':
            df_excel = df_excel[df_excel["tab_race?"] == 'yes']
        else:
            df_excel = df_excel[df_excel["tab_race?"] == True]

    # Extracting the date for the date column
    dat = df_excel['settling_position_scrape_datetime'][1]
    dd = dat.split(' ')
    actual = dd[0]
    actual = dd[0].split('-')
    month_number = actual[1]

    # Using date object to get the month name
    datetime_object = datetime.strptime(month_number, "%m")
    month_name = datetime_object.strftime("%b")

    # Drop unnecessary columns

    if tab_check:
        df_excel.drop(
            ['tab_race?', 'race_complete?', 'region', 'track_state_text', 'url', 'horse_odds',
             'closing_speed_scrape_datetime',
             'settling_position_scrape_datetime'], axis=1, inplace=True)
    else:
        df_excel.drop(
            ['race_complete?', 'region', 'track_state_text', 'url', 'horse_odds',
             'closing_speed_scrape_datetime',
             'settling_position_scrape_datetime'], axis=1, inplace=True)

    # Used column names
    column_names = ['Unnamed: 0', 'track_condition_text', 'barrier', 'track_name_text', 'race_number_text',
                    'horse_number',
                    'horse_name', 'closing_speed', 'settling_position_rank', 'settling_position_text']

    # Reindexing the columns
    df = df_excel.reindex(columns=column_names)

    df = df.iloc[:, :]

    df1 = df.groupby(['track_name_text', 'race_number_text'], sort=False).count()

    df1.reset_index(inplace=True)

    # Get all the rows where the race count or the races are greater than 8
    df_filter = df1[df1["Unnamed: 0"] >= 8]

    df_col2 = df_filter.iloc[:, 0:3]

    df_col2.rename(columns={'Unnamed: 0': 'Count'}, inplace=True)

    new_df = pd.merge(df, df_col2, how='inner', left_on=['track_name_text', 'race_number_text'],
                      right_on=['track_name_text', 'race_number_text'])

    # sort the race values on the basis of Closing speed
    ordered = new_df.groupby(['track_name_text', 'race_number_text'], sort=False).apply(
        lambda x: x.sort_values(["closing_speed"], ascending=True)).reset_index(drop=True)

    # Get the last 2 rows from the races
    result1 = ordered.groupby(['track_name_text', 'race_number_text'], sort=False).tail(2)

    # getting last and second_last values
    last = result1.groupby(['track_name_text', 'race_number_text'], sort=False).tail(1)
    second_last = result1.groupby(['track_name_text', 'race_number_text'], sort=False).head(1)

    # Merging columns accordingly and to get the desired result
    complete = pd.merge(ordered, last[["Unnamed: 0", "horse_number", "closing_speed", "settling_position_rank"]],
                        how='left', left_on=['Unnamed: 0'],
                        right_on=['Unnamed: 0'])

    last_and_sec_last_merge = pd.merge(last, second_last[
        ["track_name_text", "race_number_text", "horse_number", "closing_speed", "settling_position_rank"]], how='left',
                                       left_on=['track_name_text', 'race_number_text'],
                                       right_on=['track_name_text', 'race_number_text'])

    complete_final = pd.merge(complete, last_and_sec_last_merge[
        ["Unnamed: 0", "horse_number_y", "closing_speed_y", "settling_position_rank_y"]], how='left',
                              left_on=['Unnamed: 0'],
                              right_on=['Unnamed: 0'])

    complete_final.rename(
        columns={'horse_number_y_x': 'no. of fastest Closing speed one', 'closing_speed_y_x': '… value of fastest',
                 'settling_position_rank_y_x': 'settling rank of 1st',
                 'horse_number_y_y': 'no. of 2nd fastest Closing speed one',
                 'closing_speed_y_y': '… value of 2nd fastest',
                 'settling_position_rank_y_y': 'settling rank of 2nd', 'horse_number_x': 'horse_number',
                 'closing_speed_x': 'closing_speed', 'settling_position_rank_x': 'settling_position_rank', },
        inplace=True)

    column_names = ['date', 'Unnamed: 0', 'track_condition_text', 'barrier', 'track_name_text', 'race_number_text',
                    'horse_number',
                    'horse_name', 'horse_number_0', 'closing_speed', 'settling_position_rank', 'settling_position_text']

    time_ = actual[2] + "-" + month_name
    complete_final['date'] = str(time_)

    complete_final['Closing quintile'] = pd.qcut(complete_final['closing_speed'], 5, labels=["1", "2", "3", "4", "5"])
    complete_final['Settling quintile'] = pd.qcut(complete_final['settling_position_rank'], 5,
                                                  labels=["1", "2", "3", "4", "5"])

    # Reindexing the columns
    complete_final = complete_final.reindex(
        columns=column_names + ['no. of fastest Closing speed one', '… value of fastest', 'settling rank of 1st',
                                'weighted col O -settling rank of 1st', 'no. of 2nd fastest Closing speed one',
                                '… value of 2nd fastest', 'settling rank of 2nd', 'diff Closing', 'diff settling rank',
                                'ratio', 'Closing quintile', 'Settling quintile', 'SP', '1,2,3', 'win pay',
                                'place pay'])

    # complete_final = complete_final.reindex(columns=column_names)
    x = datetime.now()

    # check to see if there are any races where 102.8 occurs > 3 times skip these races
    ordered_count_2 = complete_final.groupby(['track_name_text', 'race_number_text'], sort=False).apply(
        lambda x: (x.closing_speed == 102.8).sum()).reset_index(name='count')
    ordered_count_2 = ordered_count_2[ordered_count_2['count'] <= 3]
    complete_final = pd.merge(complete_final, ordered_count_2, how='inner',
                              left_on=['track_name_text', 'race_number_text'],
                              right_on=['track_name_text', 'race_number_text'])

    complete_final.drop(['count'], axis=1, inplace=True)
    


    # save the file as beryl_x_y_z where x corresponds to year and y correspons to month and z corresponds to date
    global saved_file
    saved_file = "beryl_" + actual[0] + "_" + actual[1] + "_" + actual[2] + ".xlsx"
    writer = pd.ExcelWriter(saved_file, engine='xlsxwriter')

    # delete rows where "Closing quintile" or "Settling quintile" are null
    complete_final = complete_final[complete_final['Closing quintile'].notna()]
    complete_final = complete_final[complete_final['Settling quintile'].notna()]

    # converting category data types to int
    complete_final['Closing quintile'] = complete_final['Closing quintile'].astype('int')
    complete_final['Settling quintile'] = complete_final['Settling quintile'].astype('int')

    # Saving sheet one in the xlsx file
    sheet_1 = complete_final
    sheet_1 = sheet_1.set_index('date')
    sheet_1.to_excel(writer, sheet_name='Sheet1')

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # wrapping the header
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'border': 1})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(sheet_1.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)

    # Sort values according to fastest
    complete_final = complete_final.sort_values('… value of fastest')
    complete_final = complete_final.dropna(subset=['… value of fastest'])

    # Function to calculate diff Closing
    def get_sublist(sta, end):
        return ((sta - end) / end) * 100

    # lamda function for assigning diff Closing values
    complete_final['diff Closing'] = complete_final.apply(
        lambda x: get_sublist(x['… value of fastest'], x['… value of 2nd fastest']), axis=1)

    # sort the dataframe in descending order on diff Closing column
    complete_final = complete_final.sort_values(['diff Closing'], ascending=False)

    # Get first 67% rows
    num_to_highlight = complete_final.shape[0] * 0.67
    num_to_highlight = int(num_to_highlight)

    # Calculate diff settling rank of the first 67% rows
    x = 0
    for index, rows in complete_final.iterrows():
        complete_final.at[index, 'diff settling rank'] = rows['settling rank of 1st'] - rows['settling rank of 2nd']
        x = x + 1
        if x >= num_to_highlight:
            break

    # resting indexes
    complete_final = complete_final.set_index('date')
    complete_final.to_excel(writer, sheet_name='Sheet2')

    # adding color to sheet2
    worksheet = writer.sheets['Sheet2']

    format1 = workbook.add_format({'bg_color': '#B2F9FC'})
    cell_format = workbook.add_format()
    cell_format.set_font_color('red')

    start_row = 1
    start_col = 19
    end_row = num_to_highlight
    end_cold = start_col

    worksheet.conditional_format(start_row, start_col, end_row, end_cold,
                                 {'type': 'cell',
                                  'criteria': '>=',
                                  'value': 0,
                                  'format': format1})

    # wrapping the header
    header_format = workbook.add_format({
        'bold': True,
        'text_wrap': True,
        'valign': 'top',
        'border': 1})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(complete_final.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)

    # Preparing the sheet3
    complete_final = complete_final.head(num_to_highlight)

    # Sorting the sheet3 on basis of Closing quintile and Settling quintile
    complete_final = complete_final.sort_values(['Closing quintile'], ascending=False)
    complete_final = complete_final.sort_values('Settling quintile')

    complete_final = complete_final.sort_values(['diff Closing'], ascending=False)
    sum = complete_final['diff Closing'].std() + complete_final['diff Closing'].mean()
    print("mean + sd: " + str(sum))
    sum = math.floor(sum)
    print("rounded off ->mean +sd: " + str(sum))
    
    #--Michelle Edit--
    # Modify Sheet:  Drop Column B(Unnamed:0), I(horse_number), J(closing_speed), M(no.of fastest closing speed one), P(weighted col O-settling rank of 1st) 
    complete_final.drop(['Unnamed: 0','horse_number_0','closing_speed','no. of fastest Closing speed one','weighted col O -settling rank of 1st'],axis=1,inplace=True)
    #Modify sheet: Rename column "ratio" to "Distance"
    complete_final.rename(columns={'ratio':'Distance'},inplace=True)

    complete_final.to_excel(writer, sheet_name='Sheet3')

    # adding color to sheet3
    worksheet = writer.sheets['Sheet3']
    
    #--Michelle Edit--
    start_col = 14
    end_cold = start_col


    worksheet.conditional_format(start_row, start_col, end_row, end_cold,
                                 {'type': 'cell',
                                  'criteria': '>=',
                                  'value': 0,
                                  'format': format1})

    # Conditional formatting for the cell having value greater than 'sd plus mean'
    worksheet.conditional_format(start_row, start_col, end_row, end_cold,
                                 {'type': 'cell',
                                  'criteria': '>',
                                  'value': sum,
                                  'format': cell_format})

    # Write the column headers with the defined format.And also wrapping the header
    for col_num, value in enumerate(complete_final.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)

    # save the prepared xlsx file
    writer.save()
    print('Done Processing')
    #label3.config(text="Done Processing")

def script2_run():
    Process_file()


#if __name__ == '__main__':

    #main()
