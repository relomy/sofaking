import os
from espnff import League
from flask import Flask, render_template


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/', methods=['GET', 'POST'])
def index():
    league_id = 427822
    year = 2018

    league = League(league_id, year)

    response = {}
    response['matchups'] = get_matchups(league)
    response['scoreboard'] = get_scoreboard(league)
    response['scoreboard_short'] = get_scoreboard_short(league)
    response['power_rankings'] = get_power_rankings(league)
    response['trophies'] = get_trophies(league)
    errors = []

    # return render_template('index.html')
    return render_template('index.html', response=response, errors=errors)
    # return render(request, 'ff.html', {'response': response})


def pranks_week(league):
    """Look for score of 0 in team 1 to determine the last week."""
    count = 1
    first_team = next(iter(league.teams or []), None)
    # iterate through the first team's scores until you reach a week with 0 points scored
    for o in first_team.scores:
        if o == 0:
            if count != 1:
                count -= 1
            break
        else:
            # print("There's a score [{}] for week {}!".format(o, count))
            count += 1
    return count


def get_scoreboard_short(league, final=False):
    """Get current week's scoreboard with abbreviations."""
    if not final:
        matchups = league.scoreboard()
    else:
        matchups = league.scoreboard(week=pranks_week(league))
    score = ["{0} {1:.2f} - {2:.2f} {3}"
             .format(
                 i.home_team.team_abbrev, i.home_score,
                 i.away_score, i.away_team.team_abbrev)
             for i in matchups if i.away_team]
    text = ['Score Update'] + score + ['\n']
    # return '\n'.join(text)
    return score


def get_scoreboard(league):
    """Get current week's scoreboard."""
    matchups = league.scoreboard()
    score = ["{0} {1:.2f} - {2:.2f} {3}"
             .format(
                 i.home_team.team_name, i.home_score,
                 i.away_score, i.away_team.team_name)
             for i in matchups if i.away_team]
    text = ['Score Update'] + score + ['\n']
    # return '\n'.join(text)
    return score


def get_matchups(league):
    """Get current week's matchups."""
    matchups = league.scoreboard()

    score = ["{} ({}-{}) vs {} ({}-{})"
             .format(
                 i.home_team.team_name, i.home_team.wins, i.home_team.losses,
                 i.away_team.team_name, i.away_team.wins, i.away_team.losses)
             for i in matchups if i.away_team]
    text = ['This Week\'s Matchups'] + score + ['\n']
    # return '\n'.join(text)
    return score


def get_power_rankings(league):
    """
    Get current week's power rankings.

    ESPNFF uses two step dominance, as well as a combination of points scored and margin of victory.
    These are weighted 80/15/5 respectively.

    """
    p_w = pranks_week(league)
    pranks = league.power_rankings(week=p_w)

    score = ["{} - {}".format(i[0], i[1].team_name) for i in pranks if i]
    text = ['This Week\'s Power Rankings [{}]'.format(p_w)] + score + ['\n']
    # return '\n'.join(text)
    return score


def get_trophies(league):
    """Get trophies for highest score, lowest score, closest score, and biggest win."""
    low_score = 9999
    low_team_name = ''
    high_score = -1
    high_team_name = ''
    closest_score = 9999
    close_winner = ''
    close_loser = ''
    biggest_blowout = -1
    blown_out_team_name = ''
    ownerer_team_name = ''
    attempts = 0

    while True:
        try:
            week = pranks_week(league) - attempts
            print("[get_trophies] trying week: {}".format(week))
            matchups = league.scoreboard(week=week)
            break
        except Exception as e:
            print("pranks_week failed ({})".format(e))
            attempts += 1
            # print("Trying pranks_week ({}) - attempts ({}) = {} ..".format(
            #     pranks_week(league), attempts, pranks_week(league) - attempts))

    # loop through each matchup
    for i in matchups:
        if i.home_score > high_score:
            high_score = i.home_score
            high_team_name = i.home_team.team_name
        if i.home_score < low_score:
            low_score = i.home_score
            low_team_name = i.home_team.team_name
        if i.away_score > high_score:
            high_score = i.away_score
            high_team_name = i.away_team.team_name
        if i.away_score < low_score:
            low_score = i.away_score
            low_team_name = i.away_team.team_name
        if abs(i.away_score - i.home_score) < closest_score:
            closest_score = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                close_winner = i.home_team.team_name
                close_loser = i.away_team.team_name
            else:
                close_winner = i.away_team.team_name
                close_loser = i.home_team.team_name
        if abs(i.away_score - i.home_score) > biggest_blowout:
            biggest_blowout = abs(i.away_score - i.home_score)
            if i.away_score - i.home_score < 0:
                ownerer_team_name = i.home_team.team_name
                blown_out_team_name = i.away_team.team_name
            else:
                ownerer_team_name = i.away_team.team_name
                blown_out_team_name = i.home_team.team_name

    low_score_str = ['Low score:\n{} with {:.2f} points'
                     .format(low_team_name, low_score)]
    high_score_str = ['High score:\n{} with {:.2f} points'
                      .format(high_team_name, high_score)]
    close_score_str = ['{} was barely beat {} by a margin of {:.2f}!'
                       .format(close_winner, close_loser, closest_score)]
    blowout_str = ['{} was blown out by {} by a margin of {:.2f}!'
                   .format(blown_out_team_name, ownerer_team_name, biggest_blowout)]
    text = low_score_str + high_score_str + close_score_str + blowout_str
    # return '\n'.join(text)
    return text


if __name__ == '__main__':
    app.run()
