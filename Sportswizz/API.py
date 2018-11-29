import requests
import psycopg2
import json
import html

APIKey = 'ca42e9efce635c0d2922b584c8fcdd2e121258dfb8752e00875018bda96521df'
url = 'https://apifootball.com/api/?action=get_events&from=2018-08-01&to=2018-11-28&league_id=62&APIkey='
r = requests.get(url + APIKey)
s = json.dumps(r.json())
h = html.unescape(s)
h1 = h.replace(" FC", "")
j = json.loads(h1)


conn = psycopg2.connect(dbname="Sportswizz", user="postgres", password="1qaz2wsx")
# print(j)

cur = conn.cursor()

cur.execute("CREATE TABLE matches (match_id INTEGER PRIMARY KEY, match_date DATE, match_status varchar, " +
            "match_hometeam_name varchar, match_hometeam_score INTEGER, " +
            "match_awayteam_name varchar, match_awayteam_score INTEGER, " +
            "data json);")

fields = [
    'match_id',
    'match_date',
    'match_status',
    'match_hometeam_name',
    'match_hometeam_score',
    'match_awayteam_name',
    'match_awayteam_score'
]

for item in j:
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
