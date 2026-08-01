select m.fixture_id,d.full_date,m.home_team_id ,th.team_name as home_team,m.away_team_id,ta.team_name as away_team ,m.home_goals , m.away_goals,
case
when m.result='A' then ta.team_name ||' Win'
when m.result='H' then th.team_name ||' Win'
else 'Draw'
end as results,
case 
when m.home_goals+m.away_goals>=3 then 'High Scoring'
else 'Low Scoring'
end as goal_category,
l.league_name,v.venue_name,v.city,l.country
from {{ref('bronze_fact_matches')}} as m
left join {{ ref('bronze_dim_dates') }}as d
on m.fixture_id=d.fixture_id
left join {{ ref('bronze_dim_leagues') }} as l
on m.league_id =l.league_id
left join  {{ ref('bronze_dim_venues') }} as v
on m.venue_id = v.venue_id
left join {{ ref('bronze_dim_teams') }}as th
on m.home_team_id = th.team_id
left join {{ ref('bronze_dim_teams') }}as ta
on m.away_team_id = ta.team_id