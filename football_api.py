import requests
import psycopg2
import json
import html
import os
import datetime
from predict import *

APIKey = os.environ['FOOTBALL_API_KEY']
url = 'https://apifootball.com/api/?action=get_events&league_id=62'
DATABASE_URL = os.environ['DATABASE_URL']

# cur.execute("CREATE TABLE IF NOT EXISTS matches (match_id INTEGER PRIMARY KEY, match_date DATE, match_status " +
#             "varchar, match_hometeam_name varchar, match_hometeam_score INTEGER, " +
#             "match_awayteam_name varchar, match_awayteam_score INTEGER, " +
#             "data json);")

fields = [
    'match_id',
    'match_date',
    'match_status',
    'match_hometeam_name',
    'match_hometeam_score',
    'match_awayteam_name',
    'match_awayteam_score'
]


def update_computed_table(cur, conn):
    cur.execute("CREATE OR REPLACE VIEW public.home_teams AS "
                "SELECT sub.match_hometeam_name, "
                "count(*) AS matches_played, "
                "sum(sub.match_hometeam_score) AS goals_scored, "
                "ROUND(1.0*sum(sub.match_hometeam_score)/count(*), 3) AS avg_goals_scored, "
                "sum(sub.match_awayteam_score) AS goals_conceded, "
                "ROUND(1.0*sum(sub.match_awayteam_score)/count(*), 3) AS avg_goals_conceded, "
                "sum(sub.home_win) AS home_wins, "
                "ROUND(1.0*sum(sub.home_win)/count(*), 3) AS home_win_p, "
                "sum(sub.home_draw) AS home_draws, "
                "ROUND(1.0*sum(sub.home_draw)/count(*), 3) AS home_draw_p, "
                "sum(sub.home_loss) AS home_losses, "
                "ROUND(1.0*sum(sub.home_loss)/count(*), 3) AS home_loss_p "
                "FROM ( SELECT *, "
                "CASE WHEN matches.match_hometeam_score > matches.match_awayteam_score THEN 1 ELSE 0 END AS home_win, "
                "CASE WHEN matches.match_hometeam_score = matches.match_awayteam_score THEN 1 ELSE 0 END AS home_draw, "
                "CASE WHEN matches.match_hometeam_score < matches.match_awayteam_score THEN 1 ELSE 0 END AS home_loss "
                "FROM matches) AS sub "
                "GROUP BY sub.match_hometeam_name;")
    conn.commit()

    cur.execute("CREATE OR REPLACE VIEW public.away_teams AS "
                "SELECT sub.match_awayteam_name, "
                "count(*) AS matches_played, "
                "sum(sub.match_awayteam_score) AS goals_scored, "
                "ROUND(1.0*sum(sub.match_awayteam_score)/count(*), 3) AS avg_goals_scored, "
                "sum(sub.match_hometeam_score) AS goals_conceded, "
                "ROUND(1.0*sum(sub.match_hometeam_score)/count(*), 3) AS avg_goals_conceded, "
                "sum(sub.away_win) AS away_wins, "
                "ROUND(1.0*sum(sub.away_win)/count(*), 3) AS away_win_p, "
                "sum(sub.away_draw) AS away_draws, "
                "ROUND(1.0*sum(sub.away_draw)/count(*), 3) AS away_draw_p, "
                "sum(sub.away_loss) AS away_losses, "
                "ROUND(1.0*sum(sub.away_loss)/count(*), 3) AS away_loss_p "
                "FROM ( SELECT *, "
                "CASE WHEN matches.match_awayteam_score > matches.match_hometeam_score THEN 1 ELSE 0 END AS away_win, "
                "CASE WHEN matches.match_awayteam_score = matches.match_hometeam_score THEN 1 ELSE 0 END AS away_draw, "
                "CASE WHEN matches.match_awayteam_score < matches.match_hometeam_score THEN 1 ELSE 0 END AS away_loss "
                "FROM matches) AS sub "
                "GROUP BY sub.match_awayteam_name;")
    conn.commit()


