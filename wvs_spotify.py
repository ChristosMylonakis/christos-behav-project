# Import libraries
#-------------------------------------------------------------------------
import numpy as np
import pandas as pd
#import geopandas as gpd
import os
import plotly.express as px
import plotly.offline as pyo
import pycountry_convert as pc
import country_converter as coco

#-------------------------------------------------------------------------



# Specify YOUR path and load data
#-------------------------------------------------------------------------
# get working directory & make sure correct
os.getcwd()

# specify the path where the data we need lies in
########################## Change only this if file sharing ########################## 
directory = 'C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Data' # get path of data folder
########################## Change only this if file sharing ########################## 

# specify the exact files you need to load
path_wvs = os.path.join(directory, 'WVS_Cross-National_Wave_7_csv_v5_0.csv')

# read data wvs
wvs = pd.read_csv(path_wvs)
# read scraped data
file_path = "C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\merged.csv"
charts = pd.read_csv(file_path)
#-------------------------------------------------------------------------


def country_to_alpha2(country_name):
    try:
        # Try to convert the country name to a two-letter country code
        alpha2 = pc.country_name_to_country_alpha2(country_name)
        return alpha2.lower()
    except:
        # If the conversion fails, return None
        return None

# Create a new column with the two-letter abbreviations
wvs['B_COUNTRY_ALPHA_2'] = wvs['B_COUNTRY_ALPHA'].apply(country_to_alpha2)


# Get the set of unique two-letter country codes in each dataframe
wvs_countries = set(wvs['B_COUNTRY_ALPHA_2'].unique())
charts_countries = set(charts['Country'].unique())

# Get the set of countries that are common to both dataframes
common_countries = wvs_countries.intersection(charts_countries)
common_countries_df = pd.DataFrame(list(common_countries), columns=['Country'])

# Filter each dataframe to keep only the rows with country codes in the common set
wvs_common = wvs[wvs['B_COUNTRY_ALPHA_2'].isin(common_countries)]
charts_common = charts[charts['Country'].isin(common_countries)]

# Save the filtered dataframes as CSV files
wvs_common.to_csv('C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\common_wvs.csv', index=False)
charts_common.to_csv('C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\common_charts.csv', index=False)
common_countries_df.to_csv('C:\\Users\\Xristos\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\common_countries.csv', index=False)
