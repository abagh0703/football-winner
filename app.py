from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from football_api import *
import datetime
import numpy as np
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

app = Flask(__name__)


@app.route('/', methods=('GET', 'POST'))
def register():
    """To run this web application:
        1) Input the following into the command line in the directory with app.py
            a) for mac:
                i) "export FLASK_APP=hello.py"
                ii) "flask run"
            b) for windows on command prompt:
                i) C:\path\to\app>set FLASK_APP=app.py
                ii) "flask run"
            c) for windows on power shell
                i) PS C:\path\to\app> $env:FLASK_APP = "hello.py"
                ii) "flask run"
        2) Head over to the URL "http://127.0.0.1:5000/"

        Input something in the box and click "submit". The new screen rendered is the input
        (demonstrating use of request.form)."""

    if request.method == 'POST':
        print('get')
        # 1-indexed, so 2=february not march
        month_string = request.args.get('month')
        year_string = request.args.get('year')
        if month_string and year_string:
            month_num = 1
            year_num = 2018
            now = datetime.datetime.now()
            current_year = now.year
            try:
                month_num = int(month_string)
                year_num = int(year_string)
            except ValueError:
                return jsonify({})
            print(0 <= (year_num-current_year) <= 1)
            print(year_num)
            print(current_year)
            # make sure month and year are valid
            if (not (1 <= month_num <= 12)) or (not (0 <= (year_num-current_year) <= 1)):
                return jsonify({})

            return jsonify({"month num": month_string})
        else:
            return jsonify({})

    # updates the table whenever a GET request is made. from our pinger on uptimerobot, should be pinged 1x/day
    if request.method == 'GET':

        """
        X must be an array of shape (x, 23), where x is the number of games and 23 is the number of features we have
        for each game. The features must be in order. They are:

            1. Average home win probability given by betting odds (1 / home-winodds)
            2. Average draw probability given by betting odds (1 / draw-odds)
            3. Average away win probability given by betting odds (1 / away-win-odds)
            4. Home season win percentage
            5. Home season draw percentage
            6. Home season loss percentage
            7. Away season win percentage
            8. Away season draw percentage
            9. Away season loss percentage
            10. Home last-20 win percentage (going into the last season)
            11. Home last-20 draw percentage (going into the last season)
            12. Home last-20 loss percentage (going into the last season)
            13. Away last-20 win percentage (going into the last season)
            14. Away last-20 draw percentage (going into the last season)
            15. Away last-20 loss percentage (going into the last season)
            16. home season goals scored/game
            17. away season goals scored/game
            18. home season goals conceded/game
            19. away season goals conceded/game
            20. home last-20 goals scored/game
            21. away last-20 goals scored/game
            22. home last-20 goals conceded/game
            23. away last-20 goals conceded/game

        The following is a placeholder X
        """

        x = np.zeros((1, 23))

        # loading pickled model
        with open("model.pkl", "rb") as f:
            clf = pickle.load(f)

        pred = clf.predict(x)

        return jsonify({})
    else:
        return render_template('start.html')
