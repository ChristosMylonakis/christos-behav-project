from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date, timedelta
import pycountry
import time
import os

chrome_options = Options()
path_chrome_driver = "C:/Users/Xristos/Dropbox/MSc Lectures/2nd Semester/Behavioural/Spotify/Code/chromedriver_win32/chromedriver.exe"
driver = webdriver.Chrome(path_chrome_driver)
sleep(2)

url_account_login = 'https://accounts.spotify.com/en/login?continue=https:%2F%2Fwww.spotifycharts.com%2Fregional%2Fgr%2Fdaily%2Flatest'
driver.get(url_account_login)


username_box = driver.find_element("xpath", '//*[(@id = "login-username")]')
username_box .send_keys('mylonakisc@gmail.com')

password_box = driver.find_element("xpath", '//*[(@id = "login-password")]')
password_box.send_keys('mylonakis4112000')

login_button = driver.find_element("xpath", '//*[contains(concat( " ", @class, " " ), concat( " ", "encore-bright-accent-set", " " ))]')
login_button.click()
sleep(2)

# Find all countries in Spotify Website
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
url = 'https://charts.spotify.com/charts/view/regional-us-daily/latest'
driver.get(url)
sleep(1)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
catalog_countries = soup.find_all('div', {'class': 'EntityOptionDisplay__TextContainer-sc-1c8so1t-2 EZpVl'})

catalog_countries_text = [country.text for country in catalog_countries]
catalog_countries_text = catalog_countries_text[1:]

country_names_map = {
    'Bolivia, Plurinational State of': 'Bolivia',
    'Czechia': 'Czech Republic',
    'Korea, Republic of': 'South Korea',
    'Taiwan, Province of China': 'Taiwan',
    'Venezuela, Bolivarian Republic of': 'Venezuela',
    'Viet Nam': 'Vietnam'
}

country_codes = {}
for country in pycountry.countries:
    name = country.name
    if name in country_names_map:
        name = country_names_map[name]
    country_codes[name] = country.alpha_2

countries = [country_codes.get(country, country) for country in catalog_countries_text]

# Replace incorrect country codes
wrong_country_codes = {'UAE': 'AE', 'USA': 'US'}
countries = [wrong_country_codes.get(c, c) for c in countries]

exclude_countries = pd.read_csv("C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Data\\countries_no_data_from_start.csv")
excluded_list = exclude_countries['Country'].tolist()

# create a new list of available countries excluding the excluded countries
countries = [country for country in countries if country not in excluded_list]

# Pick Countries to keep
#-------------------------------------

# Select Countries by Name
# country_list_str = input("Enter a comma-separated list of countries to keep: ")
# country_list = [x.strip() for x in country_list_str.split(",")]

# # Filter charts dataframe to only keep selected countries
# charts = charts[charts['Country'].isin(country_list)]


# Select Countries by Number (In order of Appearance)
# Ask user to select a country
# selected_index = int(input(f"Enter the index of the country you want to keep (Pick number from 1 to {len(countries)}): "))

# # Filter to keep only selected country
# countries = countries[selected_index]
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

# Create a list of all the dates to scrape
#----------------------------------------------------------------------------------------------------------------------------------------------------------------
# Daily
start_date = date(2022, 5, 11)
end_date = date.today() - timedelta(days=2)
dates_daily = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

