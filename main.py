import random
import json
from flask import Flask, request, render_template, redirect

people = ['David', 'Felix', 'Hannah', 'Jakob B.', 'Jakob D.', 'Judith', 'Lara',
          'Leonie', 'Lisa', 'Sanne', 'Soeren', 'Sophia', 'Steffen', 'Timo']

alive = []
things = []

content = {}


def update_content():
    with open(".//list.json", mode='w') as file:
        file.write(json.dumps(content))


def init():
    global content

    with open(".//list.json", mode='r') as file:
        content = json.load(file)

    for person in people:
        alive.append("True")


def reset():
    global content
    people_copy = people.copy()
    random.shuffle(people_copy)

    while things.__contains__(""):
        things.remove("")

    things_list = []
    for person in people:
        if len(things) == 0:
            thing = ""
        else:
            thing = random.choice(things)
            things.remove(thing)
        things_list.append(thing)
        alive.append("True")

    new_content = {
        "people": people_copy,
        "things": things_list
    }

    content = new_content
    update_content()


def index_of(name):
    return content['people'].index(name)


def renew_thing(name):
    i = index_of(name)
    if len(things) == 0:
        thing = ""
    else:
        thing = random.choice(things)
        things.remove(thing)

    content['things'][i] = thing

    update_content()


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


def get_dialogue(name):
    i = index_of(name)
    to_kill = content['people'][(i+1) % len(content['people'])]
    thing = content['things'][i]
    if alive[i] == "True":
        return f"{name}, toete {to_kill} mit {thing}!"
    else:
        return f"Du hast {name} getoetet! Toete nun {to_kill} mit {thing}!"


app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    name = request.args.get("name")
    with app.app_context():
        return render_template('index.html', people=people)


@app.route('/reset')
def reset_game():
    reset()
    return "Has reset"


@app.route("/result", methods=['GET', 'POST'])
def result():
    name = request.args.get('name')
    select = request.form.get('people_select')
    if name is None:
        return redirect(f"result?name={select}")

    i = index_of(name)
    if alive[i] == "True":
        with app.app_context():
            return render_template('result.html', name=name, get_dialogue=get_dialogue)
    else:
        return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>toeten</title>
            </head>
            <body>
                { get_dialogue(name) }
                <a href="/"> Zurueck </a>
            </body>
        """



@app.route("/addthing", methods=['GET', 'POST'])
def add_thing():
    thing = request.form.get('thing')
    things.append(thing)
    return redirect("/")


@app.route("/newthing", methods=['GET', 'POST'])
def new_thing():
    name = request.args.get('name')
    if name is None:
        return redirect("/")
    renew_thing(name)
    alive[index_of(name)] = "False"
    print(f"{name} wurde getoetet!")
    return redirect(f"/result?name={name}")


@app.route("/friedhof")
def friedhof():
    dead_people = []
    for i, person in enumerate(content["people"]):
        if alive[i] == "False":
            dead_people.append(person)
    with app.app_context():
        return render_template("friedhof.html", dead_people=dead_people, get_inschrift=get_inschrift)



if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0")
