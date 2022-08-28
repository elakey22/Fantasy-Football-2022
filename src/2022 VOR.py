
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

################# DISPLAY ALL ROWS OF DATAFRAMES
#pd.set_option('display.max_rows', None)


############## IMPORT DATA
qb_df = pd.read_csv('data\FantasyPros_Fantasy_Football_Projections_QB.csv')
rb_df = pd.read_csv('data\FantasyPros_Fantasy_Football_Projections_RB.csv')
wr_df = pd.read_csv('data\FantasyPros_Fantasy_Football_Projections_WR.csv')
te_df = pd.read_csv('data\FantasyPros_Fantasy_Football_Projections_TE.csv')


############### SET POSITIONS
qb_df['Pos'] = 'QB'
rb_df['Pos'] = 'RB'
wr_df['Pos'] = 'WR'
te_df['Pos'] = 'TE'


############### RENAME DATAFRAME KEYS FOR UNIFORM CALCULATIONS
qb_df = qb_df.rename({
    'YDS': 'PassingYds',
    'TDS': 'PassingTD',
    'INTS': 'Int',
    'YDS.1': 'RushingYds',
    'TDS.1': 'RushingTD',
    'FPTS': 'FantasyPoints',        
},axis=1)

rb_df = rb_df.rename({
    'YDS': 'RushingYds',
    'TDS': 'RushingTD',
    'REC': 'Receptions',
    'YDS.1': 'ReceivingYds',
    'TDS.1': 'ReceivingTD',
    'FPTS': 'FantasyPoints',        
},axis=1)

wr_df = wr_df.rename({
    'YDS': 'ReceivingYds',
    'TDS': 'ReceivingTD',
    'REC': 'Receptions',
    'YDS.1': 'RushingYds',
    'TDS.1': 'RushingTD',
    'FPTS': 'FantasyPoints',        
},axis=1)

te_df = te_df.rename({
    'YDS': 'ReceivingYds',
    'TDS': 'ReceivingTD',
    'REC': 'Receptions',
    'FPTS': 'FantasyPoints',        
},axis=1)


############## ADD BLANK COLUMNS TO DATA FRAMES
qb_df['Receptions'] = 0
qb_df['ReceivingYds'] = 0
qb_df['ReceivingTD'] = 0
rb_df['PassingYds'] = 0
rb_df['PassingTD'] = 0
rb_df['Int'] = 0
wr_df['PassingYds'] = 0
wr_df['PassingTD'] = 0
wr_df['Int'] = 0
te_df['PassingYds'] = 0
te_df['PassingTD'] = 0
te_df['Int'] = 0
te_df['RushingYds'] = 0
te_df['RushingTD'] = 0

################ FIX DATA TYPES BY CHANGING TO FLOAT
qb_df['PassingYds'] = qb_df['PassingYds'].str.replace(',','').astype(float)
rb_df['RushingYds'] = rb_df['RushingYds'].str.replace(',','').astype(float)
wr_df['ReceivingYds'] = wr_df['ReceivingYds'].str.replace(',','').astype(float)
te_df['ReceivingYds'] = te_df['ReceivingYds'].str.replace(',','').astype(float)


################ COMBINE DATA FRAMES
df = pd.concat([qb_df, rb_df, wr_df, te_df])
df = df[['Player', 'Team', 'Pos', 'PassingYds', 'PassingTD', 'Int', 'RushingYds', 'RushingTD', 'FL', 'Receptions', 'ReceivingYds', 'ReceivingTD', 'FantasyPoints']]

################# CALCULATE FANTASY TOTALS
scoring_weights = {
    'receptions': 1, # PPR
    'receiving_yds': 0.1,
    'receiving_td': 6,
    'FL': -2, #fumbles lost
    'rushing_yds': 0.1,
    'rushing_td': 6,
    'passing_yds': 0.04,
    'passing_td': 4,
    'int': -2
}

df['FantasyPoints'] = (
    df['Receptions']*scoring_weights['receptions'] + df['ReceivingYds']*scoring_weights['receiving_yds'] + \
    df['ReceivingTD']*scoring_weights['receiving_td'] + df['FL']*scoring_weights['FL'] + \
    df['RushingYds']*scoring_weights['rushing_yds'] + df['RushingTD']*scoring_weights['rushing_td'] + \
    df['PassingYds']*scoring_weights['passing_yds'] + df['PassingTD']*scoring_weights['passing_td'] + \
    df['Int']*scoring_weights['int'] )


################ LOAD ADP DATA
adp_df = pd.read_csv('data\FantasyPros_2022_Draft_ALL_Rankings.csv', index_col=0)

adp_df['ADP RANK'] = adp_df.index
adp_df_cutoff = adp_df[:90]


################ CALCULATE REPLACEMENT PLAYER VALUES
replacement_players = {
    'RB': '',
    'QB': '',
    'WR': '',
    'TE': ''
}

for _, row in adp_df_cutoff.iterrows():
 
    player = row['PLAYER NAME']
    temp_player = df.loc[df['Player'] == player]
    position = temp_player['Pos'].tolist()[0]
    
    if position in replacement_players:
        replacement_players[position] = player 

df = df[['Player', 'Pos', 'Team', 'FantasyPoints']]

replacement_values = {}

for position, player_name in replacement_players.items():
    
    player = df.loc[df['Player'] == player_name]
    replacement_values[position] = player['FantasyPoints'].tolist()[0]
    
pd.set_option('chained_assignment', None)

df = df.loc[df['Pos'].isin(['QB', 'RB', 'WR', 'TE'])]


################### CALCULATE PLAYER'S VOR
df['VOR'] = df.apply(
    lambda row: row['FantasyPoints'] - replacement_values.get(row['Pos']), axis=1
)

df['VOR'] = df['VOR'].apply(lambda x: (x - df['VOR'].min()) / (df['VOR'].max() - df['VOR'].min()))
df['VOR Rank'] = df['VOR'].rank(ascending=False)
df = df.sort_values(by='VOR Rank')


################## CREATE AND PLOT DRAFT POOL
num_teams = 14
num_spots = 12 # 1 QB, 2RB, 2WR, 1TE, 2FLEX, 4 BENCH (2 EXTRA)
draft_pool = num_teams * num_spots

df_copy = df[:draft_pool]
sns.boxplot(x=df_copy['Pos'], y=df_copy['VOR'])
#plt.show()  ##### SHOW PLOTS (CURRENTLY DISABLED)


################# RENAME COLUMNS
df = df.rename({
    'VOR': 'Value',
    'VOR Rank': 'Value Rank'
}, axis=1) 

adp_df = adp_df.rename({
    'PLAYER NAME': 'Player',
    'ADP RANK': 'ADP Rank'
}, axis=1)

adp_df = adp_df.drop(columns= ['TEAM', 'TIERS', 'FAN PTS', 'YDS', 'TDS', 'REC', 'YDS.1', 'TDS.1', 'ATT', 'YDS.2', 'TDS.2'])


################# MERGE AND SORT DATAFRAME
final_df = df.merge(adp_df, how='left', on=['Player'])
final_df['Diff in ADP and Value'] = final_df['ADP Rank'] - final_df['Value Rank']

draft_pool = final_df.sort_values(by='ADP Rank')[:draft_pool]


################# SAVE DRAFT POOL TO CSV
#draft_pool.to_csv('data\sleeperDraft_pool.csv', index = False)