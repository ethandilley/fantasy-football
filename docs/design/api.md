# API Design

## Core Entities

### Players

No need for manipulating player data.
Only useful for getting information

`/players` - paginated player list (with all info)
`/players/{id}` - bio, position, team, draft
`/players/{id}/stats` - per game stats (filterable by season/week)


### Games

No need for manipulating game data.
Only useful to getting information

`/games` - paginated game list (with all info)
`/games/{id}` - matchup, weather, result
`/games/{id}/players` - all player stats for the game
`/games/{id}/stats` - team level stats

### Datasets

more data grabbing, this time with the ability to download

`/datasets/train` - gives all the data
`/datasets/test` - gives noncausal testing data

### Predictions

will need ability to post predictions and score them

`/predictions/evaluate` - takes in file, stores result, gives submission id
`/predictions/leaderboard` - shows all submissions scores
`/predictions/{submission_id}` - perhaps gives some insight to the submission score

## Pagination

Since the datasets get pretty large, we will require pagination.

I plan to have a ui that shows off some of these tables, page/limit is going to be better than offset/limit.

We dont plan to have too many writes, so cursor is overly complicated.

Response objects should roughly look like so.

```json
{
  "data": [...],
  "meta": { "page": 1, "limit": 50, "total": 4200 }
}
```
