import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from fuzzywuzzy import fuzz, process
import os

API_KEY = os.getenv("API_KEY")
# fuzzy imported to be used for the differences in the teams names between the website and the API 

# First part of the code is used to scrape the website then get the data from API

# Function to fetch and parse HTML data from a URL with headers

def scrape_error_handle(url):

  # This header was used to be able to scrape the website transfer market because I could not scrape it without it and when I tried to download syllenium I couldnt use it
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    # Error handeling ( try - except) for incorrect URL to check if there's an error from the beginning of the code
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
      # To know there is a problem in the URL same as assignment 2
        print(f"Error fetching {url}: {e}")
        return None

# This function is used for scraping the data from the website transfermarket to get the expenditures of each team for the last 2 seasons
def team_expenditures(url):
    soup = scrape_error_handle(url) 
    # Extracting all rows <tr> within the tbody

    rows = soup.find_all('tr')

    # initating the dict for the teams where we will store the scraped data

    scraped_team_dict = {}

# removing the tags to end up with the teams and the expenditures only 
    for row in rows:
        team_column = row.find('td', class_='hauptlink no-border-links')
        expenditure_column = row.find('td', class_='rechts hauptlink redtext')

#  checking if both in the same column then data should be scraped together

        if team_column and expenditure_column:
          #removing the tags and assigning the values to the dictionary
            team_name = team_column.find('a').text.strip()
            expenditure_text = expenditure_column.text.strip()
            scraped_team_dict[team_name] = expenditure_text
# creating a data frame with the teams with the columns team and expenditure only after extraction 
# created a list first then transformed to df because it was giving me an error 
    df_league_teams = pd.DataFrame(list(scraped_team_dict.items()), columns=['Team', 'Expenditure'])

    # Needed to create a function inorder to change all the values for money to be in billions not millions 
    # for a better view of the scatter plot
    def unit_convertor(expenditure):
      # removed the currency sign to make it a float
        expenditure = expenditure.replace('€', '').strip()
        # checked foor this method in order to change only the billion values and multiply by 1000 to change to millions
        if expenditure.endswith('bn'):
            value = float(expenditure.replace('bn', '').replace(',', '.')) * 1000
            value_rounded = round(value, 2)
            return f'{value_rounded}m'
        return expenditure
# Returns the expenditures rounded to two decimal places

# using the unit convertor function on expenditures and checking that all results are in million
    df_league_teams['Expenditure'] = df_league_teams['Expenditure'].apply(unit_convertor)
    df_league_teams['EV'] = df_league_teams['Expenditure'].apply(lambda x: float(x.replace('m', '').replace(',', '.')) if 'm' in x else 0)

# sorting the values of expenditures asscending order of EV which was used for ranking the values then getting only the top 10 values
    df_top_10 = df_league_teams.sort_values(by='EV', ascending=False).head(10)
    return df_top_10.drop(columns=['EV'])

# league standings and stats are fetched using this function from the API
def league_standings(api_key, competition_code, season_year, matchday):
    headers = {'X-Auth-Token': api_key}
    # Url of the API is added here with competition code being dynamic on which league chosen by the user
    url = f"https://api.football-data.org/v4/competitions/{competition_code}/standings"
    # parameters include the season and the final matchday of the league
    params = {'season': season_year,
              'matchday': matchday}
    response = requests.get(url, headers=headers, params=params)
   # The success response number 200 as per the API
    if response.status_code == 200:
        standings_data = response.json()
        # using the API documentation to get the standings of the league and return the table with standings
        for table in standings_data['standings']:
            if table['type'] == 'TOTAL':  
                return table['table']
    # Error message if the response code is not 200            
    else:
        print(f"Error fetching standings for season {season_year}, matchday {matchday}: {response.status_code}")
    # the list created to hold the data
    return []

# the teams names are matech by this function to get the top 10 teams as the transfermarket list scraped 
# there were minor differenced between how the API and the website called the teams so fuzzy was used
# the process.extractOne was used after research on how to use the fuzzy package 72 was used as a good percentage where all the changes are reflected 
#without skewing the data
def name_matcher(api_team_name, team_list):
    match, score = process.extractOne(api_team_name, team_list, scorer=fuzz.token_sort_ratio)
    return match if score > 72 else None

# This function is created to give the user the options to choose which leagues he want to view the dataset for
def league_selector():
  # Each league number is put with the league name, URL of the website with the specified league and the last matchday of the league to collect the data
    league_options = {
        '1': ("PL", "Premier League", "https://www.transfermarkt.us/transfers/einnahmenausgaben/statistik/plus/0?ids=a&sa=&saison_id=2022&saison_id_bis=2023&land_id=189&nat=&kontinent_id=&pos=&altersklasse=&w_s=&leihe=&intern=0&plus=0", 38),
        '2': ("PD", "La Liga", "https://www.transfermarkt.us/transfers/einnahmenausgaben/statistik/plus/0?ids=a&sa=&saison_id=2022&saison_id_bis=2023&land_id=157&nat=&kontinent_id=&pos=&altersklasse=&w_s=&leihe=&intern=0&plus=0", 38),
        '3': ("BL1", "Bundesliga", "https://www.transfermarkt.us/transfers/einnahmenausgaben/statistik/plus/0?ids=a&sa=&saison_id=2022&saison_id_bis=2023&land_id=40&nat=&kontinent_id=&pos=&altersklasse=&w_s=&leihe=&intern=0&plus=0", 34),
    }
    # User input part, numerical to limit errors
    while True:
        print("Choose a league to view the dataset:")
        print("1. Premier League")
        print("2. La Liga")
        print("3. Bundesliga")
        print("4. Exit")

        league_choice = input("Enter the number of your choice: ")

