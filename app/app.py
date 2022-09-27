import settings
import logic
import random
from flask import Flask, request, render_template, redirect


current_game = logic.Session("Frankreich2", settings.INITIAL_PLAYERS, [])


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
    if not current_game.running:
        with app.app_context():
            return render_template(
                'index.html',
                persons=current_game.players,
                nr_of_things=str(len(current_game.things)),
                running="False"
            )
    else:
        leaderboard = zip(
            current_game.current_game['person_order'],
            current_game.current_game['kill_count'])
        leaderboard = sorted(leaderboard, key=lambda x: x[0])
        leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
        with app.app_context():
            return render_template(
                'index.html',
                persons=current_game.players,
                nr_of_things=str(len(current_game.things)),
                running="True",
                leaderboard=leaderboard
            )


@app.route("/personal", methods=['GET', 'POST'])
def personal():
    name = request.args.get('name')
    select = request.form.get('people_select')
    if name is None:
        return redirect(f"personal?name={select}")

    if not current_game.running:
        with app.app_context():
            return render_template(
                'personal_not_running.html'
            )

    if current_game.is_alive(name):
        if current_game.get_victim(name) == name:
            with app.app_context():
                return render_template(
                    'personal_winner.html',
                    name=name
                )
        with app.app_context():
            return render_template(
                'personal_alive.html',
                name=name,
                victim=current_game.get_victim(name),
                thing=current_game.get_thing(name)
            )
    else:
        with app.app_context():
            return render_template(
                'personal_dead.html',
                name=name
            )



@app.route("/addthing", methods=['GET', 'POST'])
def add_thing():
    thing = request.form.get('thing')
    current_game.add_thing(thing)
    return redirect("/")


@app.route("/has_killed", methods=['GET', 'POST'])
def has_killed():
    name = request.args.get('name')
    if name is None:
        return redirect("/")
    current_game.has_killed(name)
    print(f"{current_game.get_victim(name)} wurde getoetet!")
    return redirect(f"/personal?name={name}")


@app.route("/friedhof")
def friedhof():
    dead_people = current_game.get_dead()
    with app.app_context():
        return render_template(
            "friedhof.html",
            dead_people=dead_people,
            get_inschrift=get_inschrift
        )


@app.route("/settings")
def settings_page():
    game_states = current_game.get_available_game_states()

    saves = game_states.keys()
    dates = []
    for save in saves:
        dates.append(game_states[save]['last_saved'])

    with app.app_context():
        return render_template(
            "settings.html",
            persons=current_game.players,
            players=current_game.get_players(),
            saves=zip(saves, dates)
        )


@app.route("/add_person", methods=['GET', 'POST'])
def add_person():
    name = request.form.get('person')
    if name not in current_game.players:
        current_game.add_person(name)
    return redirect("/settings")


@app.route("/new_game")
def new_game():
    current_game.start_new_game()
    print(current_game)
    return redirect("/settings")


@app.route("/load_game", methods=['GET', 'POST'])
def load_game():
    save = request.form.get('save_select')
    print(current_game)
    current_game.load_game_state(save)
    print(current_game)
    return redirect("/settings")


@app.route("/save_persons")
def save_persons():
    current_game.save_persons()
    return redirect("/settings")


@app.route("/save_things")
def save_things():
    current_game.save_things()
    return redirect("/settings")


if __name__ == "__main__":
    current_game.save_game_state("save0", as_new=False)
    app.run(host="0.0.0.0", port=settings.PORT)
