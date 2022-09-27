"""
In this module lives the flask application of the website.
"""

import os
import logic
import random
from flask import Flask, request, render_template, redirect
import settings


sessions = {}
""" 
a dict of all the active sessions. 
looks like this:
{
    'session_name1': session1
    ...
}
"""
hash_table = {}
""" 
a dict that links hashes of session- and player-names with the names themselves.
looks like this:
{
    'hash_of_session_name1_and_player_name1': ('session_name1', 'player_name1')
    ...
}
all players in all sessions can be looked up here.
"""


def hash_args(session_name, player_name):
    """
    Returns a hash of a concatenation of session_name and player_name as a string.
    The hash is used in the global hash-table
    :param session_name: the name of a session
    :param player_name: the name of a player
    :return: the hash-value
    """
    hash_str = str(hash(session_name + player_name))
    hash_table[hash_str] = (session_name, player_name)
    return hash_str


def str_or(str1, str2):
    """
    Returns the first input that is not None. If all inputs are None returns None.
    :param str1: first string
    :param str2: second string
    :return: str1 or str2 or None
    """
    if str1 is not None:
        return str1

    if str2 is not None:
        return str2

    return None


def start_session(session_name):
    """
    start the session with name session_name. If there is no save-file of this session,
    create a new session.
    :param session_name: the name of the session
    :return: None
    """
    sessions[session_name] = (logic.load_session(session_name))


def get_inschrift():
    """
    returns a random Grabinschrift
    :return: a Grabinschrift as str
    """
    inschriften = [
        "Er starb wie er lebte.",
        "Möge er in Frieden ruhen.",
        "Stets bemüht.",
        "Tja.",
        "Er liegt jetzt da, wo sein Niveau immer schon war.",
        "Geliebter Trinker.",
        "Gruess Gott!",
        "Am Ende fragt man sich immer, woran hat es jelegen.",
        "Bis bald.",
        "Hat die Gruppe verlassen.",
        "404 - not Found."
    ]

    return random.choice(inschriften)


app = Flask(__name__, template_folder='templates')
"""
The Flask application
"""


@app.route('/')
def index():
    """
    Returns the index-page with corresponding attributes
    :return: The index-page
    """
    with app.app_context():
        return render_template('index.html')


@app.route('/session', methods=['POST'])
def set_session():
    """
    Called to get the personal session-page
    :return: redirect to the personal session-page
    """
    session_name = request.form.get('session_name')
    player_name = request.form.get('player_name')

    if session_name is None or player_name is None:
        return redirect('/')

    if session_name not in sessions:
        start_session(session_name)

    session = sessions.get(session_name)
    if player_name not in session.players:
        sessions.get(session_name).add_player(player_name)

    hash_str = hash_args(session_name, player_name)
    return redirect(f'/session?hash={hash_str}')


@app.route('/session', methods=['GET'])
def get_session():
    """
    Returns the personal session-page with corresponding attributes
    :return: The session-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    if hash_str is None or hash_str not in hash_table:
        return redirect('/')

    session_name, player_name = hash_table.get(hash_str)

    session = sessions.get(session_name)

    if session.running:
        if session.player_in_game(player_name):
            if session.is_alive(player_name):
                mode = 'alive'
                victim = session.get_victim(player_name)
                weapon = session.get_thing(player_name)
            else:
                mode = 'dead'
                victim = None
                weapon = None
        else:
            mode = 'not_in_game'
            victim = None
            weapon = None

        player_infos = []

        for player in session.get_players():
            if session.is_alive(player):
                alive = "alive"
            else:
                alive = "dead"
            kill_count = session.get_kill_count(player)
            player_infos.append((player, kill_count, alive))
            player_infos.sort(key=lambda x: x[0], reverse=True)
            player_infos.sort(key=lambda x: x[1], reverse=True)

        with app.app_context():
            return render_template(
                'session.html',
                hash=hash_str,
                session_name=session_name,
                player_name=player_name,
                victim_name=victim,
                weapon=weapon,
                mode=mode,
                nr_of_things=len(session.things),
                player_infos=player_infos
            )

    else:
        mode = "not_running"
        with app.app_context():
            return render_template(
                'session.html',
                hash=hash_str,
                session_name=session_name,
                player_name=player_name,
                nr_of_things=len(session.things),
                mode=mode
            )


@app.route("/settings")
def settings_page():
    """
    Returns the settings-page with corresponding attributes
    :return: The settings-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))

    if hash_str is None:
        return redirect("/")

    with app.app_context():
        return render_template(
            "settings.html",
            hash=hash_str
        )


