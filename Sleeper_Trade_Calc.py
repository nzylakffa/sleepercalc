import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import fuzzywuzzy
import sys
import io
import logging
import concurrent.futures
import difflib
import requests
from fuzzywuzzy import process
from re import findall
from io import StringIO

###################
##### Sidebar #####
###################
# st.sidebar.image('ffa_red.png', use_column_width=True)
st.sidebar.markdown(" ## About This App:")
st.sidebar.markdown("This is a trade calculator for those of you playing in Sleeper leagues!")

st.sidebar.markdown("## Read This!")
st.sidebar.markdown("You will see errors until you fill out the 4 items on this page and then select your team and a trade partner on the Trade Calculator tab!")
st.sidebar.markdown("## 1) Click Fullscreen at the bottom for a better user experience")
st.sidebar.markdown("## 2) Input Sleeper Username")
st.sidebar.markdown("## 3) Input Season")
st.sidebar.markdown("This is the season you're looking at. Use 2023 for last season and 2024 once we draft our teams for 2024.")
st.sidebar.markdown("## 4) Select the league you want to use")
st.sidebar.markdown("This is a dropdown of all the league's you're in! If you don't know which is which then just pick one and check out the trade calculator tab to see which team of yours that is.")
st.sidebar.markdown("## 5) Input your league's scoring format")
st.sidebar.markdown("## 6) Go to the Trade Calculator tab and select your display name along with your trade partner's display name")
st.sidebar.markdown("## 7) You'll need to wait a few seconds for the tool to pull all the information")

tab_scrape, tab_trade = st.tabs(["Collect League", "Trade Calculator"])

