import requests
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os



load_dotenv()  # Load environment variables from .env file
API_KEY=os.getenv("API_KEY")  # Get the API key from environment variables

headers = {
    "X-apisports-Key":API_KEY,
}
base_url = "https://v3.football.api-sports.io"

engine=create_engine('postgresql://ram:1234@host.docker.internal:5432/football_project')


def fetch_fixtures(league_id , season):
    url=f"{base_url}/fixtures"
    params = {"season": season,"league": league_id   # Premier League
              }
    response=requests.get(url , headers=headers,params=params)
    return response.json()['response']
def fetch_players(league_id,season):
    url=f"{base_url}/players/topscorers"
    params={"season":season,"league":league_id}
    response=requests.get(url,headers=headers,params=params)
    return response.json()['response']

def parse_players(scorers):
    players=[]
    
    for s in scorers:
        player=s["player"]
        stats=s["statistics"][0]
        players.append({
         "player_id":player['id'],
         "player_name":player['name'],
         "nationality":player['nationality'],
         "team_id":stats['team']['id'],
         "team_name":stats['team']['name'],
         "position":stats['games']['position'],
         "appearences":stats['games']['appearences'],
         "goals":stats['goals']['total'],
         "assists":stats['goals']['assists'],
         "penalties":stats['penalty']['scored'],
         "rating":stats['games']['rating']
        })
    return pd.DataFrame(players)

def upsert_players(df,table_name):
    if df.empty:
        print("no new stats/player to load")
        return
    df.to_sql(
        f"{table_name}_temp",
        engine,
        schema='public',
        if_exists='replace',
        index=False,
    )
    
    with engine.connect() as conn:
        conn.execute(text(f"""
            insert into {table_name} (
                player_id,player_name,nationality,team_id,team_name,position,appearences,goals,assists,penalties,rating
            )
            select
                player_id,player_name,nationality,team_id,team_name,position,appearences,goals,assists,penalties,rating::numeric(4,2)
            from {table_name}_temp
            
            on conflict (player_id) do update set
                goals=excluded.goals,
                assists=excluded.assists,
                appearences=excluded.appearences,
                penalties=excluded.penalties,
                team_name=excluded.team_name
        """))
        conn.commit()
    print(f"upserted {len(df)} players into {table_name}")
        
    
def get_existing_ids():
    #fecth already loaded fixtures ids from postgres
    try:
        with engine.connect() as conn:
            result=conn.execute(text("SELECT fixture_id FROM fact_matches"))
            return set(row[0] for row in result)
    except Exception:
        return set()
        

def parse_fixtures(fixtures):
    
    fact_matches=[]
    dim_teams={}
    dim_leagues={}
    dim_venues={}
    dim_dates=[]
    
    for f in fixtures:
        fixture =f['fixture']
        league=f['league']
        teams=f['teams']
        goals=f['goals']
        score=f['score']
        
        home_goals=goals['home'] if goals['home'] is not None else 0
        away_goals=goals['away'] if goals['away'] is not None else 0
        
        if teams['home']['winner']==True:
            result="H"
        elif teams['away']['winner']==True:
            result="A"
        else:
            result="D"
        
        fact_matches.append({
            "fixture_id":fixture['id'],
            "league_id":league['id'],
            "season":league['season'],
            "round":league['round'],
            "home_team_id":teams['home']['id'],
            "away_team_id":teams['away']['id'],
            "venue_id":fixture['venue']['id'],
            "match_date":fixture['date'],
            "referee":fixture['referee'],
            "home_goals":home_goals,
            "away_goals":away_goals,
            "ht_home_goals":score['halftime']['home'],
            "ht_away_goals":score['halftime']['away'],
            "result":result,
            "status":fixture['status']['short']
        })
        
        for side in ['home','away']:
            team=teams[side]
            dim_teams[team["id"]]={
                "team_id":team["id"],
                "team_name":team["name"]
            }
        dim_leagues[league['id']]={
            "league_id":league['id'],
            "league_name":league['name'],
            "country":league['country'],
            "season":league['season']
        }
        venue=fixture['venue']
        if venue['id']:
            dim_venues[venue['id']]={
                'venue_id':venue['id'],
                'venue_name':venue['name'],
                'city':venue['city']
            }
        
        date=pd.to_datetime(fixture['date'])
        dim_dates.append({
            "fixture_id":fixture['id'],
            "full_date":date.date(),
            "day":date.day,
            "month":date.month,
            "year":date.year,
            "week":date.isocalendar()[1],
            "weekday":date.strftime("%A")
        })
        
    return (
        pd.DataFrame(fact_matches),
        pd.DataFrame(dim_teams.values()),
        pd.DataFrame(dim_leagues.values()),
        pd.DataFrame(dim_venues.values()),
        pd.DataFrame(dim_dates)
    )

def load_incremental_to_postgres(df,table_name,unique_col):
    if df.empty:
        print(f"no new rows for {table_name}")
        return
    try:
        with engine.connect() as conn:
            existing=pd.read.sql(f"SELECT {unique_col} FROM {table_name}",conn)
        existing_ids=set(existing[unique_col].tolist())
    except Exception:
        existing_ids=set()
    new_rows=df[~df[unique_col].isin(existing_ids)]
    
    if new_rows.empty:
        print("no new rows for {table_name} -already up to date")
    else:
        new_rows.to_sql(
            table_name,
            engine,
            schema='public',
            if_exists='append',
            index=False
        )
    print(f"insterted {len(new_rows)} rows into {table_name} ")

if __name__=='__main__':
    print("Fetching fixtures from api...")
    fixtures =fetch_fixtures(league_id=39 , season=2023)
    
    print("checking exisiting data...")
    existing_ids=get_existing_ids()
    print(f"Already loaded: {len(existing_ids)} fixtures")
    
    new_fixtures=[f for f in fixtures if f['fixture']['id'] not in existing_ids]
    print(f"new fixtures to process: {len(new_fixtures)}")
    
    if not new_fixtures:
        print("everything up to date...nothing to load")
    else:
        print("parsing the data ...")
        fact_matches,dim_teams,dim_leagues,dim_venues,dim_dates=parse_fixtures(new_fixtures)
        
        print("loading into postgres...")
        load_incremental_to_postgres(fact_matches,"fact_matches","fixture_id")
        load_incremental_to_postgres(dim_teams,"dim_teams","team_id")
        load_incremental_to_postgres(dim_leagues,"dim_leagues","league_id")
        load_incremental_to_postgres(dim_venues,"dim_venues","venue_id")
        load_incremental_to_postgres(dim_dates,"dim_dates","fixture_id")
    print("fetching player details")
    scorers=fetch_players(league_id=39,season=2023)
    dim_players=parse_players(scorers)
    print(f"total scorers fetched {len(dim_players)}")
    upsert_players(dim_players,"dim_players")
    
    