def normalize_team_name(team_name):
    # Converting team name here to the team name in the views for computed tables
    correct_name_dict = {
        'Chelsea FC': 'Chelsea',
        'Brighton &amp; Hove Albion': 'Brighton & Hove Albion',
    }
    if team_name in correct_name_dict:
        team_name = correct_name_dict[team_name]
    return team_name


def get_computed_table_row(cur, team_name, is_home):
    table_name = ''
    team_col_name = ''
    if is_home:
        table_name = 'home_teams'
        team_col_name = 'match_hometeam_name'
    else:
        table_name = 'away_teams'
        team_col_name = 'match_awayteam_name'
    team_name = normalize_team_name(team_name)
    cur.execute("SELECT * FROM " + table_name + " WHERE " + team_col_name + "='" + team_name + "'")
    team_stats = cur.fetchall()
    if len(team_stats) < 1:
        print('WARNING this should not happen!!')
        return [0] * 23
    return team_stats[0]


def update_matches_table(start_date, end_date):
    print('start')
    from_string = '&from=' + start_date
    to_string = '&to=' + end_date
    api_string = '&APIkey=' + APIKey
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    # TODO populate with 2015-09-01 to 2018-07-31, or switch to new
    r = requests.get(url + from_string + to_string + api_string, timeout=(60 * 10))
    s = json.dumps(r.json())
    h = html.unescape(s)
    h1 = h.replace(" FC", "")
    json_data = json.loads(h1)
    # conn = psycopg2.connect(dbname="Sportswizz", user="postgres", password="1qaz2wsx")
    # print(json_data)
    bad_request = False
    for item in json_data:
        # sometimes there's a bug where game is not updated yet and it's just an empty string
        if isinstance(item, str):
            print("item is a string, error")
            print(item)
            print(json_data)
            bad_request = True
            break
        if not item['match_hometeam_score'] or item['match_hometeam_score'] == '?':
            continue
        temp = [item[field] for field in fields]
        # stats = item["statistics"]
        # for i in stats:
        #     home = i["home"]
        #     away = i["away"]
        #     temp.append(home)
        #     temp.append(away)
        temp.append(json.dumps(item))
        cur.execute("INSERT INTO matches VALUES (%S, %S, %S, %S, %S, %S, %S, %S) ON CONFLICT DO NOTHING", tuple(temp))
        conn.commit()
    if not bad_request:
        update_computed_table(cur, conn)
    conn.close()
    print("done")


