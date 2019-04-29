"""Converts IMDb html ratings data to csv files.

All scraped files of one episode are assumed to be stored in the directory htmls/E<episode_no>/.
File names must be in the following format: E<episode_no>_2019-05-03_23-10-36.html
where the date_time in the name is assumed to be the time the data is taken.

IMDb ratings data is contained in 3 tables: histogram, demographic, region.
The 3 tables are converted to 3 separate csv files: histogram, demographics, region.
The tables explained:
    Histogram contains the rating histogram: how many votes were cast for each rating from 1-10.
    Demographic contains the rating and number of votes by demographic. It is divided by Age Group
        (All Ages, <18, 18-29, 30-44, 45+) and by gender (All, Males, Females).
        Note that the numbers for different age groups and genders do not have to add up to the total number of votes
        contain in All Ages and All) because the age group and gender is not known for all voters.
    Region contains the rating and number of votes by different regions (Top 1000 Voters, US Users and Non-US Users)
"""

from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from glob import glob

# give (path) and name for csv
histogram_csv = "histogram.csv"
demographic_csv = "demographic.csv"
region_csv = "region.csv"

# number of episodes to process
no_episodes = 6

# choose which table is converted: histogram, demographic, region, all
requested_table = "all"

# early exit for debugging
exit_after_n_files_processed = -1


def convert_ratings_histogram(table):
    rows = table.find_all('tr')
    # rating & vote_counts
    rating = list()
    vote_counts = list()
    for row in range(1, 11):
        rating_in_row = rows[row].find_all('div', {'class': 'rightAligned'})[0].contents[0]
        vote_count_in_row = rows[row].find_all('div', {'class': 'leftAligned'})[0].contents[0]
        rating.append(rating_in_row)
        vote_counts.append(vote_count_in_row)

    df_ratings_histogram = pd.DataFrame({"rating": rating, "vote_counts": vote_counts})
    df_ratings_histogram['rating'] = pd.to_numeric(df_ratings_histogram['rating'])
    df_ratings_histogram['vote_counts'] = df_ratings_histogram['vote_counts'].str.replace(',', '').astype(int)
    return df_ratings_histogram

def convert_demographic_table(table):
    rows = table.find_all('tr')
    # age_group (All Ages, <18, 18-29, 30-44, 45+)
    row1_age_group = rows[0].find_all('div')
    age_group = list()
    for content in row1_age_group:
        age_group.append(content.contents[0])
    # gender (All, Males, Females; without All change to range(2,4))
    gender = list()
    for i in range(1, 4):
        gender.append(rows[i].find_all('div', {'class': 'leftAligned'})[0].contents[0])
    # ratings
    ratings = list()
    for j in range(1, 4):
        ratings_per_row = list()
        for i in range(0, 5):
            rating = rows[j].find_all('div', {'class': 'bigcell'})[i].contents[0]
            ratings_per_row.append(rating)
        ratings.append(ratings_per_row)
    vote_counts = list()
    for row in range(1, 4):
        vote_counts_per_row = list()
        all_voting_rows = rows[row].find_all('td', {'align': 'center'})
        for column in range(0, 5):
            try:
                vote_count = all_voting_rows[column].a.contents[0].strip()
                vote_counts_per_row.append(vote_count)
            except AttributeError:
                vote_count = "0"
                vote_counts_per_row.append(vote_count)
        vote_counts.append(vote_counts_per_row)

    # reconstruct lists for use in dataframe
    age_group_for_df = age_group * 3
    gender_for_df = [item[:1] for item in gender for i in range(5)]
    vote_counts_for_df = [item for sublist in vote_counts for item in sublist]
    ratings_for_df = [item for sublist in ratings for item in sublist]
   
    # construct dataframe for table2_demographics
    df_demographics = pd.DataFrame({"gender": gender_for_df, "age_group": age_group_for_df, "rating": ratings_for_df,
                                    "vote_count": vote_counts_for_df})
    
    #convert data types
    df_demographics['rating'] = df_demographics['rating'].replace('-', np.NaN)
    df_demographics['rating'] = pd.to_numeric(df_demographics['rating'])
    df_demographics['vote_count'] = df_demographics['vote_count'].str.replace(',', '').astype(int)
    df_demographics['gender'] = df_demographics['gender'].astype('category')
    df_demographics['age_group'] = df_demographics['age_group'].astype('category')

    return df_demographics


