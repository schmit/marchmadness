from sqlalchemy import create_engine

import numpy as np
import pandas as pd

def logistic(x):
    return 1.0/(1.0+np.exp(-x))

class Data:
    def __init__(self):
        self.engine = create_engine('sqlite:///app.db')

    def query(self, query):
        return pd.io.sql.read_sql(query, self.engine)

    def find_team_id(self, team_name):
        q = '''
        SELECT id, team_name FROM team WHERE team_name LIKE '{}%';
        '''.format(team_name)
        df = self.query(q)
        if len(df) == 0:
            return
        return df.id[0], df.team_name[0]

    def team_stats(self, team_id):
        q = '''
        SELECT season, wins, ngames, winrank, teamrank AS rank, luck
        FROM team_stats
        WHERE team_id = {}
        '''.format(team_id)
        return self.query(q)

    def top_teams(self, season, k=25):
        q = '''
        SELECT
            team_stats.teamrank as rank,
            team.team_name as team,
            team_stats.wins,
            team_stats.ngames,
            team_stats.winrank,
            team_stats.luck
        FROM team_stats
        JOIN team on team.id = team_stats.team_id
        WHERE season = {}
        AND team_stats.teamrank <= {}
        ORDER BY team_stats.teamrank ASC
        '''.format(season, k)
        return self.query(q)

    def find_games(self, team_1, team_2, season=None):
        if season:
            q = '''
            SELECT
                daynum AS day,
                t1.team_name AS winner,
                wscore AS wpoints,
                lscore as lpoints,
                t2.team_name AS loser,
                wloc AS location
            FROM games
            JOIN team t1 ON t1.id = wteam
            JOIN team t2 ON t2.id = lteam
            WHERE ((wteam = {0} AND lteam = {1}) OR (wteam = {1} AND lteam = {0}))
            AND season = {2}
            ORDER BY daynum DESC
            '''.format(team_1, team_2, season)
        else:
            q = '''
            SELECT
                season,
                daynum AS day,
                t1.team_name AS winner,
                wscore AS wpoints,
                lscore AS lpoints,
                t2.team_name AS loser,
                wloc as location
            FROM games
            JOIN team t1 ON t1.id = wteam
            JOIN team t2 ON t2.id = lteam
            WHERE (wteam = {0} AND lteam = {1}) OR (wteam = {1} AND lteam = {0})
            ORDER BY season DESC, daynum DESC
            '''.format(team_1, team_2)
        df = self.query(q)
        return df

    def predict(self, team_1, team_2, season=2015):
        # get team statistics
        t1_stats = self.team_stats(team_1)
        t2_stats = self.team_stats(team_2)

        XB = 0
        # extract pagerank scores
        t1_pr = float(t1_stats[t1_stats.season == season].winrank)
        t2_pr = float(t2_stats[t2_stats.season == season].winrank)
        coef_pr = 0.1056
        XB += coef_pr * (t1_pr - t2_pr)

        # extract luck
        t1_luck = float(t1_stats[t1_stats.season == season].luck)
        t2_luck = float(t2_stats[t2_stats.season == season].luck)
        coef_pr = -0.0072
        XB += coef_pr * (t1_luck - t2_luck)

        return round(logistic(XB),4)*100

