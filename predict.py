import numpy as np
import pickle
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split

with open('models/home_goals.pkl', 'rb') as f:
    clf_home = pickle.load(f)
with open('models/away_goals.pkl', 'rb') as f:
    clf_away = pickle.load(f)
with open("models/model.pkl", "rb") as f:
    clf_model = pickle.load(f)

x = np.zeros((1, 23))


def get_score_pred(stats, is_home):
    # Returns predicted number of goals scored
    clf = None
    if is_home:
        clf = clf_home
    else:
        clf = clf_away
    # number of goals home team scores
    return clf.predict(stats)


def get_win_draw_loss_probs(stats):
    # Would give 3 probabilities, last value is home team win prob, middle value draw, first value away team win prob
    return clf_model.predict_proba(stats)


def create_training_array(avg_betting_home_win_prob,
                          avg_betting_draw_prob,
                          avg_betting_away_win_prob,
                          home_season_win_perc,
                          home_season_draw_perc,
                          home_season_loss_perc,
                          away_season_win_perc,
                          away_season_draw_perc,
                          away_season_loss_perc,
                          home_l20_win_perc,
                          home_l20_draw_perc,
                          home_l20_loss_perc,
                          away_l20_win_perc,
                          away_l20_draw_perc,
                          away_l20_loss_perc,
                          home_season_goals_per_game,
                          away_season_goals_per_game,
                          home_season_conc_per_game,
                          away_season_conc_per_game,
                          home_l20_goals_per_game,
                          away_l20_goals_per_game,
                          home_l20_goals_conc_per_game,
                          away_l20_goals_conc_per_game):
    stats_arr = np.array([avg_betting_home_win_prob,
                          avg_betting_draw_prob,
                          avg_betting_away_win_prob,
                          home_season_win_perc,
                          home_season_draw_perc,
                          home_season_loss_perc,
                          away_season_win_perc,
                          away_season_draw_perc,
                          away_season_loss_perc,
                          home_l20_win_perc,
                          home_l20_draw_perc,
                          home_l20_loss_perc,
                          away_l20_win_perc,
                          away_l20_draw_perc,
                          away_l20_loss_perc,
                          home_season_goals_per_game,
                          away_season_goals_per_game,
                          home_season_conc_per_game,
                          away_season_conc_per_game,
                          home_l20_goals_per_game,
                          away_l20_goals_per_game,
                          home_l20_goals_conc_per_game,
                          away_l20_goals_conc_per_game])
    return stats_arr.reshape(1, -1)


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

"""
x = np.zeros((1, 23))

# loading pickled model
with open("model.pkl", "rb") as f:
    clf = pickle.load(f)

pred = clf.predict(x)

return jsonify({})
else:
return render_template('start.html')



x = np.zeros((1, 23))

# loading pickled model
with open("model.pkl", "rb") as f:
    clf = pickle.load(f)
pred0 = clf.predict(x)
pred = clf.predict_proba(x)
print(pred0)
print(pred)
return "done"        
"""