def convert_region_table(table):
    rows = table.find_all('tr')
    # regions
    row1_regions = rows[0].find_all('div')
    regions = list()
    for content in row1_regions:
        regions.append(content.contents[0])
    # ratings
    row2_ratings = rows[1].find_all('div', {'class':'bigcell'})
    ratings = list()
    for content in row2_ratings:
        ratings.append(content.contents[0])
    # vote_counts
    row2_votes = rows[1].find_all('td')
    vote_counts = list()
    for column in row2_votes:
        try:
            vote_count = column.a.contents[0].strip()
            vote_counts.append(vote_count)
        except AttributeError:
            vote_count = "0"
            vote_counts.append(vote_count)
    # build dataframe
    df_ratings_region = pd.DataFrame({"region": regions, "rating": ratings, "vote_counts":vote_counts})
    df_ratings_region['rating'] = df_ratings_region['rating'].replace('-', np.NaN)
    df_ratings_region['rating'] = pd.to_numeric(df_ratings_region['rating'])
    df_ratings_region['vote_counts'] = df_ratings_region['vote_counts'].str.replace(',', '').astype(int)
    df_ratings_region['region'] = df_ratings_region['region'].astype('category')
    return df_ratings_region


def add_date_time_and_episode(table, func, time, episode_no):
    df = func(table)
    df["date_time"] = time
    df["episode"] = episode_no
    return df


def table_requested(table):
    if requested_table == "all":
        return True
    if table == requested_table:
        return True
    return False


# pattern for date_time
pattern = re.compile('\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}')

# initialize different counters
count_files_opened = 0
count_histogram_files = 0
count_demographic_files = 0
count_region_files = 0

for episode in range(1,no_episodes+1):
    list_df_histogram = list()
    list_df_demographic = list()
    list_df_region = list()

    file_names = glob("htmls/E%d/E%d_*.html" % (episode, episode))
    for file_name in file_names:
        if count_files_opened == exit_after_n_files_processed:
            break
        count_files_opened += 1
        with open(file_name) as fp:
            soup = BeautifulSoup(fp, features="html.parser")

            # skip file when ratings table is empty
            if not soup.table:
                print("skipped: " + file_name)
                continue
            # skip file when ratings table is empty
            if "cellpadding" not in soup.table.attrs:
                print("skipped: " + file_name)
                continue
            # find appropriate tables
            all_tables = soup.find_all('table')

            table1_ratings_histogram = None
            table2_ratings_demographic = None
            table3_ratings_region = None

            if table_requested("histogram"):
                table1_ratings_histogram = all_tables[0]

            if table_requested("demographic"):
                table2_ratings_demographic = all_tables[1]
            
            if table_requested("region"):
                table3_ratings_region = all_tables[2]
            
            # determine date-time
            result = pattern.search(file_name)
            date_time = result.group(0)

            # create all dataframes (histogram, demographic, region)
            if table1_ratings_histogram:
                df_histogram = add_date_time_and_episode(table1_ratings_histogram, convert_ratings_histogram, date_time, episode)
                list_df_histogram.append(df_histogram)
            
            if table2_ratings_demographic:
                df_demographic = add_date_time_and_episode(table2_ratings_demographic, convert_demographic_table, date_time, episode)
                list_df_demographic.append(df_demographic)

            if table3_ratings_region:
                df_region = add_date_time_and_episode(table3_ratings_region, convert_region_table, date_time, episode)
                list_df_region.append(df_region)

    #ignore empty list which can happen due to skipped files
    if not list_df_demographic:
        continue
    
    header = False
    mode = "ab"
    if episode == 1:
        header = True
        mode = "wb"

    if list_df_histogram:
        df_histogram_total = pd.concat(list_df_histogram, ignore_index=True)

        with open(histogram_csv, mode) as f:
            df_histogram_total.to_csv(f, index=False, header=header)
        count_histogram_files += len(list_df_histogram)

    if list_df_demographic:
        df_demographic_total = pd.concat(list_df_demographic, ignore_index=True)
    
        with open(demographic_csv, mode) as f:
            df_demographic_total.to_csv(f, index=False, header=header)
        count_demographic_files += len(list_df_demographic)

    if list_df_region:
        df_region_total = pd.concat(list_df_region, ignore_index=True)

        with open(region_csv, mode) as f:
            df_region_total.to_csv(f, index=False, header=header)
        count_region_files += len(list_df_region)

print("%d files were opened" % count_files_opened)
print("(histogram) %d files were converted into data and %d files were skipped" % (count_histogram_files, count_files_opened - count_histogram_files))
print("(demographic) %d files were converted into data and %d files were skipped" % (count_demographic_files, count_files_opened - count_demographic_files))
print("(region) %d files were converted into data and %d files were skipped " % (count_region_files, count_files_opened - count_region_files))
