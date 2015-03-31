from flask import render_template, flash, redirect, url_for
import vincent

from app import app
from data import *

database = Data()

### Vincent Data Routes

WIDTH = 400
HEIGHT = 200

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
                            title='Home')

@app.route('/teams')
@app.route('/teams/<season>')
def teams(season=2015):
    k = 100
    df = database.top_teams(season, k)
    return render_template('teams.html',
                            title='Teams',
                            k=k,
                            season=season,
                            data=df)

@app.route('/games')
def games():
    return render_template('games.html',
                            title='Games')

@app.route('/team/<teamname>')
@app.route('/team')
def team(teamname='Stanford'):
    team = database.find_team_id(teamname)
    if team:
        team_id = team[0]
        name = team[1]

        df = database.team_stats(team_id)

        return render_template('team.html',
                            title='{} Team Stats'.format(name),
                            team_name=name,
                            team_id=team_id,
                            data=df)

    flash('Team name {} not found'.format(teamname))
    return redirect('/index')

@app.route('/game/<team_1>/<team_2>/<season>')
@app.route('/game/<team_1>/<team_2>/')
@app.route('/game')
def game(team_1='Stanford', team_2='California', season=None):
    teama = database.find_team_id(team_1)
    teamb = database.find_team_id(team_2)

    if teama and teamb:
        df = database.find_games(teama[0], teamb[0], season)
        if len(df) > 0:
            return render_template('game.html',
                            title='{} vs {}'.format(teama[1], teamb[1]),
                            team_1 = teama[1],
                            team_2 = teamb[1],
                            season=season,
                            data=df)
        else:
            flash('No games found'.format(team_2))
            return redirect('/games')
    elif teama:
        flash('Team name {} not found'.format(team_2))
        return redirect('/games')
    else:
        flash('Team name {} not found'.format(team_1))
        return redirect('/games')

@app.route('/predict/<team_1>/<team_2>/<season>')
@app.route('/predict/<team_1>/<team_2>/')
def predict(team_1, team_2, season=2015):
    teama = database.find_team_id(team_1)
    teamb = database.find_team_id(team_2)

    if teama and teamb:
        prediction = database.predict(teama[0], teamb[0], int(season))
        return render_template('predict.html',
                        title='{} vs {}'.format(teama[1], teamb[1]),
                        team_1 = teama[1],
                        team_2 = teamb[1],
                        season=season,
                        prediction=prediction,
                        prediction2=100-prediction)

    elif teama:
        flash('Team name {} not found'.format(team_2))
        return redirect('/games')
    else:
        flash('Team name {} not found'.format(team_1))
        return redirect('/games')

### Vincent plots

@app.route('/data/pagerank/<team_id>')
def pagerankplot(team_id):
    df = database.team_stats(team_id)
    # df.index = df.season

    p = vincent.Line(df.winrank, width=WIDTH, height=HEIGHT)
    p.axis_titles(x='Season', y='Winrank')

    return p.to_json()
