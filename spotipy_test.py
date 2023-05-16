# 1st: Install Spotipy in Anaconda
#      Write in Anaconda Prompt: conda install -c conda-forge spotipy or pip install spotipy
# 2nd: Get client ID 
#      Go to https://developer.spotify.com/dashboard -> Create App -> Fill name, Description,redirect URI (ie with http://localhost:3000)
#      Get Client ID & Client Secret in -> Settings -> Basic Information Page 

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
import numpy as np

# Read Scraped Data 
file_path = "C:\\Users\\mylon\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\common_charts.csv"
charts = pd.read_csv(file_path)

#charts = charts.iloc[0:20,]


# Pick dates to keep
#-------------------------------------
# Prompt user to input start and end dates
start_date = input("Enter start date (yyyy-mm-dd): ")
end_date = input("Enter end date (yyyy-mm-dd): ")

# Filter charts dataframe to keep only dates between start and end dates
charts = charts[(charts['Date'] >= start_date) & (charts['Date'] <= end_date)]
#-------------------------------------

# Pick Countries to keep
#-------------------------------------

# Select Countries by Name
# country_list_str = input("Enter a comma-separated list of countries to keep: ")
# country_list = [x.strip() for x in country_list_str.split(",")]

# # Filter charts dataframe to only keep selected countries
# charts = charts[charts['Country'].isin(country_list)]

# Select Counries by Number (In order of Appearance)

# Get unique country codes
# unique_countries = charts['Country'].unique()

# # Ask user to select a country
# selected_index = int(input(f"Enter the index of the country you want to keep (Pick number from 1 to {len(unique_countries)}): "))
# selected_country = unique_countries[selected_index - 1]

# # Filter result_df to keep only selected country
# charts = charts[charts['Country'] == selected_country]

#-------------------------------------

# Set up authentication
client_id = 'your-id'
client_secret = 'your-secret'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Define a variable to store the number of iterations between saves
save_interval = 1000

# Initialize empty lists to store track IDs and audio features
track_ids = []
audio_features = []
titles = []
artists = []


start_time = time.time()
# Loop over rows of the charts dataframe and extract track IDs
for index, row in charts.iterrows():
    track_title = row['Title']
    track_artist = row['Artist']
    time.sleep(10)
    print(index, track_title, track_artist)
    results = sp.search(q=f'track:{track_title} artist:{track_artist}', type='track')
    print("cool")
    if results['tracks']['items']:
        track_id = results['tracks']['items'][0]['id']
        track_ids.append(track_id)
        titles.append(track_title)
        artists.append(track_artist)
    else:
        track_ids.append(None)
        titles.append(track_title)
        artists.append(track_artist)
    print(f"Processed row {index} of {len(charts)}")
    
    # Save results to a CSV file every 1000 rows
    if index % 1000 == 0:
        data = {'Title': titles, 'Artist': artists, 'Track_ID': track_ids}
        df = pd.DataFrame(data)
        df.to_csv(f'C:\\Users\\mylon\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\track_ids{index}.csv', index=False)

# Save remaining results to a CSV file
data = {'Title': titles, 'Artist': artists, 'Track_ID': track_ids}
df = pd.DataFrame(data)
df.to_csv('C:\\Users\\mylon\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\track_ids.csv', index=False)



# Split track_ids into chunks of 100
chunks = [track_ids[x:x+100] for x in range(0, len(track_ids), 100)]

# Make separate requests for each chunk and concatenate the results
audio_features = []
i=0
i_size=len(chunks)
for chunk in chunks:
    i=i+1
    j=0
    for ch in chunk:
        j=j+1
        print(f'{i} in {i_size} and {j} in 100')
        if ch is not None:
            results = sp.audio_features(tracks=ch)
            for res in results:
                if res is not None:
                    audio_features.append(res)
                else:
                    audio_features.append({"danceability": np.nan, "energy": np.nan, "key": np.nan,
                                            "loudness": np.nan, "mode": np.nan, "speechiness": np.nan,
                                            "acousticness": np.nan, "instrumentalness": np.nan, "liveness": np.nan,
                                            "valence": np.nan, "tempo": np.nan, "type": np.nan, "id": np.nan,
                                            "uri": np.nan, "track_href": np.nan, "analysis_url": np.nan,
                                            "duration_ms": np.nan, "time_signature": np.nan})
        else:
            audio_features += [{"danceability": np.nan, "energy": np.nan, "key": np.nan,
                                "loudness": np.nan, "mode": np.nan, "speechiness": np.nan,
                                "acousticness": np.nan, "instrumentalness": np.nan, "liveness": np.nan,
                                "valence": np.nan, "tempo": np.nan, "type": np.nan, "id": np.nan,
                                "uri": np.nan, "track_href": np.nan, "analysis_url": np.nan,
                                "duration_ms": np.nan, "time_signature": np.nan}]



# Convert the list of dictionaries to a dataframe
audio_features_df = pd.DataFrame(audio_features)
audio_features_df = audio_features_df.drop(['type', 'id', 'uri', 'track_href', 'analysis_url'], axis=1)

# Add title and artist columns to the audio features dataframe
audio_features_df['Title_audio'] = titles
audio_features_df['Artist_audio'] = artists

# Merge the charts and audio features dataframes
result_df = pd.concat([charts.reset_index(drop=True), audio_features_df.reset_index(drop=True)], axis=1)

# Add a new column 'Match' to result_df
result_df['Match'] = (result_df['Title'] == result_df['Title_audio']) & (result_df['Artist'] == result_df['Artist_audio'])
(result_df['Match'] == False).any()

end_time = time.time()
print(f"Time taken: {end_time - start_time} seconds")

result_df.to_csv("C:\\Users\\mylon\\Dropbox\\MSc Lectures\\2nd Semester\\Behavioural\\Spotify\\Output\\audio_features.csv", index=False)
