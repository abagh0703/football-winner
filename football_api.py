import requests
import psycopg2
import json
import html
import os
import datetime
from predict import *
from psycopg2.extras import Json

APIKey = os.environ['FOOTBALL_API_KEY']
betting_url = 'https://apifootball.com/api/?action=get_odds&league_id=62'
url = 'https://apifootball.com/api/?action=get_events&league_id=62'
DATABASE_URL = os.environ['DATABASE_URL']
API_STRING = '&APIkey=' + APIKey
MINUTES_TO_WAIT = 3

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


def compute_l20_stats_in_dict(stats_dict):
    for team in stats_dict:
        team_name = team
        team = stats_dict[team]
        wins = team['wins']
        losses = team['losses']
        draws = team['draws']
        goals = team['goals']
        conc = team['conc']
        num_games = team['num_games']
        # we would get div by 0 err for next part otherwise
        if num_games < 1:
            team['l20_win_p'] = 0
            team['l20_draw_p'] = 0
            team['l20_loss_p'] = 0
            team['l20_avg_goals'] = 0
            team['l20_avg_conc'] = 0
            continue
        sig_figs = 3
        team['l20_win_p'] = round(wins / num_games, sig_figs)
        team['l20_draw_p'] = round(draws / num_games, sig_figs)
        team['l20_loss_p'] = round(losses / num_games, sig_figs)
        team['l20_avg_goals'] = round(goals / num_games, sig_figs)
        team['l20_avg_conc'] = round(conc / num_games, sig_figs)
        stats_dict[team_name] = team
    return stats_dict


def get_stats_from_matches(team_name, team_dict, home_goals, away_goals):
    if team_dict.get(team_name) is None:
        team_dict[team_name] = {
            'num_games': 0,
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'goals': 0,
            'conc': 0
        }
    current_stats = team_dict[team_name]
    if current_stats['num_games'] > 20:
        return team_dict
    current_stats['num_games'] += 1
    current_stats['goals'] += home_goals
    current_stats['conc'] += away_goals
    if home_goals > away_goals:
        current_stats['wins'] += 1
    elif away_goals > home_goals:
        current_stats['losses'] += 1
    else:
        current_stats['draws'] += 1
    team_dict[team_name] = current_stats
    return team_dict


def insert_l20_into_table(cur, conn, table_name, team_name_col, team_name, team_stats):
    stats = team_stats[team_name]
    # print(stats)
    cur.execute('UPDATE ' + table_name
                + ' SET '
                  'l20_win_p=' + str(stats['l20_win_p'])
                + ', l20_loss_p=' + str(stats['l20_loss_p'])
                + ', l20_draw_p=' + str(stats['l20_draw_p'])
                + ', l20_avg_goals=' + str(stats['l20_avg_goals'])
                + ', l20_avg_conc=' + str(stats['l20_avg_conc'])
                + ' WHERE ' + team_name_col + '=\'' + team_name
                + '\';')
    conn.commit()


def update_l20(cur, conn):
    cur.execute("SELECT * FROM matches ORDER BY match_date LIMIT 300")
    matches = cur.fetchall()
    """
    each item in the dict is a dict with key team name with a value of another dict
    {
        num_games: <=20,
        wins: ,
        losses: ,
        draws: ,
        goals: ,
        conc: ,
        l20_win_p: ,
        l20_draw_p: ,
        l20_loss_p: ,
        l20_avg_goals: ,
        l20_avg_conc: ,
    }
    """
    home_stats_dict = {}
    away_stats_dict = {}
    for match in matches:
        home_team_name = match[3]
        away_team_name = match[5]
        home_goals = match[4]
        away_goals = match[6]
        home_stats_dict = get_stats_from_matches(home_team_name, home_stats_dict, home_goals, away_goals)
        away_stats_dict = get_stats_from_matches(away_team_name, away_stats_dict, away_goals, home_goals)
    home_stats_dict = compute_l20_stats_in_dict(home_stats_dict)
    away_stats_dict = compute_l20_stats_in_dict(away_stats_dict)
    home_table_name = 'home_teams_comp'
    away_table_name = 'away_teams_comp'
    home_team_name_col = 'match_hometeam_name'
    away_team_name_col = 'match_awayteam_name'
    for team in home_stats_dict:
        insert_l20_into_table(cur, conn, home_table_name, home_team_name_col, team, home_stats_dict)
    for team in away_stats_dict:
        insert_l20_into_table(cur, conn, away_table_name, away_team_name_col, team, away_stats_dict)


