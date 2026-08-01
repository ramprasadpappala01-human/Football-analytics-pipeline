with team_stats as(
    select team_id , team,count(*) as Played,
    sum(case when result='W' then 1 else 0 end) as Wins,
    sum(case when result='L' then 1 else 0 end) as Losses,
    sum(case when result='D' then 1 else 0 end) as Draws,
    round(sum(case when result='W' then 1 else 0 end )*100.0/count(*),2) as win_rate_prcnt,
    round(avg(goals_for),2) as avg_goals_for,
    round(avg(goals_against),2) as avg_goals_against,
    sum(goals_for) as total_goals_scored,
    sum(goals_against) as total_goals_conceeded
    from(
        select home_team_id as team_id , home_team as team , home_goals as goals_for , away_goals as goals_against,
        case
        when home_goals>away_goals then 'W'
        when home_goals=away_goals then 'D'
        else 'L' 
        end as result
        from {{ ref('silver_matches') }}
        union all
        select away_team_id as team_id, away_team as team , away_goals as goals_for , home_goals as goals_against,
        case
        when away_goals>home_goals then 'W'
        when away_goals=home_goals then 'D'
        else 'L'
        end as result
        from {{ ref('silver_matches') }}
        )as team_results
        group by team_id,team
)
select * from team_stats
order by (wins * 3 + draws)DESC, (total_goals_scored - total_goals_conceeded) DESC