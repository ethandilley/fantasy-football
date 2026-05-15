# Fantasy Football

A dataplatform for fantasy football.

## Architecture

- mediallion data architecture
    - store bronze data in [minio](https://github.com/minio/minio)
    - store silver and gold data in [clickhouse](https://github.com/clickhouse/clickhouse)
- schedule jobs using [airflow](https://github.com/apache/airflow)
- serve data and score predictions on api built on [fastapi](https://github.com/fastapi/fastapi)
- orchestrate using [k3s](https://github.com/k3s-io/k3s/)
- running on bare metal
    - stone (control-plane) node: mac m2 air, 8 core, 8gb ram, 512gb ssd
    - dilley (weak, edge) node: raspberry pi 4 model B, 4 core, 8gb ram, 1TB external ssd
    - ethan (strong, intermittent, edge) node: pc build, 8 core, 32gb ram, 1TB ssd, 5070ti gpu
- basic api found [dilleystone.com](http://dilleystone.com) 

## Details

### Minio

Minio is essentially open source s3. It is utilized in the bronze layer of the data platform.

I chose Minio because I needed a platform to store raw files. The default here is s3, but Minio is free.

#### Purpose 

The purpose of a bronze layer is to store raw data in its original format and maintain history.
If espn were to go down or completely change its api, we would still have our own data to run pipelines off of.

#### Usage

To standup minio, you can use the image minio/minio. It comes with two ports 
- 9000, the s3 api that clients interact with
- 9001, the ui

For the purposes of this project, we utilize a single bucket called `bronze`.
The pattern within the bucket is ever evolving, but generally.

```bash
data source
└── raw
    ├── restful object
    │   └── ...
    └── misc
```

An example looks like
Note: season and week refer to nfl season/week and date refers to run date.

```bash
bronze
└── raw
    ├── events
    │   └── season=1999
    │       ├── week=1
    │       │   └── data.json.gz
    │       └── week=2
    │           └── data.json.gz
    ├── players
    │   └── date=2026-04-15
    │       └── players
    │           └── page=0
    │               └── data.json.gz
    │           └── page=1
    │               └── data.json.gz
    ├── stats
    │   └── ...
    └── teams
        └── ...
```

I may update this, but for the time being it feels memorable and extensible enough.

### Clickhouse

Clickhouse is an open source OLAP DBMS. It is utilized in the silver and gold layers of the data platform.

I chose Clickhouse because the nature of the data is a vast amount of historical data which will be queried for analytics, so OLAP makes sense.

#### Purpose

The silver layer takes raw, unstructured, bronze data and standardizes, normalizes, and cleans it.
The gold layer takes the standardized, structured silver data, and aggregates it.
Clickhouse maintains all of our standardized and structured data from silver to gold layers.
Models are trained on data from the gold layer.

#### Usage

To stand up clickhouse, you can use the `clickhouse/clickhouse-server` image. It also comes with two ports
- 8123, the http interface that the python client uses
- 9000, the native interface that the cli uses

For this project, I utilize two databases in clickhouse `silver` and `gold`
The silver layer maintains the poorly named tables
- games, raw game data (season/week/weather/teams)
- playergamestats, player game stats (yards, touchdowns)
- players, player data (age, weight, height, draft pick)
- teamgamestats, team game stats (team yards, team touchdowns, 3rd down conversion rate)
- teams, team data (32 rows of each team)

The gold layer maintains
- playergame, an aggregate of all tables above
- playergame_features, adding some basic features for training on top of player game

### Service

The service (to be named) utilizes the gold layer and offers 3 endpoints

- get training data
- get testing data (no causal information)
- evaluate model predictions

I used fastapi, but hope to soon rewrite this in rust.

It is currently dumb simple with only one router, but I hope to add functionality soon (airflow interactions).



### Airflow

Airflow is an open source workflow orchestrator. It is utilized to run the tasks that move data from apis to bronze/silver/gold layers.

I chose Airflow because I am familiar and I know it can handle the job - although perhaps it is a bit to beefy for the things I use it for.

#### Usage

The dags are split into their bronze/silver/gold portions, all are named similarly to the table they populate.

Bronze Dags:
- players
- teams
- games

Silver Dags:
- games
- players
- teams
- player_games
- team_games

Gold Dags:
- player_games

### k3s

k3s is a lightweight kubernetes installation.

I chose k3s because I am running the project locally (on my own devices) and they are quite weak (ram limited).
k3s is a lightweight self-hosting k8s solution that can fit even on my PI.

Currently, the only way in which I interact with k3s is within the /infra directory where there are some ugly written yamls.
It works for now, but needs some makeup (better deployment/cleaner yamls/more helm)

As mentioned, I am self-hosting all of this on my own devices. That consists of 3 nodes

- my pc (ethan)
    - 7800x3d (8 core)
    - 32gb ram
    - 5070ti (16vram)
    - 1tb ssd
- my m2 macbook air (stone)
    - m2 chip (8 core)
    - 8gb ram
    - 512 ssd
- my raspberry pi 4 model b
    - 4 core cpu
    - 8gb ram
    - 1tb ssd (crucial pro)

I wish to soon add a mac mini from @eming (8gb ram, m1 chip, 256 ram)


## Goals

- learn rust
- build a data platform e2e
- win fantasy

## Next Steps

**tasks**
- write readme
- clean up api
- do some modeling myself
- rearchitect dags to be more efficient
- rewalk through airflow setup
- add some security (tls + passwords not in plain text)
- add some backfill endpoints and tables (perhaps postgres?)

**issues**
- backfills suck
- api sucks
- k3s is messy
- passwords are in plaintext