def update_computed_table(cur, conn):
    cur.execute("DROP TABLE public.home_teams_comp")
    cur.execute("DROP TABLE public.away_teams_comp")
    cur.execute("CREATE TABLE public.home_teams_comp AS "
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
                "ROUND(1.0*sum(sub.home_loss)/count(*), 3) AS home_loss_p, "
                "0.0 AS l20_win_p, "
                "0.0 AS l20_loss_p, "
                "0.0 AS l20_draw_p, "
                "0.0 AS l20_avg_goals, "
                "0.0 AS l20_avg_conc "
                "FROM ( SELECT *, "
                "CASE WHEN matches.match_hometeam_score > matches.match_awayteam_score THEN 1 ELSE 0 END AS home_win, "
                "CASE WHEN matches.match_hometeam_score = matches.match_awayteam_score THEN 1 ELSE 0 END AS home_draw, "
                "CASE WHEN matches.match_hometeam_score < matches.match_awayteam_score THEN 1 ELSE 0 END AS home_loss "
                "FROM matches) AS sub "
                "GROUP BY sub.match_hometeam_name;")

    cur.execute("CREATE TABLE public.away_teams_comp AS "
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
                "ROUND(1.0*sum(sub.away_loss)/count(*), 3) AS away_loss_p, "
                "0.0 AS l20_win_p, "
                "0.0 AS l20_loss_p, "
                "0.0 AS l20_draw_p, "
                "0.0 AS l20_avg_goals, "
                "0.0 AS l20_avg_conc "
                "FROM ( SELECT *, "
                "CASE WHEN matches.match_awayteam_score > matches.match_hometeam_score THEN 1 ELSE 0 END AS away_win, "
                "CASE WHEN matches.match_awayteam_score = matches.match_hometeam_score THEN 1 ELSE 0 END AS away_draw, "
                "CASE WHEN matches.match_awayteam_score < matches.match_hometeam_score THEN 1 ELSE 0 END AS away_loss "
                "FROM matches) AS sub "
                "GROUP BY sub.match_awayteam_name;")
    conn.commit()
    update_l20(cur, conn)


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
        table_name = 'home_teams_comp'
        team_col_name = 'match_hometeam_name'
    else:
        table_name = 'away_teams_comp'
        team_col_name = 'match_awayteam_name'
    team_name = normalize_team_name(team_name)
    cur.execute("SELECT * FROM " + table_name + " WHERE " + team_col_name + "='" + team_name + "'")
    team_stats = cur.fetchall()
    if len(team_stats) < 1:
        print('WARNING this should not happen!!')
        return [0] * 23
    return team_stats[0]


# Source: https://www.bettingexpert.com/academy/betting-fundamentals/betting-odds-explained
def convert_odd_to_prob(odd):
    # they're like 1.88 right now, have to be 188
    # odd *= 100
    # if odd < 0:
    #     return -odd / (-odd + 100)
    # else:
    #     return 100 / (odd + 100)
    if odd <= 0:
        return .333
    return 1 / odd


def calc_weighted_average(first_val, first_occur, second_val, second_occur):
    return (first_val * first_occur + second_val * second_occur) / (first_occur + second_occur)