def get_matches_within(start_date, end_date):
    from_string = '&from=' + start_date
    to_string = '&to=' + end_date
    api_string = '&APIkey=' + APIKey
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    r = requests.get(url + from_string + to_string + api_string, timeout=(60 * 10))
    s = json.dumps(r.json())
    home_comps = html.unescape(s)
    h1 = home_comps.replace(" FC", "")
    json_data = json.loads(h1)
    bad_request = False
    """
    future_predictions is an array of dicts.
    each dict has keys home (name), away, date, home_win_prob, draw_prob, away_win_prob, home_score, away_score
    """
    future_predictions = []
    for item in json_data:
        # sometimes there's a bug where game is not updated yet and it's just an empty string
        if isinstance(item, str):
            bad_request = True
            break
        # we only want games that haven't started yet
        if item['match_hometeam_score'] and item['match_hometeam_score'] != '?':
            continue
        temp = [item[field] for field in fields]
        temp.append(json.dumps(item))
        match_id = item['match_id']
        one_week_ago = datetime.datetime.now() + datetime.timedelta(days=-7)
        one_week_ago = one_week_ago.strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM predictions WHERE last_updated >= '" + one_week_ago +
                    "' AND match_id=" + str(match_id) + ";")
        """
        Order of row data in predictions table:
        0 prediction_id, 1 pred_home_score, 2 pred_away_score, 3 pred_home_win_percent, 4 pred_away_win_percent,
        5 pred_draw_percent, 6 home_name, 7 away_name, 8 match_date, 9 match_id
        """
        matches = cur.fetchall()
        if len(matches) < 1:
            # match doesn't have a prediction, so generate one
            home_name = normalize_team_name(item['match_hometeam_name'])
            away_name = normalize_team_name(item['match_awayteam_name'])
            """
            TABLE home_teams
            0 match_hometeam_name, 1 matches_played, 2 goals_scored, 3 avg_goals_scored, 4 goals_conceded, 
            5 avg_goals_conceded, 6 home_wins, 7 home_win_p, 8 home_draws, 9 home_draw_p, 10 home_losses, 11 home_loss_p
            TABLE away_teams
            (same as above but replace "home" with "away" everywhere it's mentioned
            """
            # home_computed_vals
            home_comps = get_computed_table_row(cur, home_name, True)
            away_comps = get_computed_table_row(cur, away_name, False)

            stats = create_training_array(.5, .3, .2, home_comps[7], home_comps[9], home_comps[11], away_comps[7],
                                          away_comps[9], away_comps[11], .5, .3, .2, .5, .3, .2, home_comps[3],
                                          away_comps[3], home_comps[4], away_comps[4], 1, 1, 1, 1)
            # TODO adjust once Victor responds
            # home_goals_pred = get_score_pred(stats, True)
            # away_goals_pred = get_score_pred(stats, False)
            home_goals_pred = 1
            away_goals_pred = 0

            win_loss_draw = get_win_draw_loss_probs(stats)[0]
            home_win_prob = win_loss_draw[2]
            draw_prob = win_loss_draw[1]
            away_win_prob = win_loss_draw[0]
            # See prediction table for what each item in pred_stats represents
            print(item['match_hometeam_name'])
            print(item['match_awayteam_name'])
            print(datetime.datetime.now().strftime("%Y-%m-%d"))
            print(match_id)
            # pred_stats = [match_id, home_goals_pred, away_goals_pred, home_win_prob, away_win_prob, draw_prob,
            #               item['match_hometeam_name'], item['match_awayteam_name'], item['match_date'], match_id,
            #               datetime.datetime.now().strftime("%Y-%m-%d")]
            pred_stats = [match_id, home_goals_pred, away_goals_pred, home_win_prob, away_win_prob, draw_prob,
                          item['match_hometeam_name'], item['match_awayteam_name'], item['match_date'], match_id,
                          datetime.datetime.now().strftime("%Y-%m-%d")]
            match_data = {
                'home': pred_stats[6],
                'away': pred_stats[7],
                'date': pred_stats[8],
                'home_win_prob': pred_stats[3],
                'draw_prob': pred_stats[5],
                'away_win_prob': pred_stats[4],
                'home_score': pred_stats[1],
                'away_score': pred_stats[2]
            }
            future_predictions.append(match_data)
            cur.execute("INSERT INTO predictions VALUES (" + pred_stats[0] +
                        "," + str(pred_stats[1]) + "," + str(pred_stats[2]) + "," + str(pred_stats[3]) + "," + str(pred_stats[4]) + ","
                        + str(pred_stats[5]) + ",'" + str(pred_stats[6]) + "','" + str(pred_stats[7]) + "','" + str(pred_stats[8]) + "',"
                        + str(pred_stats[9]) + ",'" + str(pred_stats[10]) + "') ON CONFLICT (prediction_id) "
                        "DO UPDATE SET "
                        + "last_updated='" + str(pred_stats[10]) + "',pred_home_score=" + str(pred_stats[1]) +
                        ",pred_away_score="
                        + str(pred_stats[2]) + ",pred_home_win_percent=" + str(pred_stats[3]) + ",pred_away_win_percent="
                        + str(pred_stats[4]) + ",pred_draw_percent=" + str(pred_stats[5]) + ";")
            conn.commit()
            # TODO remove below
            # break
        else:
            print('already exists')
            match = matches[0]
            print(match)
            # match has a prediction, so return it
            match_data = {
                'home': match[6],
                'away': match[7],
                'date': match[8].strftime("%Y-%m-%d"),
                'home_win_prob': match[3],
                'draw_prob': match[5],
                'away_win_prob': match[4],
                'home_score': match[1],
                'away_score': match[2]
            }
            future_predictions.append(match_data)
    print("done")
    conn.close()
    return future_predictions