with tab_scrape:    
    # Replace 'nzylak' with the actual username you want to query
    username_to_query = st.text_input("Input Username", value="")
    season = st.number_input("Input Season (use the year the draft happened in)", value = 2023)
    
    def get_user_info(username):
        api_url = f"https://api.sleeper.app/v1/user/{username}"
    
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Check for errors in the response
            user_info = response.json()
            return user_info
        except requests.exceptions.HTTPError as errh:
            st.write ("HTTP Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            st.write ("Error Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            st.write ("Timeout Error:",errt)
        except requests.exceptions.RequestException as err:
            st.write ("Something went wrong:",err)
    
    def get_user_leagues(user_id, sport, season):
        api_url = f"https://api.sleeper.app/v1/user/{user_id}/leagues/{sport}/{season}"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Check for errors in the response
            leagues_info = response.json()
            return leagues_info
        except requests.exceptions.HTTPError as errh:
            st.write("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            st.write("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            st.write("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            st.write("Something went wrong:", err)
            
    def get_league_rosters(league_id):
        api_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Check for errors in the response
            rosters_info = response.json()
            return rosters_info
        except requests.exceptions.HTTPError as errh:
            st.write("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            st.write("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            st.write("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            st.write("Something went wrong:", err)
            
    def get_league_users(league_id):
        api_url = f"https://api.sleeper.app/v1/league/{league_id}/users"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Check for errors in the response
            rosters_info = response.json()
            return rosters_info
        except requests.exceptions.HTTPError as errh:
            st.write("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            st.write("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            st.write("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            st.write("Something went wrong:", err)
            
    def get_league_draft(league_id):
        api_url = f"https://api.sleeper.app/v1/league/{league_id}/drafts"

        try:
            response = requests.get(api_url)
            response.raise_for_status()  # Check for errors in the response
            rosters_info = response.json()
            return rosters_info
        except requests.exceptions.HTTPError as errh:
            st.write("HTTP Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            st.write("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            st.write("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            st.write("Something went wrong:", err)
                        
    # Get user information
    user_info = get_user_info(username_to_query)
            
    # Extract user_id from the user information
    user_id = user_info['user_id']
    
    # Get user leagues
    user_leagues = get_user_leagues(user_id, "nfl", season)
    # st.write(user_leagues)
    
    # Get the roster settings for each of their leagues
    roster_pos_league_id = []
    roster_positions = []
    
    # Collect all league_id's
    league_ids = []
    for i in range(len(user_leagues)):
        league_ids.append(user_leagues[i]['league_id'])
        
    # Have the user select a league ID
    league_id = st.selectbox("Select the league you want to use",
                            league_ids)

    # Getting rosters
    if league_id is not None:        
        league_rosters = get_league_rosters(league_id)
        league_users = get_league_users(league_id)
        # st.write("League Users Information:")
        # st.write(league_users)

        # Print the league rosters information
        # st.write("League Rosters Information:")
        # st.write(league_rosters)
        
        # Get all the teams and ids into a list
        display_names = []
        user_ids = []
        for i in range(len(league_users)):
            display_names.append(league_users[i]['display_name'])
            user_ids.append(league_users[i]['user_id'])

            
        draft = get_league_draft(league_id)
        
        try:
            s_qbs = draft[0]['settings']['slots_qb']
        except Exception as e:
            s_qbs = 0
        try:
            s_rbs = draft[0]['settings']['slots_rb']
        except Exception as e:
            s_rbs = 0
        try:
            s_wrs = draft[0]['settings']['slots_wr']
        except Exception as e:
            s_wrs = 0
        try:
            s_tes = draft[0]['settings']['slots_te']
        except Exception as e:
            s_tes = 0
        try:
            s_flex = draft[0]['settings']['slots_flex']
        except Exception as e:
            s_flex = 0
        try:
            s_sflex = draft[0]['settings']['slots_super_flex']
        except Exception as e:
            s_sflex = 0
        try:
            s_ks = draft[0]['settings']['slots_k']
        except Exception as e:
            s_ks = 0
        try:
            s_dsts = draft[0]['settings']['slots_def']
        except Exception as e:
            s_dsts = 0
        try:
            s_bench = draft[0]['settings']['slots_bn']
        except Exception as e:
            s_bench = 0
    
    scoring = st.selectbox(
        "Input your league's scoring format",
        ('PPR', 'HPPR', 'Std', '1.5 TE', '6 Pt Pass', 'DK'))

    # GitHub raw URL for the CSV file
    github_csv_url = 'https://raw.githubusercontent.com/nzylakffa/sleepercalc/main/ROS%20Rankings%20for%20trade%20calc.csv'

    # Read the CSV file into a DataFrame
    ros = pd.read_csv(github_csv_url)
    

    # Keep these columns of ros
    ros = ros[["Player Name", "Team", "Pos", "PPR", "HPPR", "Std", "1.5 TE", "6 Pt Pass", "DK"]]
        
    # Replace defense names
    replace_dict = {'Ravens D/ST': 'BAL D/ST', 'Cowboys D/ST': 'DAL D/ST', 'Bills D/ST': 'BUF D/ST', 'Jets D/ST': 'NYJ D/ST', 'Dolphins D/ST': 'MIA D/ST',
                    'Browns D/ST': 'CLE D/ST', 'Raiders D/ST': 'LVR D/ST', 'Saints D/ST': 'NO D/ST', '49ers D/ST': 'SF D/ST', 'Colts D/ST': 'IND D/ST',
                    'Steelers D/ST': 'PIT D/ST', 'Bucs D/ST': 'TB D/ST', 'Chiefs D/ST': 'KC D/ST', 'Texans D/ST': 'HOU D/ST', 'Giants D/ST': 'NYG D/ST',
                    'Vikings D/ST': 'MIN D/ST', 'Jaguars D/ST': 'JAX D/ST', 'Bengals D/ST': 'CIN D/ST', 'Bears D/ST': 'CHI D/ST', 'Broncos D/ST': 'DEN D/ST',
                    'Packers D/ST': 'GB D/ST', 'Chargers D/ST': 'LAC D/ST', 'Lions D/ST': 'DET D/ST', 'Seahawks D/ST': 'SEA D/ST', 'Patriots D/ST': 'NE D/ST',
                    'Falcons D/ST': 'ATL D/ST', 'Eagles D/ST': 'PHI D/ST', 'Titans D/ST': 'TEN D/ST', 'Rams D/ST': 'LAR D/ST', 'Panthers D/ST': 'NE D/ST',
                    'Cardinals D/ST': 'ARI D/ST', 'Commanders D/ST': 'WAS D/ST'}
    ros['Player Name'] = ros['Player Name'].replace(replace_dict)
    
    
    ##########################################
    ##########################################
    # Our last step is figuring out free agency
    # I think we might need to pull all teams
    # Then remove those players from the ROS rankings list
    # The remaining is FA
    

with tab_trade:
    # Have user select which team is theirs
    my_team = st.selectbox("Select Your Display Name",
                           display_names)
    
    trade_partner = st.selectbox("Select Your Trade Partner's Display Name",
                                display_names)
    
    # Get the player id's for each team
    my_display_name_index = display_names.index(my_team)
    trade_partner_index = display_names.index(trade_partner)
    my_user_id = user_ids[my_display_name_index]
    trade_partner_user_id = user_ids[trade_partner_index]
    
#     # Initialize an empty list to store player_id values
#     player_ids = []

#     # Iterate through the list of rosters
#     for roster in league_rosters:
#         owner_id = roster.get('owner_id', '')

#         # Check if the current roster belongs to the target_owner_id
#         if owner_id == my_user_id:
#             players = roster.get('players', [])

#             # Append player_ids to the list
#             player_ids.extend(players)

#     # Create a DataFrame with the 'player_id' column
#     my_player_ids = pd.DataFrame({'player_id': player_ids})
    
    # Use the user id to get rosters!
    # Initialize an empty list to store player_id values
    my_player_ids = []
    opponent_player_ids = []
    all_other_player_ids = []

    # Iterate through the list of rosters
    for roster in league_rosters:
        owner_id = roster.get('owner_id', '')

        # Check if the current roster belongs to the target_owner_id
        if owner_id == my_user_id:
            my_players = roster.get('players', [])
            my_player_ids.extend(my_players)            
        elif owner_id == trade_partner_user_id:
            trade_partner_players = roster.get('players', [])
            opponent_player_ids.extend(trade_partner_players)
        else:
            other_team_players = roster.get('players', [])
            all_other_player_ids.extend(other_team_players)

    # Create a DataFrame with the 'player_id' column
    my_roster_ids = pd.DataFrame({'player_id': my_player_ids})
    trade_partner_roster_ids = pd.DataFrame({'player_id': opponent_player_ids})
    all_other_roster_player_ids = pd.DataFrame({'player_id': all_other_player_ids})
    
    # Stack these dfs on top of each other
    dfs = [my_roster_ids, trade_partner_roster_ids, all_other_roster_player_ids]
    rostered_players = pd.concat(dfs).reset_index(drop=True)

    # Pull in player id's and names
    # GitHub raw URL for the CSV file
    github_csv_url = 'https://raw.githubusercontent.com/nzylakffa/sleepercalc/main/sleeper_player_info.csv'

    # Read the CSV file into a DataFrame
    player_ids = pd.read_csv(github_csv_url)
 
    # Perform a left join to get player for each df
    final_my_team_roster = my_roster_ids.merge(player_ids, on='player_id', how='left')
    final_trade_partner_roster = trade_partner_roster_ids.merge(player_ids, on='player_id', how='left')
    final_rostered_players = rostered_players.merge(player_ids, on='player_id', how='left')
    
    # Change names from full_name to Player Name
    final_my_team_roster = final_my_team_roster.rename(columns={'full_name': 'Player Name'})    
    final_trade_partner_roster = final_trade_partner_roster.rename(columns={'full_name': 'Player Name'})
    final_rostered_players = final_rostered_players.rename(columns={'full_name': 'Player Name'})    
    
    # If None then make it player_id plus a space and D/ST
    final_my_team_roster['Player Name'] = final_my_team_roster['Player Name'].fillna(final_my_team_roster['player_id'] + ' D/ST')
    final_trade_partner_roster['Player Name'] = final_trade_partner_roster['Player Name'].fillna(final_trade_partner_roster['player_id'] + ' D/ST')
    final_rostered_players['Player Name'] = final_rostered_players['Player Name'].fillna(final_rostered_players['player_id'] + ' D/ST')
    
    # Drop player_id from each
    final_my_team_roster = final_my_team_roster[['Player Name']]
    final_trade_partner_roster = final_trade_partner_roster[['Player Name']]
    final_rostered_players = final_rostered_players[['Player Name']]

    # rename to match the other script
    my_team_df = final_my_team_roster
    trade_partner_df = final_trade_partner_roster  
    
    # Define find_best_match
    # Function to find the best match for each player
    @st.cache_data(ttl=600)  # Set the time-to-live (TTL) to 600 seconds (adjust as needed)
    def find_best_match(player_name, choices):
        return process.extractOne(player_name, choices)
    
    #################################################
    ########## My Team and Opponent Values ##########
    #################################################

    # Find best matches for each player in my_team_df
    my_team_df['Best Match'] = my_team_df['Player Name'].apply(lambda x: find_best_match(x, ros['Player Name']))

    # Split the result into matched and unmatched
    my_team_df['Matched'] = my_team_df['Best Match'].apply(lambda x: x[0] if x[1] >= 80 else None)
    my_team_df['Unmatched'] = my_team_df['Player Name'][~my_team_df['Matched'].notna()]

    # Merge matched players based on the best match
    my_team_values = my_team_df.merge(ros, left_on='Matched', right_on='Player Name', how='left')

    # Just keep certain columns
    # my_team_values = my_team_values[["Player Name_y", "Team", "Pos", "PPR", "HPPR", "Standard", "TE Premium", "6 Pt Pass"]]

    # Rename Column
    my_team_values = my_team_values.rename(columns={'Player Name_y': 'Player Name'})

    # Display the merged DataFrame
    my_team_values = my_team_values[["Player Name", "Team", "Pos", "PPR", "HPPR", "Std", "1.5 TE", "6 Pt Pass", "DK"]]
    
    # Add in a "New Pos" feature that's just pos
    my_team_values["New Pos"] = my_team_values["Pos"]

    ######################################
    ########## Opponents Values ##########
    ######################################

    # Find best matches for each player in my_team_df
    trade_partner_df['Best Match'] = trade_partner_df['Player Name'].apply(lambda x: find_best_match(x, ros['Player Name']))

    # Split the result into matched and unmatched
    trade_partner_df['Matched'] = trade_partner_df['Best Match'].apply(lambda x: x[0] if x[1] >= 80 else None)
    trade_partner_df['Unmatched'] = trade_partner_df['Player Name'][~trade_partner_df['Matched'].notna()]

    # Merge matched players based on the best match
    trade_partner_values = trade_partner_df.merge(ros, left_on='Matched', right_on='Player Name', how='left')

    # Just keep certain columns
    # my_team_values = my_team_values[["Player Name_y", "Team", "Pos", "PPR", "HPPR", "Standard", "TE Premium", "6 Pt Pass"]]

    # Rename Column
    trade_partner_values = trade_partner_values.rename(columns={'Player Name_y': 'Player Name'})

    # Display the merged DataFrame
    trade_partner_values = trade_partner_values[["Player Name", "Team", "Pos", "PPR", "HPPR", "Std", "1.5 TE", "6 Pt Pass", "DK"]]

    # Add in a "New Pos" feature that's just pos
    trade_partner_values["New Pos"] = trade_partner_values["Pos"]
    
    ################################################
    ########## Free Agent List and Values ##########
    ################################################
    
    # Find best matches for each player in my_team_df
    final_rostered_players['Best Match'] = final_rostered_players['Player Name'].apply(lambda x: find_best_match(x, ros['Player Name']))

    # Split the result into matched and unmatched
    final_rostered_players['Matched'] = final_rostered_players['Best Match'].apply(lambda x: x[0] if x[1] >= 80 else None)
    final_rostered_players['Unmatched'] = final_rostered_players['Player Name'][~final_rostered_players['Matched'].notna()]

    # Merge matched players based on the best match
    rostered_values = final_rostered_players.merge(ros, left_on='Matched', right_on='Player Name', how='left')

    # Just keep certain columns
    # my_team_values = my_team_values[["Player Name_y", "Team", "Pos", "PPR", "HPPR", "Standard", "TE Premium", "6 Pt Pass"]]

    # Rename Column
    rostered_values = rostered_values.rename(columns={'Player Name_y': 'Player Name'})

    # Display the merged DataFrame
    rostered_values = rostered_values[["Player Name", "Team", "Pos", "PPR", "HPPR", "Std", "1.5 TE", "6 Pt Pass", "DK"]]    
    
    # Now remove these rows from the ros rankings
    # Merge DataFrames and identify rows
    merged = pd.merge(ros, rostered_values, how="left", indicator=True)

    # Filter rows present only in 'ros'
    fa_df_values = merged[merged["_merge"] == "left_only"].drop(columns=["_merge"])
    
    # Sort by scoring
    fa_df_values = fa_df_values.sort_values(by=scoring, ascending=False)
    
    #######################################################
    ########## Calculate total for each position ##########
    #######################################################

    # My Team
    qbs = len(my_team_values[my_team_values['Pos'] == "QB"])
    rbs = len(my_team_values[my_team_values['Pos'] == "RB"])
    wrs = len(my_team_values[my_team_values['Pos'] == "WR"])
    tes = len(my_team_values[my_team_values['Pos'] == "TE"])
    ks = len(my_team_values[my_team_values['Pos'] == "K"])
    dsts = len(my_team_values[my_team_values['Pos'] == "D/ST"])

    # Trade Partner
    t_qbs = len(trade_partner_values[trade_partner_values['Pos'] == "QB"])
    t_rbs = len(trade_partner_values[trade_partner_values['Pos'] == "RB"])
    t_wrs = len(trade_partner_values[trade_partner_values['Pos'] == "WR"])
    t_tes = len(trade_partner_values[trade_partner_values['Pos'] == "TE"])
    t_ks = len(trade_partner_values[trade_partner_values['Pos'] == "K"])
    t_dsts = len(trade_partner_values[trade_partner_values['Pos'] == "D/ST"])
    
    #######################################
    ########## Creating Starters ##########
    #######################################

    # Creating Pos Starters
    starting_qbs = my_team_values[my_team_values['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[0:s_qbs]
    starting_rbs = my_team_values[my_team_values['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[0:s_rbs]
    starting_wrs = my_team_values[my_team_values['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[0:s_wrs]
    starting_tes = my_team_values[my_team_values['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[0:s_tes]
    starting_ks = my_team_values[my_team_values['Pos'] == "K"].sort_values(by = scoring, ascending = False)[0:s_ks]
    starting_dsts = my_team_values[my_team_values['Pos'] == "D/ST"].sort_values(by = scoring, ascending = False)[0:s_dsts]

    # Create FLEX Starters
    flex_viable_rbs = my_team_values[my_team_values['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[s_rbs:rbs]
    flex_viable_wrs = my_team_values[my_team_values['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[s_wrs:wrs]
    flex_viable_tes = my_team_values[my_team_values['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[s_tes:tes]
    starting_flex = pd.concat([flex_viable_rbs, flex_viable_wrs, flex_viable_tes]).sort_values(by = scoring, ascending = False)[0:s_flex]
    starting_flex["New Pos"] = "FLEX"

    # Create SuperFlex
    superflex_viable_qbs = my_team_values[my_team_values['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[s_qbs:qbs]
    starting_superflex = pd.concat([superflex_viable_qbs, starting_flex[s_flex:]])[0:s_sflex]
    starting_superflex["New Pos"] = "SuperFlex"
    final_starters = pd.concat([starting_qbs, starting_rbs, starting_wrs, starting_tes, starting_flex, starting_superflex, starting_dsts]).reset_index(drop=True)
    final_starters = final_starters[["Pos", "New Pos", "Player Name", scoring]]    

    # Create Bench
    my_team_values = my_team_values[["Pos","New Pos", "Player Name", scoring]]  
    bench_df = pd.concat([final_starters, my_team_values])
    bench_df = bench_df.drop_duplicates(subset = ["Player Name", scoring], keep=False)

    ##################################################
    ########## Opponents Starters and Bench ##########
    ##################################################

    # Creating Pos Starters
    trade_partner_starting_qbs = trade_partner_values[trade_partner_values['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[0:s_qbs]
    trade_partner_starting_rbs = trade_partner_values[trade_partner_values['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[0:s_rbs]
    trade_partner_starting_wrs = trade_partner_values[trade_partner_values['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[0:s_wrs]
    trade_partner_starting_tes = trade_partner_values[trade_partner_values['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[0:s_tes]
    trade_partner_starting_ks = trade_partner_values[trade_partner_values['Pos'] == "K"].sort_values(by = scoring, ascending = False)[0:s_ks]
    trade_partner_starting_dsts = trade_partner_values[trade_partner_values['Pos'] == "D/ST"].sort_values(by = scoring, ascending = False)[0:s_dsts]

    # Create FLEX Starters
    trade_partner_flex_viable_rbs = trade_partner_values[trade_partner_values['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[s_rbs:t_rbs]
    trade_partner_flex_viable_wrs = trade_partner_values[trade_partner_values['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[s_wrs:t_wrs]
    trade_partner_flex_viable_tes = trade_partner_values[trade_partner_values['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[s_tes:t_tes]
    trade_partner_starting_flex = pd.concat([trade_partner_flex_viable_rbs, trade_partner_flex_viable_wrs, trade_partner_flex_viable_tes]).sort_values(by = scoring, ascending = False)[0:s_flex]
    trade_partner_starting_flex["New Pos"] = "FLEX"

    # Create SuperFlex
    trade_partner_superflex_viable_qbs = trade_partner_values[trade_partner_values['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[s_qbs:t_qbs]
    trade_partner_starting_superflex = pd.concat([trade_partner_superflex_viable_qbs, trade_partner_starting_flex[s_flex:]])[0:s_sflex]
    trade_partner_starting_superflex["New Pos"] = "SuperFlex"
    trade_partner_final_starters = pd.concat([trade_partner_starting_qbs, trade_partner_starting_rbs, trade_partner_starting_wrs, trade_partner_starting_tes,
                                              trade_partner_starting_flex, trade_partner_starting_superflex, trade_partner_starting_dsts]).reset_index(drop=True)
    trade_partner_final_starters = trade_partner_final_starters[["Pos","New Pos", "Player Name", scoring]]    

    # Create Bench
    trade_partner_values = trade_partner_values[["Pos","New Pos", "Player Name", scoring]]  
    trade_partner_bench_df = pd.concat([trade_partner_final_starters, trade_partner_values])
    trade_partner_bench_df = trade_partner_bench_df.drop_duplicates(subset = ["Player Name", scoring], keep=False)
    
    ############################################
    ########## Calculate Adjusted PPG ##########
    ############################################

    ### Calculate Total Roster Adjusted PPG ###
    if (s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts) == 0:
        qb_weight = 0
        rb_weight = 0
        wr_weight = 0
        te_weight = 0
        k_weight = 0
        dst_weight = 0
    else:
        qb_weight = (s_qbs+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        rb_weight = (s_rbs+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        wr_weight = (s_wrs+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        te_weight = (s_tes+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        k_weight = (s_ks)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        dst_weight = (s_dsts)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)

    # Create df with those weights
    all_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [qb_weight, rb_weight, wr_weight, te_weight, k_weight, dst_weight]})  

    # Merge weights into bench_df
    bench_weights_df = bench_df.merge(all_weights, on = "Pos")
    bench_weights_df["Weighted PPG"] = bench_weights_df[scoring]*bench_weights_df["Weight"]

    # Divide each of those weights by the number on the bench
    qbs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "QB"].shape[0]
    rbs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "RB"].shape[0]
    wrs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "WR"].shape[0]
    tes_on_bench = bench_weights_df[bench_weights_df["Pos"] == "TE"].shape[0]
    ks_on_bench = bench_weights_df[bench_weights_df["Pos"] == "K"].shape[0]
    dsts_on_bench = bench_weights_df[bench_weights_df["Pos"] == "D/ST"].shape[0]

    # Adjust weights to reflect that number
    if qbs_on_bench != 0:
        adj_qb_weight = qb_weight/qbs_on_bench
    else:
        adj_qb_weight = 0

    if rbs_on_bench != 0:
        adj_rb_weight = rb_weight/rbs_on_bench
    else:
        adj_rb_weight = 0        

    if wrs_on_bench != 0:
        adj_wr_weight = wr_weight/wrs_on_bench
    else:
        adj_wr_weight = 0

    if tes_on_bench != 0:
        adj_te_weight = te_weight/tes_on_bench
    else:
        adj_te_weight = 0

    if ks_on_bench != 0:
        adj_k_weight = k_weight/ks_on_bench
    else:
        adj_k_weight = 0

    if dsts_on_bench != 0:
        adj_dst_weight = dst_weight/dsts_on_bench
    else:
        adj_dst_weight = 0

    # Create df with those adj weights
    adj_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [adj_qb_weight, adj_rb_weight, adj_wr_weight, adj_te_weight, adj_k_weight, adj_dst_weight]}) 

    # Merge weights into bench_df
    adj_bench_weights_df = bench_df.merge(adj_weights, on = "Pos")
    adj_bench_weights_df["Weighted PPG"] = adj_bench_weights_df[scoring]*adj_bench_weights_df["Weight"]
    
    #################################################
    ########## Trade Partners Adjusted PPG ##########
    #################################################

    ### Calculate Total Roster Adjusted PPG ###

    # Create df with those weights
    all_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [qb_weight, rb_weight, wr_weight, te_weight, k_weight, dst_weight]})  

    # Merge weights into bench_df
    trade_partner_bench_weights_df = trade_partner_bench_df.merge(all_weights, on = "Pos")
    trade_partner_bench_weights_df["Weighted PPG"] = trade_partner_bench_weights_df[scoring]*trade_partner_bench_weights_df["Weight"]

    # Divide each of those weights by the number on the bench
    qbs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "QB"].shape[0]
    rbs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "RB"].shape[0]
    wrs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "WR"].shape[0]
    tes_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "TE"].shape[0]
    ks_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "K"].shape[0]
    dsts_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "D/ST"].shape[0]

    # Adjust weights to reflect that number
    if qbs_on_bench != 0:
        adj_qb_weight = qb_weight/qbs_on_bench
    else:
        adj_qb_weight = 0

    if rbs_on_bench != 0:
        adj_rb_weight = rb_weight/rbs_on_bench
    else:
        adj_rb_weight = 0        

    if wrs_on_bench != 0:
        adj_wr_weight = wr_weight/wrs_on_bench
    else:
        adj_wr_weight = 0

    if tes_on_bench != 0:
        adj_te_weight = te_weight/tes_on_bench
    else:
        adj_te_weight = 0

    if ks_on_bench != 0:
        adj_k_weight = k_weight/ks_on_bench
    else:
        adj_k_weight = 0

    if dsts_on_bench != 0:
        adj_dst_weight = dst_weight/dsts_on_bench
    else:
        adj_dst_weight = 0

    # Create df with those adj weights
    adj_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [adj_qb_weight, adj_rb_weight, adj_wr_weight, adj_te_weight, adj_k_weight, adj_dst_weight]}) 

    # Merge weights into bench_df
    trade_partner_adj_bench_weights_df = trade_partner_bench_df.merge(adj_weights, on = "Pos")
    trade_partner_adj_bench_weights_df["Weighted PPG"] = trade_partner_adj_bench_weights_df[scoring]*trade_partner_adj_bench_weights_df["Weight"]

    # Adjusted PPG!
    og_score = round(final_starters[scoring].sum() + adj_bench_weights_df['Weighted PPG'].sum(),2)
    st.write("My Team's Adjusted PPG: ", og_score)
    st.write("Trade Partner's Adjusted PPG: ", round(trade_partner_final_starters[scoring].sum() + trade_partner_adj_bench_weights_df['Weighted PPG'].sum(),2))
    
    # Combine starters and bench
    my_roster = [*final_starters['Player Name'], *adj_bench_weights_df['Player Name']]
    opponents_roster = [*trade_partner_final_starters['Player Name'], *trade_partner_adj_bench_weights_df['Player Name']]
    
    # Make a drop down for each team's roster
    my_team_list = st.multiselect(
        "Player's You're Trading AWAY",
        my_roster)
    
    opponents_roster_list = st.multiselect(
        "Player's You're Trading FOR",
        opponents_roster)
    
    # This is the new team...before adding in the other players
    my_new_team = [x for x in my_roster if x not in my_team_list]
    opponent_new_team = [x for x in opponents_roster if x not in opponents_roster_list]
    
    # Now we add the player's we're trading for to the list
    my_new_team2 = [*my_new_team, *opponents_roster_list]
    opponent_new_team2 = [*opponent_new_team, *my_team_list]
       
    # Now we take that list and go back to our final roster. We want to only keep rows of players that are left
    # Stack df's on top of each other
    my_dfs = [final_starters, adj_bench_weights_df]
    my_og_roster = pd.concat(my_dfs).reset_index(drop=True)
    left_on_my_roster = my_og_roster[my_og_roster['Player Name'].isin(my_new_team2)]
    
    # Next create a subset of the opponents team with the players you're getting
    opponent_dfs = [trade_partner_final_starters, trade_partner_adj_bench_weights_df]
    opponent_og_roster = pd.concat(opponent_dfs).reset_index(drop=True)
    get_from_opponent = opponent_og_roster[opponent_og_roster['Player Name'].isin(opponents_roster_list)]

    # Then stack those two DF's!
    my_post_trade_roster = pd.concat([left_on_my_roster, get_from_opponent])
    my_post_trade_roster = my_post_trade_roster[["Pos", "Player Name", scoring]]
    
    # Do the same for the opponent
    # Stack df's on top of each other
    opponent_dfs = [trade_partner_final_starters, trade_partner_adj_bench_weights_df]
    opponent_og_roster = pd.concat(opponent_dfs).reset_index(drop=True)
    left_on_opponent_roster = opponent_og_roster[opponent_og_roster['Player Name'].isin(opponent_new_team2)]
    
    # Next create a subset of the opponents team with the players you're getting
    my_dfs = [final_starters, adj_bench_weights_df]
    my_og_roster = pd.concat(my_dfs).reset_index(drop=True)
    get_from_me = my_og_roster[my_og_roster['Player Name'].isin(my_team_list)]

    # Then stack those two DF's!
    opponent_post_trade_roster = pd.concat([left_on_opponent_roster, get_from_me])
    opponent_post_trade_roster = opponent_post_trade_roster[["Pos", "Player Name", scoring]]
    

    # Add in a "New Pos" feature that's just pos to each
    my_post_trade_roster["New Pos"] = my_post_trade_roster["Pos"]
    opponent_post_trade_roster["New Pos"] = opponent_post_trade_roster["Pos"]
    
    def extract_player_name(player):
    # Remove "Player(" from the beginning and extract the player name
        player_name = re.sub(r'^Player\((.*?)\)', r'\1', str(player))
        return re.match(r"^(.*?), points", player_name).group(1)

    def find_best_match_simple(player_name, choices):
        # Get the best match using simple string matching
        matches = difflib.get_close_matches(player_name, choices, n=1, cutoff=0.85)

        # Return the best match and its similarity score
        if matches:
            return matches[0], difflib.SequenceMatcher(None, player_name, matches[0]).ratio()
        else:
            return None, 0.0

#     # Create a DF that has the free agents
#     fa_list = qb_fa + rb_fa + wr_fa + te_fa + k_fa + dst_fa

#     # Replace string manipulation with a function
#     fa_df = pd.DataFrame({'Player Name': [extract_player_name(player) for player in fa_list]})

#     # Find best matches for each player in my_team_df using the simple method
#     fa_df['Best Match'] = fa_df['Player Name'].apply(lambda x: find_best_match_simple(x, ros['Player Name']))

#     # Split the result into matched and unmatched
#     fa_df['Matched'] = fa_df['Best Match'].apply(lambda x: x[0] if x[1] >= .85 else None)
#     fa_df['Unmatched'] = fa_df['Player Name'][~fa_df['Matched'].notna()]

#     # Merge matched players based on the best match
#     fa_df_values = fa_df.merge(ros, left_on='Matched', right_on='Player Name', how='left')

#     # Rename Column
#     fa_df_values = fa_df_values.rename(columns={'Player Name_y': 'Player Name'})

#     # Display the merged DataFrame
#     fa_df_values = fa_df_values[["Player Name", "Team", "Pos", "PPR", "HPPR", "Std", "1.5 TE", "6 Pt Pass", "DK"]]

#     # Sort by scoring
#     fa_df_values = fa_df_values.sort_values(by=scoring, ascending=False)
#     # st.dataframe(fa_df_values)

    # Select the position you wish to add off FA
    fa_pos = st.multiselect("Which Position Do You Want to Add?",
                           ["QB", "RB", "WR", "TE", "K", "D/ST"])

    # Have that list as an option to multiselect for each position
    if fa_pos is not None:
        fa_add = st.multiselect("Pick player(s) to ADD",
                                fa_df_values[fa_df_values['Pos'].isin(fa_pos)]['Player Name'])
        
    team_drop = st.multiselect("Pick player(s) to DROP",
                              my_post_trade_roster['Player Name'])
    

    # Make those two adjustments to your team
    my_post_trade_roster = pd.concat([my_post_trade_roster, fa_df_values[fa_df_values['Player Name'].isin(fa_add)]])
    my_post_trade_roster = my_post_trade_roster[~my_post_trade_roster['Player Name'].isin(team_drop)]
    
    # Signal if your team is the correct number of people
    players_to_adjust = (len(fa_add) + len(opponents_roster_list)) - (len(team_drop) + len(my_team_list))

    if players_to_adjust > 0:
        action = "Drop or Trade Away"
        st.subheader(f":red[{action} {players_to_adjust} More Player{'s' if players_to_adjust != 1 else ''}]")
    elif players_to_adjust < 0:
        action = "Add or Trade For"
        st.subheader(f":red[{action} {abs(players_to_adjust)} More Player{'s' if abs(players_to_adjust) != 1 else ''}]")
    else:
        st.subheader(":green[Add or Trade For 0 More Players]")

    ##############################################################
    ########## Now we need to recalculate adjusted PPG! ##########
    ##############################################################
    
    
    #######################################################
    ########## Calculate total for each position ##########
    #######################################################

    # My Team
    qbs = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "QB"])
    rbs = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "RB"])
    wrs = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "WR"])
    tes = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "TE"])
    ks = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "K"])
    dsts = len(my_post_trade_roster[my_post_trade_roster['Pos'] == "D/ST"])

    # Trade Partner
    t_qbs = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "QB"])
    t_rbs = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "RB"])
    t_wrs = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "WR"])
    t_tes = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "TE"])
    t_ks = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "K"])
    t_dsts = len(opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "D/ST"])    

    #######################################
    ########## Creating Starters ##########
    #######################################

    # Creating Pos Starters
    starting_qbs = my_post_trade_roster[my_post_trade_roster['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[0:s_qbs]
    starting_rbs = my_post_trade_roster[my_post_trade_roster['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[0:s_rbs]
    starting_wrs = my_post_trade_roster[my_post_trade_roster['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[0:s_wrs]
    starting_tes = my_post_trade_roster[my_post_trade_roster['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[0:s_tes]
    starting_ks = my_post_trade_roster[my_post_trade_roster['Pos'] == "K"].sort_values(by = scoring, ascending = False)[0:s_ks]
    starting_dsts = my_post_trade_roster[my_post_trade_roster['Pos'] == "D/ST"].sort_values(by = scoring, ascending = False)[0:s_dsts]

    # Create FLEX Starters
    flex_viable_rbs = my_post_trade_roster[my_post_trade_roster['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[s_rbs:rbs]
    flex_viable_wrs = my_post_trade_roster[my_post_trade_roster['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[s_wrs:wrs]
    flex_viable_tes = my_post_trade_roster[my_post_trade_roster['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[s_tes:tes]
    starting_flex = pd.concat([flex_viable_rbs, flex_viable_wrs, flex_viable_tes]).sort_values(by = scoring, ascending = False)[0:s_flex]
    starting_flex["New Pos"] = "FLEX"

    # Create SuperFlex
    superflex_viable_qbs = my_post_trade_roster[my_post_trade_roster['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[s_qbs:qbs]
    starting_superflex = pd.concat([superflex_viable_qbs, starting_flex[s_flex:]])[0:s_sflex]
    starting_superflex["New Pos"] = "SuperFlex"
    final_starters = pd.concat([starting_qbs, starting_rbs, starting_wrs, starting_tes, starting_flex, starting_superflex, starting_dsts]).reset_index(drop=True)
    final_starters = final_starters[["Pos", "New Pos", "Player Name", scoring]]    

    # Create Bench
    my_post_trade_roster = my_post_trade_roster[["Pos", "New Pos", "Player Name", scoring]]  
    bench_df = pd.concat([final_starters, my_post_trade_roster])
    bench_df = bench_df.drop_duplicates(subset = ["Player Name", scoring], keep=False)
    
    ##################################################
    ########## Opponents Starters and Bench ##########
    ##################################################

    # Creating Pos Starters
    trade_partner_starting_qbs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[0:s_qbs]
    trade_partner_starting_rbs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[0:s_rbs]
    trade_partner_starting_wrs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[0:s_wrs]
    trade_partner_starting_tes = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[0:s_tes]
    trade_partner_starting_ks = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "K"].sort_values(by = scoring, ascending = False)[0:s_ks]
    trade_partner_starting_dsts = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "D/ST"].sort_values(by = scoring, ascending = False)[0:s_dsts]

    # Create FLEX Starters
    trade_partner_flex_viable_rbs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "RB"].sort_values(by = scoring, ascending = False)[s_rbs:t_rbs]
    trade_partner_flex_viable_wrs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "WR"].sort_values(by = scoring, ascending = False)[s_wrs:t_wrs]
    trade_partner_flex_viable_tes = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "TE"].sort_values(by = scoring, ascending = False)[s_tes:t_tes]
    trade_partner_starting_flex = pd.concat([trade_partner_flex_viable_rbs, trade_partner_flex_viable_wrs, trade_partner_flex_viable_tes]).sort_values(by = scoring, ascending = False)[0:s_flex]
    trade_partner_starting_flex["New Pos"] = "FLEX"

    # Create SuperFlex
    trade_partner_superflex_viable_qbs = opponent_post_trade_roster[opponent_post_trade_roster['Pos'] == "QB"].sort_values(by = scoring, ascending = False)[s_qbs:t_qbs]
    trade_partner_starting_superflex = pd.concat([trade_partner_superflex_viable_qbs, trade_partner_starting_flex[s_flex:]])[0:s_sflex]
    trade_partner_starting_superflex["New Pos"] = "SuperFlex"
    trade_partner_final_starters = pd.concat([trade_partner_starting_qbs, trade_partner_starting_rbs, trade_partner_starting_wrs, trade_partner_starting_tes,
                                              trade_partner_starting_flex, trade_partner_starting_superflex, trade_partner_starting_dsts]).reset_index(drop=True)
    trade_partner_final_starters = trade_partner_final_starters[["Pos", "New Pos", "Player Name", scoring]]    

    # Create Bench
    trade_partner_values = opponent_post_trade_roster[["Pos", "New Pos", "Player Name", scoring]]  
    trade_partner_bench_df = pd.concat([trade_partner_final_starters, opponent_post_trade_roster])
    trade_partner_bench_df = trade_partner_bench_df.drop_duplicates(subset = ["Player Name", scoring], keep=False)
    
    ############################################
    ########## Calculate Adjusted PPG ##########
    ############################################

    ### Calculate Total Roster Adjusted PPG ###
    if (s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts) == 0:
        qb_weight = 0
        rb_weight = 0
        wr_weight = 0
        te_weight = 0
        k_weight = 0
        dst_weight = 0
    else:
        qb_weight = (s_qbs+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        rb_weight = (s_rbs+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        wr_weight = (s_wrs+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        te_weight = (s_tes+s_flex+s_sflex)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        k_weight = (s_ks)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)
        dst_weight = (s_dsts)/(s_qbs+s_rbs+s_wrs+s_tes+s_flex+s_sflex+s_ks+s_dsts)

    # Create df with those weights
    all_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [qb_weight, rb_weight, wr_weight, te_weight, k_weight, dst_weight]})  

    # Merge weights into bench_df
    bench_weights_df = bench_df.merge(all_weights, on = "Pos")
    bench_weights_df["Weighted PPG"] = bench_weights_df[scoring]*bench_weights_df["Weight"]

    # Divide each of those weights by the number on the bench
    qbs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "QB"].shape[0]
    rbs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "RB"].shape[0]
    wrs_on_bench = bench_weights_df[bench_weights_df["Pos"] == "WR"].shape[0]
    tes_on_bench = bench_weights_df[bench_weights_df["Pos"] == "TE"].shape[0]
    ks_on_bench = bench_weights_df[bench_weights_df["Pos"] == "K"].shape[0]
    dsts_on_bench = bench_weights_df[bench_weights_df["Pos"] == "D/ST"].shape[0]

    # Adjust weights to reflect that number
    if qbs_on_bench != 0:
        adj_qb_weight = qb_weight/qbs_on_bench
    else:
        adj_qb_weight = 0

    if rbs_on_bench != 0:
        adj_rb_weight = rb_weight/rbs_on_bench
    else:
        adj_rb_weight = 0        

    if wrs_on_bench != 0:
        adj_wr_weight = wr_weight/wrs_on_bench
    else:
        adj_wr_weight = 0

    if tes_on_bench != 0:
        adj_te_weight = te_weight/tes_on_bench
    else:
        adj_te_weight = 0

    if ks_on_bench != 0:
        adj_k_weight = k_weight/ks_on_bench
    else:
        adj_k_weight = 0

    if dsts_on_bench != 0:
        adj_dst_weight = dst_weight/dsts_on_bench
    else:
        adj_dst_weight = 0

    # Create df with those adj weights
    adj_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [adj_qb_weight, adj_rb_weight, adj_wr_weight, adj_te_weight, adj_k_weight, adj_dst_weight]}) 

    # Merge weights into bench_df
    adj_bench_weights_df = bench_df.merge(adj_weights, on = "Pos")
    adj_bench_weights_df["Weighted PPG"] = adj_bench_weights_df[scoring]*adj_bench_weights_df["Weight"]
    
    #################################################
    ########## Trade Partners Adjusted PPG ##########
    #################################################

    ### Calculate Total Roster Adjusted PPG ###

    # Create df with those weights
    all_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [qb_weight, rb_weight, wr_weight, te_weight, k_weight, dst_weight]})  

    # Merge weights into bench_df
    trade_partner_bench_weights_df = trade_partner_bench_df.merge(all_weights, on = "Pos")

    trade_partner_bench_weights_df["Weighted PPG"] = trade_partner_bench_weights_df[scoring]*trade_partner_bench_weights_df["Weight"]

    # Divide each of those weights by the number on the bench
    qbs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "QB"].shape[0]
    rbs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "RB"].shape[0]
    wrs_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "WR"].shape[0]
    tes_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "TE"].shape[0]
    ks_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "K"].shape[0]
    dsts_on_bench = trade_partner_bench_weights_df[trade_partner_bench_weights_df["Pos"] == "D/ST"].shape[0]

    # Adjust weights to reflect that number
    if qbs_on_bench != 0:
        adj_qb_weight = qb_weight/qbs_on_bench
    else:
        adj_qb_weight = 0

    if rbs_on_bench != 0:
        adj_rb_weight = rb_weight/rbs_on_bench
    else:
        adj_rb_weight = 0        

    if wrs_on_bench != 0:
        adj_wr_weight = wr_weight/wrs_on_bench
    else:
        adj_wr_weight = 0

    if tes_on_bench != 0:
        adj_te_weight = te_weight/tes_on_bench
    else:
        adj_te_weight = 0

    if ks_on_bench != 0:
        adj_k_weight = k_weight/ks_on_bench
    else:
        adj_k_weight = 0

    if dsts_on_bench != 0:
        adj_dst_weight = dst_weight/dsts_on_bench
    else:
        adj_dst_weight = 0

    # Create df with those adj weights
    adj_weights = pd.DataFrame(
    {"Pos": ["QB", "RB", "WR", "TE", "K", "D/ST"],
        "Weight": [adj_qb_weight, adj_rb_weight, adj_wr_weight, adj_te_weight, adj_k_weight, adj_dst_weight]}) 

    # Merge weights into bench_df
    trade_partner_adj_bench_weights_df = trade_partner_bench_df.merge(adj_weights, on = "Pos")
    trade_partner_adj_bench_weights_df["Weighted PPG"] = trade_partner_adj_bench_weights_df[scoring]*trade_partner_adj_bench_weights_df["Weight"]

    # Is it a good or bad trade?
    if og_score == (round(final_starters[scoring].sum() + adj_bench_weights_df['Weighted PPG'].sum(),2)):
        st.subheader(f":gray[This is a perfectly even trade!]")
    elif og_score < (round(final_starters[scoring].sum() + adj_bench_weights_df['Weighted PPG'].sum(),2)):
        st.subheader(f":green[You are winning this trade!]")
    else:
        st.subheader(f":red[You are losing this trade!]")
    
    # Adjusted PPG!
    st.write("My Team's New Adjusted PPG: ", round(final_starters[scoring].sum() + adj_bench_weights_df['Weighted PPG'].sum(),2))
    st.write("Trade Partner's New Adjusted PPG: ", round(trade_partner_final_starters[scoring].sum() + trade_partner_adj_bench_weights_df['Weighted PPG'].sum(),2))
    
    # Sort
    my_post_trade_roster = my_post_trade_roster.sort_values(by = ['Pos', scoring], ascending=False)
    opponent_post_trade_roster = opponent_post_trade_roster.sort_values(by = ['Pos', scoring], ascending=False)
    
    # Delete New Pos
    my_post_trade_roster = my_post_trade_roster[['Pos', 'Player Name', scoring]]
    opponent_post_trade_roster = opponent_post_trade_roster[['Pos', 'Player Name', scoring]]
    

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3 style='text-align: center;'>My Post Trade Team</h3>", unsafe_allow_html=True)
        st.dataframe(my_post_trade_roster, use_container_width = True)
        
    with col2:
        st.markdown("<h3 style='text-align: center;'>Opponent's Post Trade Team</h3>", unsafe_allow_html=True)
        st.dataframe(opponent_post_trade_roster, use_container_width = True)