def get_betting_odds(start_interval, end_interval):
    print('in betting odds method')
    from_string = '&from=' + start_interval.strftime('%Y-%m-%d')
    to_string = '&to=' + end_interval.strftime('%Y-%m-%d')
    r = requests.get(betting_url + from_string + to_string + API_STRING, timeout=(60 * MINUTES_TO_WAIT))
    print('finished request')
    if not r.ok:
        print('odds error: ' + r.status_code)
        return {}
    print('its ok')
    s = json.dumps(r.json())
    print('json dump')
    h = html.unescape(s)
    h1 = h.replace(" FC", "")
    print('about to load')
    raw_odds = json.loads(h1)
    print('loaded')
    """ match id (string) key
        {
        '26631' : 
            { 'home_win_prob': 1/odds,
            'draw_prob': 1/odds,
            'away_win_prob': 1/odds,
            'bets': 0
            },
        '41532': ...,
    """
    avg_odds = {}
    for odd in raw_odds:
        if isinstance(odd, str):
            print("odd is a string, error")
            print(raw_odds)
            print(end_interval)
            break
        match_id = odd['match_id']
        if match_id is None:
            continue
        if match_id not in avg_odds:
            avg_odds[match_id] = {'home_win_prob': .33, 'draw_prob': .33, 'away_win_prob': .33, 'bets': 0}
        # I know 1 is supposed to be away team win, but this api seems to have mixed them up (or my source is wrong)
        home_team_win = odd['odd_1']
        away_team_win = odd['odd_2']
        draw_odd = odd['odd_x']
        if away_team_win is None or home_team_win is None or draw_odd is None:
            continue
        away_win_prob = convert_odd_to_prob(float(away_team_win))
        home_win_prob = convert_odd_to_prob(float(home_team_win))
        draw_prob = convert_odd_to_prob(float(draw_odd))
        current_match_odds = avg_odds[match_id]
        num_bets = current_match_odds['bets']
        avg_odds[match_id] = {
            'home_win_prob': calc_weighted_average(home_win_prob, 1, current_match_odds['home_win_prob'], num_bets),
            'away_win_prob': calc_weighted_average(away_win_prob, 1, current_match_odds['away_win_prob'], num_bets),
            'draw_prob': calc_weighted_average(draw_prob, 1, current_match_odds['draw_prob'], num_bets),
            'bets': num_bets + 1
        }
    print('finishes parsing odds and added to list')
    return avg_odds


