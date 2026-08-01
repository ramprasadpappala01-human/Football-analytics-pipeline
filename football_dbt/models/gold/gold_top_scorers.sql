with ranked_players as (
    select player_id,player_name,nationality,team_name,position,appearences,goals,assists,penalties,goals_per_game,assists_per_game,
    rank() over(order by goals desc) as goals_rank
    from {{ ref('silver_players') }}
)
select * from ranked_players
where goals_rank<=20
order by goals_rank