@app.route("/add_thing", methods=['POST'])
def add_thing():
    """
    add a weapon to the session that corresponds to
    request.args.get('hash') or request.form.get('hash')
    :return: index-page if there was a problem, personal session-page if not
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    session_name, _ = hash_table.get(hash_str)
    session = sessions.get(session_name)
    thing = request.form.get('thing')

    if session is None or thing is None:
        return redirect('/')

    session.add_thing(thing)
    return redirect(f'/session?hash={hash_str}')


@app.route("/has_killed", methods=['GET', 'POST'])
def has_killed():
    """
    called by the killer that corresponds to
    request.args.get('hash') or request.form.get('hash'),
    to kill his current victim.
    :return: index-page if there was a problem, personal session-page if not
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    print(hash_table)
    session_name, player_name = hash_table.get(hash_str)
    session = sessions.get(session_name)

    if session is None:
        return redirect('/')

    session.has_killed(player_name)
    print(f"{session.get_victim(player_name)} wurde getoetet!")
    return redirect(f"/session?hash={hash_str}")


@app.route("/friedhof")
def friedhof():
    """
    Returns the friedhof-page with corresponding attributes
    :return: The friedhof-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    session_name, _ = hash_table.get(hash_str)
    session = sessions.get(session_name)

    if session is None:
        return redirect('/')

    dead_people = session.get_dead()
    with app.app_context():
        return render_template(
            "friedhof.html",
            hash=hash_str,
            dead_people=dead_people,
            get_inschrift=get_inschrift
        )


@app.route('/new_game')
def new_game():
    """
    start a new game in the session that corresponds to
    request.args.get('hash') or request.form.get('hash').
    :return: the personal session-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    print(hash_str)
    session_name, _ = hash_table.get(hash_str)

    if session_name is None:
        return redirect('/')

    session = sessions.get(session_name)
    session.start_new_game()
    return redirect(f'/session?hash={hash_str}')


@app.route('/save_game')
def save_game():
    """
    save the session that corresponds to
    request.args.get('hash') or request.form.get('hash').
    :return: the personal session-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    session_name, _ = hash_table.get(hash_str)

    if session_name is None:
        return redirect('/')

    session = sessions.get(session_name)
    session.save()
    return redirect(f'/session?hash={hash_str}')


@app.route('/end_game')
def end_game():
    """
    if there is a game running in the session that corresponds to
    request.args.get('hash') or request.form.get('hash'),
    end it.
    :return: the personal session-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    session_name, _ = hash_table.get(hash_str)

    if session_name is None:
        return redirect('/')

    session = sessions.get(session_name)
    session.end_game()
    return redirect(f'/session?hash={hash_str}')


@app.route('/remove_player')
def remove_player():
    """
    remove the player with name request.args.get('player_to_remove')
    from the session that corresponds to
    request.args.get('hash') or request.form.get('hash').
    :return: the personal session-page
    """
    hash_str = str_or(request.args.get('hash'), request.form.get('hash'))
    session_name, player_name = hash_table.get(hash_str)

    player_to_remove = request.args.get('player_to_remove')

    if session_name is None:
        return redirect('/')

    session = sessions.get(session_name)
    session.remove_player(player_to_remove)

    del hash_table[hash_args(session_name, player_to_remove)]

    if len(session.players) == 0:
        del sessions[session_name]
        os.remove(f"..//saves//{session_name}.json")

    if player_to_remove == player_name:
        return redirect('/')
    return redirect(f'/session?hash={hash_str}')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.PORT)