def update_matches_table(start_date, end_date):
    print('start')
    from_string = '&from=' + start_date
    to_string = '&to=' + end_date
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print('connected to database')
    cur = conn.cursor()
    print('got cursor')
    r = requests.get(url + from_string + to_string + API_STRING, timeout=(60 * MINUTES_TO_WAIT))
    print('made request')
    s = json.dumps(r.json())
    print('json dump')
    h = html.unescape(s)
    print('unescape')
    h1 = h.replace(" FC", "")
    print('replace')
    json_data = json.loads(h1)
    print('json load')
    # conn = psycopg2.connect(dbname="Sportswizz", user="postgres", password="1qaz2wsx")
    bad_request = False
    start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start_interval = start_date_obj
    end_interval = start_date_obj + datetime.timedelta(days=5)
    print('about to get betting odds')
    betting_data = get_betting_odds(start_interval, end_interval)
    print('got betting odds first time')
    start_interval = end_interval + datetime.timedelta(days=1)
    end_interval = start_interval + datetime.timedelta(days=5)
    while end_date_obj > start_interval:
        print('running betting loop')
        betting_data = {**betting_data, **(get_betting_odds(start_interval, end_interval))}
        print('got betting odds again')
        start_interval = end_interval + datetime.timedelta(days=1)
        end_interval = start_interval + datetime.timedelta(days=5)
        print("next: ")
        print(end_interval)
    for item in json_data:
        # sometimes there's a bug where game is not updated yet and it's just an empty string
        if isinstance(item, str):
            print("item is a string, error")
            print(item)
            print(json_data)
            bad_request = True
            break
        # if not item['match_hometeam_/score'] or item['match_hometeam_score'] == '?' or item['match_status'] != 'FT':
        #     continue
        temp = [item[field] for field in fields]
        temp = ['0'] * 8
        count = 0
        for field in fields:
            if field in item and (item[field] or item[field] == 0):
                temp[count] = item.get(field)
            count += 1
        # storing json is tricky, not sure how to do it with psycopg, so just store nothing
        # temp += ('depr',)
        temp[7] = 'depr'
        match_stats = item.get('statistics')
        home_shots = 0
        away_shots = 0
        home_off = 0
        away_off = 0
        home_poss = 0
        away_poss = 0
        home_corners = 0
        away_corners = 0
        home_fouls = 0
        away_fouls = 0
        home_goal_kicks = 0
        away_goal_kicks = 0
        if match_stats is not None:
            for stat in match_stats:
                stat_type = stat['type']
                if stat_type == 'shots on target':
                    home_shots = stat['home']
                    away_shots = stat['away']
                elif stat_type == 'shots off target':
                    home_off = stat['home']
                    away_off = stat['away']
                elif stat_type == 'possession (%)':
                    home_poss = stat['home']
                    away_poss = stat['away']
                elif stat_type == 'corners':
                    home_corners = stat['home']
                    away_corners = stat['away']
                elif stat_type == 'fouls':
                    home_fouls = stat['home']
                    away_fouls = stat['away']
                elif stat_type == 'goal kicks':
                    home_goal_kicks = stat['home']
                    away_goal_kicks = stat['away']
        current_odds = betting_data.get(str(temp[0]))
        print(current_odds)
        if current_odds is None:
            home_win_prob = .333
            away_win_prob = .333
            draw_prob = .333
        else:
            home_win_prob = current_odds['home_win_prob']
            away_win_prob = current_odds['away_win_prob']
            draw_prob = current_odds['draw_prob']
        # for each match, use betting odds dict to get betting data
        # if it doesn't exist use default
        # add it to the cur.execute part, making sure to str()
        #
        """
        TABLE matches: 0 match_id, 1 match_date, 2 match_status, 3 match_hometeam_name, 4 match_hometeam_score, 
        5 match_awayteam_name, 6 match_awayteam_score, 7 data, 8 home_win_prob, 9 draw_prob, 
        10-11 _shots, 12-13 _off, 14-15 _poss, 16-17 _corners, 18-19 _fouls, 20-21 goal_kicks, 22 away_win_prob
        """
        cur.execute("INSERT INTO matches VALUES ("
                    + temp[0] + ",'"
                    + temp[1] + "', '"
                    + temp[2] + "', '"
                    + temp[3] + "', "
                    + temp[4] + ", '"
                    + temp[5] + "', "
                    + temp[6] + ", '"
                    + temp[7] + "', "
                    + str(home_win_prob) + ", "
                    + str(draw_prob) + ", "
                    + str(home_shots) + ", "
                    + str(away_shots) + ", "
                    + str(home_off) + ", "
                    + str(away_off) + ", "
                    + str(home_poss) + ", "
                    + str(away_poss) + ", "
                    + str(home_corners) + ", "
                    + str(away_corners) + ", "
                    + str(home_fouls) + ", "
                    + str(away_fouls) + ", "
                    + str(home_goal_kicks) + ", "
                    + str(away_goal_kicks) + ", "
                    + str(away_win_prob)
                    + ") ON CONFLICT (match_id) DO UPDATE SET " +
                    "match_id=" + temp[0]
                    + ", match_date='" + temp[1]
                    + "', match_status='" + temp[2]
                    + "', match_hometeam_name='" + temp[3]
                    + "', match_hometeam_score=" + temp[4]
                    + ", match_awayteam_name='" + temp[5]
                    + "', match_awayteam_score=" + temp[6]
                    + ", data='" + temp[7]
                    + "', home_win_prob=" + str(home_win_prob)
                    + ", draw_prob=" + str(draw_prob)
                    + ", away_win_prob=" + str(away_win_prob)
                    + ", home_shots=" + str(home_shots)
                    + ", away_shots=" + str(away_shots)
                    + ", home_off=" + str(home_off)
                    + ", away_off=" + str(away_off)
                    + ", home_poss=" + str(home_poss)
                    + ", away_poss=" + str(away_poss)
                    + ", home_corners=" + str(home_corners)
                    + ", away_corners=" + str(away_corners)
                    + ", home_fouls=" + str(home_fouls)
                    + ", away_fouls=" + str(away_fouls)
                    + ", home_goal_kicks=" + str(home_goal_kicks)
                    + ", away_goal_kicks=" + str(away_goal_kicks)
                    + ";")
    conn.commit()
    if not bad_request:
        update_computed_table(cur, conn)
    conn.close()
    print("done")


"""
TABLE matches: 0 match_id, 1 match_date, 2 match_status, 3 match_hometeam_name, 4 match_hometeam_score, 
5 match_awayteam_name, 6 match_awayteam_score, 7 data, 8 home_win_prob, 9 draw_prob, 
10-11 _shots, 12-13 _off, 14-15 _poss, 16-17 _corners, 18-19 _fouls, 20-21 goal_kicks, 22 away_win_prob
"""


