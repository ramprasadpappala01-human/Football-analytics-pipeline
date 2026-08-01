select team_id, team , count(*) as played ,
sum(case when result='W'then 1 else 0 end) as Wins,
sum(case when result='L'then 1 else 0 end) as losses,
sum(case when result='D'then 1 else 0 end) as Draws,
sum(goals_for) as goals_for,
sum(goals_against) as goals_againts,
sum(goals_for) - sum(goals_against) as goal_difference,
sum(case when result='W' then 3
    when result='D' then 1 else 0 end) as points 
from(select home_team_id as team_id,home_team as team, home_goals as goals_for ,away_goals as goals_against,
case 
when home_goals>away_goals then 'W'
when home_goals=away_goals then 'D'
else 'L'
end as result
from {{ ref('silver_matches') }}
union all
select away_team_id as team_id ,away_team as team , away_goals as goals_for , home_goals as goals_against,
case
when away_goals>home_goals then 'W'
when away_goals=home_goals then 'D'
else 'L'
end as result
from {{ ref('silver_matches') }}
) as team_results
group by team_id,team
order by points DESC, goal_difference DESC