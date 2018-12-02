import requests
import psycopg2
import json
import html
import os

# TODO make private in env file
APIKey = os.environ['FOOTBALL_API_KEY']
url = 'https://apifootball.com/api/?action=get_events&from=2018-08-01&to=2018-12-02&league_id=62&APIkey='
DATABASE_URL = os.environ['DATABASE_URL']
# cur.execute("CREATE TABLE IF NOT EXISTS matches (match_id INTEGER PRIMARY KEY, match_date DATE, match_status varchar, " +
#             "match_hometeam_name varchar, match_hometeam_score INTEGER, " +
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


def test_me():
    print('broken')


def update_matches_table(startDate, endDate):
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()
    # TODO populate with 2015-09-01 to 2018-07-31, or switch to new
    r = requests.get(url + APIKey, timeout=(60*10))
    s = json.dumps(r.json())
    h = html.unescape(s)
    h1 = h.replace(" FC", "")
    json_data = json.loads(h1)
    # conn = psycopg2.connect(dbname="Sportswizz", user="postgres", password="1qaz2wsx")
    # print(json_data)
    for item in json_data:
        # sometimes there's a bug where game is not updated yet and it's just an empty string
        if not item['match_hometeam_score']:
            continue
        temp = [item[field] for field in fields]
        # stats = item["statistics"]
        # for i in stats:
        #     home = i["home"]
        #     away = i["away"]
        #     temp.append(home)
        #     temp.append(away)
        temp.append(json.dumps(item))
        cur.execute("INSERT INTO matches VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", tuple(temp))
    conn.commit()
    conn.close()
    print("done")