# Weekly
start_date = date(2017, 1, 5)
end_date = date.today() - timedelta(days=8)
dates_weekly = [start_date + timedelta(weeks=x) for x in range((end_date - start_date).days // 7 + 1)]

################################# GET RID OF when deploying full code ###########################################################
# # Ask user to input 5 integers
# selected_indices = input("Enter 5 integers (0-{}) separated by space: ".format(len(dates_weekly)-1)).split()
# selected_indices = [int(idx) for idx in selected_indices]

# # Keep the selected dates from dates_weekly
# selected_dates = [dates_weekly[idx] for idx in selected_indices]
# print("Selected dates:", selected_dates)

# dates_weekly = selected_dates
################################# GET RID OF when deploying full code ###########################################################
#----------------------------------------------------------------------------------------------------------------------------------------------------------------

def scrape_daily_country(country, date, frequency):
    # navigate to website
    url = f'https://charts.spotify.com/charts/view/regional-{country.lower()}-{frequency}/{date}'
    driver.get(url)
    sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    tracks = soup.find_all('div', {'class': 'styled__StyledThumbnail-sc-135veyd-13 jaRpim'})
    streams = soup.find_all('td', {'class': 'TableCell__TableCellElement-sc-1nn7cfv-0 kJgiFu styled__RightTableCell-sc-135veyd-4 kGfYTK'})
    
    list_titles = []
    list_artists = []
    list_ranks = []
    list_streams = []
    
    for i in range(len(tracks)):
        #rank = tracks[i].find('span', {'class': 'Type__TypeElement-goli3j-0 hgLxdb'})
        title = tracks[i].find('span', {'class': 'styled__StyledTruncatedTitle-sc-135veyd-22 kKOJRc'})
        artist = tracks[i].find_all('a', {'class': 'styled__StyledHyperlink-sc-135veyd-25 bVVLJU'})
        
        list_ranks.append(i+1)
        list_titles.append(title.text)
        artist_names = [artist[j].text for j in range(len(artist))]
        list_artists.append(", ".join(artist_names))  
        
        streams_text = streams[i].text
        streams_numeric = int(''.join(filter(str.isdigit, streams_text)))
        list_streams.append(streams_numeric)
        
    df = pd.DataFrame({'Title': list_titles,
                       'Artist': list_artists,
                       'Rank': list_ranks,
                       'Streams': list_streams})
    df['Country'] = country.lower()
    df['Date'] = date
    
    return df



# Pick Frequency/Interval
#---------------------------
freq = input("Pick Frequency of Data - Daily or Weekly? (enter 0 for Daily or 1 for weekly):")
# freq = 1 # Daily -> 0
#          # Weekly -> 1
freq = int(freq)

if freq==0:
    dates = dates_daily
    frequency = 'daily'
    print("Daily Frequency of data chosen")
else:
    if freq==1:
        dates = dates_weekly
        frequency = 'weekly'
        print("Weekly Frequency of data chosen")
    else:
        print("Pick Intervals: Daily or Weekly?")    
#---------------------------
start_time = time.time()

countries_done=0
dfs = []  
countries_with_no_data = []
for country in countries[countries_done:]:
    sleep(10)
    dfs = []
    for date in dates:
        print(f"Scraping {country} - {date}")
        df = scrape_daily_country(country, date, frequency)
        if df.empty:
            # Create a new dataframe with desired columns and add to dfs
            df = pd.DataFrame(columns=['Title', 'Artist', 'Streams', 'Country', 'Date'])
            df['Country'] = country.lower()
            df['Date'] = date.strftime('%Y-%m-%d')
            dfs.append(df)
            countries_with_no_data.append(country)
            print(country.lower())
        else:
            dfs.append(df)
        
        df_country = pd.concat(dfs, ignore_index=True)
    df_country.to_csv(f"C:/Users/Xristos/Dropbox/MSc Lectures/2nd Semester/Behavioural/Spotify/Output/spotify_all_{country}_weekly.csv", index=True)
    countries_done = countries_done + 1


# Convert the list to a DataFrame
# countries_with_no_data = pd.DataFrame({'Country': countries_with_no_data})
# countries_with_no_data.to_csv("C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Data\\countries_no_data_from_start.csv", index=False)


#df_all = pd.concat(dfs, ignore_index=True)

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")

# close browser
driver.quit()



# Set the directory path
dir_path = "C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output"

dfs_countries = []
# Loop through all the files in the directory
for filename in os.listdir(dir_path):
    
    # Check if the file is a CSV file
    if filename.endswith('.csv'):
        
        # Read the CSV file into a pandas dataframe
        file_path = os.path.join(dir_path, filename)
        df = pd.read_csv(file_path)
        dfs_countries.append(df)

# Concatenate all the dataframes into a single dataframe
merged_df = pd.concat(dfs_countries, axis=0, ignore_index=True)

# Save the merged dataframe as a CSV file in the same file path
merged_file_path = os.path.join(dir_path, 'merged.csv')
merged_df.to_csv(merged_file_path, index=False)
