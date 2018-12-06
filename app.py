from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from football_api import *
import datetime

app = Flask(__name__)


def add_two_zeroes(s):
    if len(s) < 2:
        return "0" + s
    return s


def format_date_string(year, month, day):
    return add_two_zeroes(str(year)) + '-' + add_two_zeroes(str(month)) + '-' + add_two_zeroes(str(day))


@app.route('/', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        # 1-indexed, so 2=february not march
        month_string = request.args.get('month')
        year_string = request.args.get('year')
        if month_string and year_string:
            month_num = 1
            year_num = 2018
            today = datetime.datetime.now()
            current_year = today.year
            try:
                month_num = int(month_string)
                year_num = int(year_string)
            except ValueError:
                return jsonify({})
            # make sure month and year are valid
            if (not (1 <= month_num <= 12)) or (not (0 <= (year_num - current_year) <= 1)):
                return jsonify({})
            # we know month_num and year_num are valid.
            # now get all games for the rest of the month,
            day_num = None
            last_day_num = None
            # if it's the same month, then get all games for the rest of the month, otherwise get all games for the
            # entire month
            if month_num == int(today.month):
                day_num = int(today.day)
            else:
                day_num = 1
            last_day_num = 31
            matches_data = get_matches_preds_within(format_date_string(year_num, month_num, day_num),
                                                    format_date_string(year_num, month_num, last_day_num))
            resp = jsonify(matches_data)
            resp.headers.add('Access-Control-Allow-Origin', '*')
            return resp
            # return jsonify({"month num": month_num})
        else:
            return jsonify({})

    # updates the table whenever a GET request is made. from our pinger on uptimerobot, should be pinged 1x/day
    if request.method == 'GET':
        # update_matches_table('2015-09-15', '2018-09-15')
        # # update_matches_table('2015-09-01', '2018-12-04')
        # return "success"
        today = datetime.datetime.now()
        two_days_ago = today + datetime.timedelta(days=-2)
        five_days_ahead = today + datetime.timedelta(days=5)
        today_full = format_date_string(today.year, today.month, today.day)
        five_days_ahead_full = format_date_string(five_days_ahead.year, five_days_ahead.month, five_days_ahead.day)
        past_full = format_date_string(two_days_ago.year, two_days_ago.month, two_days_ago.day)
        # update_matches_table(past_full, today_full)
        update_matches_table(past_full, five_days_ahead_full)
        return "success"