# if condition to check the user input with the options available and returns a tuple if true
        if league_choice in league_options:
            return league_options[league_choice]  
        elif league_choice == '4':
            print("Exiting the program.")
            return None, None, None, None
        # error message if false
        else:
            print("Invalid choice. Please try again.")

# the main function of the program where all the data will be combined
def main():
    api_key = API_KEY 

    # league selector function is called and the data is stored in this order as we wrote it in the upper part
    competition_code, league_name, url_transfermarkt, matchday = league_selector()
# if the competition code not matched then error is encountered
    if not competition_code:
        print("Error encountered, No valid league selected. Exiting.")
        return

    # use the team expenditures function to get the data from the website scarped 
    transfermarkt_df = team_expenditures(url_transfermarkt)

    # league leaderboard dict craeted to hold all the stats and they are all started from 0 to accumelate at the end of the league
    league_leaderboard = {team: {'Expenditure': expenditure, 'Goals For': 0, 'Goals Against': 0, 'Wins': 0, 'Draws': 0, 'Losses': 0, 'Points': 0}
                  for team, expenditure in zip(transfermarkt_df['Team'], transfermarkt_df['Expenditure'])}

    # for loop to get the data for both seasons of 2022 and 2023 and use the league standings function to fetch the data
    for season_year in [2022, 2023]:
        league_leaderboard_seasons = league_standings(api_key, competition_code, season_year, matchday)
        
        # storing the team name of the teams fetched by the api to then be used when combining both data from website and API 
        # using fuzzymatch .tolist() gets the matched name
        for team_data in league_leaderboard_seasons:
            api_team_name = team_data['team']['name']
            matched_team = name_matcher(api_team_name, transfermarkt_df['Team'].tolist())
            
            # if conditions to start calculating the stats of each team and adding the number of goals, wins, points and all other stats
            if matched_team:
                league_leaderboard[matched_team]['Goals For'] += team_data['goalsFor']
                league_leaderboard[matched_team]['Goals Against'] += team_data['goalsAgainst']
                league_leaderboard[matched_team]['Wins'] += team_data['won']
                league_leaderboard[matched_team]['Draws'] += team_data['draw']
                league_leaderboard[matched_team]['Losses'] += team_data['lost']
                league_leaderboard[matched_team]['Points'] += team_data['points']

    # putting the data in league_leaderboard into a data frame using pandas
    #orient is used to make the dict keys (Teams) as the row labels after renaming the index
    league_leaderboard_df = pd.DataFrame.from_dict(league_leaderboard, orient='index').reset_index()
    league_leaderboard_df.rename(columns={'index': 'Team'}, inplace=True)

    # using the merge method from pandas to merge both dfs by the team as the common variabl
    final_merged_df = pd.merge(transfermarkt_df, league_leaderboard_df, on='Team', how='inner')
    # cleaning the data 
    final_merged_df = final_merged_df.drop(columns=['Expenditure_y'])
    final_merged_df = final_merged_df.rename(columns={'Expenditure_x': 'Expenditure'})

    # Adding the Millions per point to give an overview for the user
    final_merged_df['Million Euro per Point'] = final_merged_df['Expenditure'].apply(lambda x: float(x.replace('m', ''))) / final_merged_df['Points']

    # Save the data for CSV file 
    final_merged_df.to_csv('LeagueEXP.csv', index=False)

    # Plottin a scatter plot of the expediture and the points obtained by the league teams 
    # used matplotlib for this 
    plt.figure(figsize=(10, 6))
    x = final_merged_df['Expenditure'].apply(lambda x: float(x.replace('m', '')))
    y = final_merged_df['Points']
    plt.scatter(x, y, color='blue')

    # Tried to label the teams on the graph to show the user it was a bit covered by the points but couldnt change
    #using this for loop label each team on the graph
    for i, team_name in enumerate(final_merged_df['Team']):
        plt.text(x[i], y[i], team_name, fontsize=5, ha='right')
    # Save the plot as a PNG file
    plt.savefig(f'Expenditure_vs_Points_{league_name}.png', format='png', dpi=300)
    # Print the plot figure 
    plt.title(f'Expenditure vs Points in {league_name} (Previous 2 seasons 2022/23 and 2023/24)')
    plt.xlabel('Expenditure (Million Euros)')
    plt.ylabel('Points')
    plt.grid(True)
    plt.show()
    
    #print("Final Data with Cumulative Stats:")
    #print(final_merged_df)

    print("\nProgram finished. Please refresh to select another league.")

# Run the main function
if __name__ == "__main__":
    main()
# Used LLM to know how to solve the header problem which suggested in adding a user agent as put above also when dealing with the difference in names it introduced me to fuzzy package and its notation. 
# However, all code structure and functionalitties have been thought of and implemented by human activites
