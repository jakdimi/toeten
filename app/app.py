import settings
import logic
import random
from flask import Flask, request, render_template, redirect


sessions = {}
current_game = logic.Session("Frankreich2", settings.INITIAL_PLAYERS, [])
hash_table = {}


def hash_args(session_name, player_name):
    hash_str = str(hash(session_name + player_name))
    hash_table[hash_str] = (session_name, player_name)
    return hash_str


def start_session(session_name):
    sessions[session_name] = (logic.load_session(session_name))


def get_inschrift():
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


@app.route('/')
def index():
    with app.app_context():
        return render_template('index.html')


@app.route('/session', methods=['POST'])
def set_session():
    session_name = request.form.get('session_name')
    player_name = request.form.get('player_name')

    if session_name is None or player_name is None:
        return redirect('/')

    if session_name not in sessions.keys():
        start_session(session_name)

    session = sessions[session_name]
    if player_name not in session.players:
        sessions[session_name].add_player(player_name)

    hash_str = hash_args(session_name, player_name)
    return redirect(f'/session?hash={hash_str}')


@app.route('/session', methods=['GET'])
def get_session():
    hash_str = request.args.get('hash')
    if hash_str is None:
        return redirect('/')

    session_name, player_name = hash_table[hash_str]

    session = sessions[session_name]
    print(session)

    if session.running:
        if session.is_alive(player_name):
            mode = 'alive'
        else:
            mode = 'dead'

        player_infos = []

        for player in session.get_players():
            if session.is_alive(player):
                alive = "alive"
            else:
                alive = "dead"
            kill_count = session.get_kill_count(player)
            player_infos.append((player, kill_count, alive))

        with app.app_context():
            return render_template(
                'session.html',
                hash=hash_str,
                session_name=session_name,
                player_name=player_name,
                victim_name=session.get_victim(player_name),
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
    pass


@app.route("/add_thing", methods=['POST'])
def add_thing():
    hash_str = request.args.get('hash')
    thing = request.form.get('thing')
    current_game.add_thing(thing)
    return redirect(f'/session?hash={hash_str}')


@app.route("/has_killed", methods=['GET', 'POST'])
def has_killed():
    hash_str = request.args.get('hash')

    if hash_str is None:
        return redirect('/')

    session_name, player_name = hash_table[hash_str]
    current_game.has_killed(player_name)
    print(f"{current_game.get_victim(player_name)} wurde getoetet!")
    return redirect(f"/personal?name={player_name}")


@app.route("/friedhof")
def friedhof():
    dead_people = current_game.get_dead()
    with app.app_context():
        return render_template(
            "friedhof.html",
            dead_people=dead_people,
            get_inschrift=get_inschrift
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.PORT)
