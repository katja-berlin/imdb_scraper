# IMDb scraper
Scrape ratings data for TV shows or movies from IMDb as html files and convert html files to csv data.

This scraper consits of two components: 
1.  `html_scraper_season8.sh`: Hourly download of the raw IMDb html page using wget and cron.
2.  `convert_html_to_csv.py`: Parsing and converting downloaded html files into aggregated csv files.

Some demo raw html files are included showing the ratings of the last season of Game of Thrones.

## Install
### using crontab to save html from IMDb with html_scraper_season8.sh

Cron is a system daemon used to execute desired tasks (in the background) at designated times.

1.  Install cgywin
      
    more information:
    * https://www.cygwin.com/
    * https://help.ubuntu.com/community/CronHowto
    * https://stackoverflow.com/questions/707184/how-do-you-run-a-crontab-in-cygwin-on-windows

2.  Edit crontab (using vim editor in cgywin):

    ```shell
    crontab -e
    ```
    Enter the following keys to
    * `i` 	- insert mode
    * `Esc` - exit insert mode
    * `:q!`	- quit without saving
    * `:wq`	- write(save) and quit

    write in insert mode e.g. to save html data every hour:
    ```
    0 * * * * /path_to_html_scraper/html_scraper_season8.sh
    ```

    short explanation for setting time when data is scheduled to be scraped:
    ```
    * * * * *
    Min(0-59) H(0-23) D(1-31) Month(1-12) weekday(0-6, 0-sunday)
    ```

3.  Install cron as a windows service, using cygrunsrv:

    ```shell
    cygrunsrv -I cron -p /usr/sbin/cron -a -n

    net start cron
    ```

4.  Customize html_scraper shell script
    * edit the directory where the html data from IMBd is saved (OUTPUT_DIR)
    * edit html to your favourite show (in demo code it is season 8 of Game of Thrones)
  
 ## using convert_html_to_csv.py
 
Converts raw IMDb html ratings data to csv files.

1.  File Format

    * All scraped files of one episode are assumed to be stored in the directory htmls/E<episode_no>/.
    * File names must be in the following format: E<episode_no>_2019-05-03_23-10-36.html
        * where the date_time in the name is assumed to be the time the data is taken.

2.  Choose tables to be converted
    
    * IMDb ratings data is contained in 3 tables: histogram, demographic, region.
    * The 3 tables are converted to 3 separate csv files: histogram, demographics, region.
    * choose which table is converted by editing `requested_table = "all"` (options: `"histogram"`, `"demographic"`, `"region"`, `"all"`)
    * The tables explained:
        * **_Histogram_** contains the rating histogram: how many votes were cast for each rating from 1-10.
        * **_Demographic_** contains the rating and number of votes by demographic. It is divided by Age Group
            (All Ages, <18, 18-29, 30-44, 45+) and by gender (All, Males, Females).
            Note that the numbers for different age groups and genders do not have to add up to the total number of votes
            contain in All Ages and All) because the age group and gender is not known for all voters.
        * **_Region_** contains the rating and number of votes by different regions (Top 1000 Voters, US Users and Non-US Users)

3. Choose path and name of output csv files

    * `histogram_csv = "histogram.csv"`
    * `demographic_csv = "demographic.csv"`
    * `region_csv = "region.csv"`

4.  Choose number of episodes

    * `no_episodes = 6`