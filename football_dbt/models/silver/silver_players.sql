select
p.player_id,p.player_name,p.nationality,p.team_name,p.team_id,p.position,p.appearences,p.goals,p.assists,p.penalties,p.rating,
round(p.goals*1.0/ nullif(p.appearences,0),2) as goals_per_game,
round(p.assists*1.0/ nullif(p.appearences,0),2) as assists_per_game
from {{ ref('bronze_dim_players') }} as p