def form_post_response(pred_row):
    match_data = {
        'home': pred_row[6],
        'away': pred_row[7],
        'date': pred_row[8],
        'home_win_prob': pred_row[3],
        'draw_prob': pred_row[5],
        'away_win_prob': pred_row[4],
        'home_score': pred_row[1],
        'away_score': pred_row[2],
        'home_shots': pred_row[11],
        'away_shots': pred_row[12],
        'home_off': pred_row[13],
        'away_off': pred_row[14],
        'home_poss': pred_row[15],
        'away_poss': pred_row[16],
        'home_corners': pred_row[17],
        'away_corners': pred_row[18],
        'home_fouls': pred_row[19],
        'away_fouls': pred_row[20],
        'home_goal_kicks': pred_row[21],
        'away_goal_kicks': pred_row[22],
    }
    return match_data


def get_matches_preds_within(start_date, end_date):
    from_string = '&from=' + start_date
    to_string = '&to=' + end_date
    api_string = '&APIkey=' + APIKey
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    r = requests.get(url + from_string + to_string + api_string, timeout=(60 * MINUTES_TO_WAIT))
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
        if item['match_status'] == 'FT':
            continue
        temp = [item[field] for field in fields]
        temp.append(json.dumps(item))
        match_id = item['match_id']
        # TODO remove force update
        one_week_ago = datetime.datetime.now() + datetime.timedelta(days=1)
        one_week_ago = one_week_ago.strftime('%Y-%m-%d')
        cur.execute("SELECT * FROM predictions WHERE last_updated >= '" + one_week_ago +
                    "' AND match_id=" + str(match_id) + ";")
        """
        Order of row data in TABLE predictions:
        0 prediction_id, 1 pred_home_score, 2 pred_away_score, 3 pred_home_win_percent, 4 pred_away_win_percent,
        5 pred_draw_percent, 6 home_name, 7 away_name, 8 match_date, 9 match_id
        """
        matches = cur.fetchall()
        if len(matches) < 1:
            # match doesn't have a prediction, so generate one
            home_name = normalize_team_name(item['match_hometeam_name'])
            away_name = normalize_team_name(item['match_awayteam_name'])
            """
            TABLE home_teams_comp
            0 match_hometeam_name, 1 matches_played, 2 goals_scored, 3 avg_goals_scored, 4 goals_conceded, 
            5 avg_goals_conceded, 6 home_wins, 7 home_win_p, 8 home_draws, 9 home_draw_p, 10 home_losses, 11 home_loss_p
            12 l20_win_p, 13 l20_loss_p, 14 l20_draw_p, 15 l20_avg_goals, 16 l20_avg_conc
            TABLE away_teams_comp
            (same as above but replace "home" with "away" everywhere it's mentioned
            """
            # home_computed_vals
            home_comps = get_computed_table_row(cur, home_name, True)
            away_comps = get_computed_table_row(cur, away_name, False)
            cur.execute("SELECT * FROM matches WHERE match_id=" + str(match_id) + ";")
            this_match = cur.fetchall()
            if len(this_match) < 1:
                continue
            """
            TABLE matches: 0 match_id, 1 match_date, 2 match_status, 3 match_hometeam_name, 4 match_hometeam_score, 
            5 match_awayteam_name, 6 match_awayteam_score, 7 data, 8 home_win_prob, 9 draw_prob, 
            10-11 _shots, 12-13 _off, 14-15 _poss, 16-17 _corners, 18-19 _fouls, 20-21 goal_kicks, 22 away_win_prob
            """
            this_match = this_match[0]
            stats = create_training_array(this_match[8], this_match[9], this_match[22], home_comps[7], home_comps[9],
                                          home_comps[11], away_comps[7],
                                          away_comps[9], away_comps[11], home_comps[12], home_comps[14],
                                          home_comps[13], away_comps[12], away_comps[14], away_comps[13], home_comps[3],
                                          away_comps[3], home_comps[4], away_comps[4], home_comps[15], away_comps[15],
                                          home_comps[16], away_comps[16])
            score_stats = create_score_training_array(this_match[8], this_match[9], this_match[22], home_comps[3],
                                                      away_comps[3], home_comps[4], away_comps[4], home_comps[15],
                                                      away_comps[15], home_comps[16], away_comps[16])
            home_goals_pred = get_score_pred(score_stats, True)
            away_goals_pred = get_score_pred(score_stats, False)
            # TODO remove
            if len(home_goals_pred) < 1:
                home_goals_pred = 0
            else:
                home_goals_pred = round(abs(home_goals_pred[0]))
            if len(away_goals_pred) < 1:
                away_goals_pred = 0
            else:
                away_goals_pred = round(abs(away_goals_pred[0]))
            win_loss_draw = get_win_draw_loss_probs(stats)[0]
            home_win_prob = win_loss_draw[2]
            draw_prob = win_loss_draw[1]
            away_win_prob = win_loss_draw[0]
            home_shots = this_match[10]
            away_shots = this_match[11]
            home_off = this_match[12]
            away_off = this_match[13]
            home_poss = this_match[14]
            away_poss = this_match[15]
            home_corners = this_match[16]
            away_corners = this_match[17]
            home_fouls = this_match[18]
            away_fouls = this_match[19]
            home_goal_kicks = this_match[20]
            away_goal_kicks = this_match[21]
            # See prediction table for what each item in pred_stats represents
            pred_stats = [match_id, home_goals_pred, away_goals_pred, home_win_prob, away_win_prob, draw_prob,
                          item['match_hometeam_name'], item['match_awayteam_name'], item['match_date'], match_id,
                          datetime.datetime.now().strftime("%Y-%m-%d"),
                          home_shots,
                          away_shots,
                          home_off,
                          away_off,
                          home_poss,
                          away_poss,
                          home_corners,
                          away_corners,
                          home_fouls,
                          away_fouls,
                          home_goal_kicks,
                          away_goal_kicks]
            match_data = form_post_response(pred_stats)
            future_predictions.append(match_data)
            cur.execute("INSERT INTO predictions VALUES ("
                        + pred_stats[0] +
                        "," + str(pred_stats[1])
                        + "," + str(pred_stats[2])
                        + "," + str(pred_stats[3])
                        + "," + str(pred_stats[4])
                        + "," + str(pred_stats[5])
                        + ",'" + str(pred_stats[6])
                        + "','" + str(pred_stats[7])
                        + "','" + str(pred_stats[8])
                        + "'," + str(pred_stats[9])
                        + ",'" + str(pred_stats[10]) + "', "
                        + str(home_shots) + ", "
                        + str(away_shots) + ", "
                        + str(home_off) + ", "
                        + str(away_off) + ", "
                        + str(home_poss) + ", "
                        + str(away_poss) + ", "
                        + str(home_corners) + ", "
                        + str(away_corners) + ", "
                        + str(home_fouls) + ", "
                        + str(away_fouls) + ", "
                        + str(home_goal_kicks) + ", "
                        + str(away_goal_kicks)
                        + ") ON CONFLICT (prediction_id) "
                        + "DO UPDATE SET "
                        + "last_updated='" + str(pred_stats[10])
                        + "',pred_home_score=" + str(pred_stats[1])
                        + ",pred_away_score=" + str(pred_stats[2])
                        + ",pred_home_win_percent=" + str(pred_stats[3])
                        + ",pred_away_win_percent=" + str(pred_stats[4])
                        + ",pred_draw_percent=" + str(pred_stats[5])
                        + ", home_shots=" + str(home_shots)
                        + ", away_shots=" + str(away_shots)
                        + ", home_off=" + str(home_off)
                        + ", away_off=" + str(away_off)
                        + ", home_poss=" + str(home_poss)
                        + ", away_poss=" + str(away_poss)
                        + ", home_corners=" + str(home_corners)
                        + ", away_corners=" + str(away_corners)
                        + ", home_fouls=" + str(home_fouls)
                        + ", away_fouls=" + str(away_fouls)
                        + ", home_goal_kicks=" + str(home_goal_kicks)
                        + ", away_goal_kicks=" + str(away_goal_kicks)
                        + ";")
            conn.commit()
        else:
            print('already exists')
            match = matches[0]
            print(match)
            # match has a prediction, so return it
            match_data = form_post_response(match)
            future_predictions.append(match_data)
    print("done")
    conn.close()
    return future_predictions
