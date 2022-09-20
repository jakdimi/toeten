import random
import json
from os.path import exists
from datetime import datetime


class Game:

    def __init__(self, name, persons, things):
        self.name = name
        self.running = False
        self.persons = persons
        self.things = things
        self.current_gamestate = {
            'person_order': [],
            'things': [],
            'alive_status': [],
            'killcount': [],
            'available_things': [],
            'last_saved': ''
        }

    def __repr__(self):
        return \
            f"""
            Game: {{
              name: {self.name}
              persons: {self.persons}
              things: {self.things}
              current_gamestate: {self.current_gamestate}
            }}
            """

    # ========================= handle the saving and loading ============================

    def save_persons(self):
        if exists(f"..//saves//{self.name}.json"):
            with open(f"..//saves//{self.name}.json", mode='r') as file:
                game = json.load(file)
            game['players'] = self.persons

            with open(f"..//saves//{self.name}.json", mode='w') as file:
                file.write(json.dumps(game))

    def save_things(self):
        if exists(f"..//saves//{self.name}.json"):
            with open(f"..//saves//{self.name}.json", mode='r') as file:
                game = json.load(file)
            game['things'] = self.things

            with open(f"..//saves//{self.name}.json", mode='w') as file:
                file.write(json.dumps(game))

    def save_gamestate(self, gamestate_name="save", as_new=True):
        """ save the current gamestate """

        self.current_gamestate['last_saved'] = datetime.now().strftime("%D:%H:%M:%S")

        game = {
            'name': self.name,
            'players': self.persons,
            'things': self.things,
            'gamestates': {}
        }

        # retreive saved gamestates, if a save file already exists
        if exists(f"..//saves//{self.name}.json"):
            with open(f"..//saves//{self.name}.json", mode='r') as file:
                game['gamestates'] = json.load(file)['gamestates']

        # make sure that the gamestate is saved as a new gamestate
        if gamestate_name in game['gamestates'].keys() and as_new is True:
            count = 1
            while (gamestate_name + count.__str__()) in game['gamestates']:
                count += 1
            gamestate_name = gamestate_name + count.__str__()

        # save game
        game['gamestates'][gamestate_name] = self.current_gamestate
        with open(f"..//saves//{self.name}.json", mode='w') as file:
            file.write(json.dumps(game))

    def load_gamestate(self, gamestate_name="save"):
        """ load gamestate 'name' """

        # load save file
        with open(f"..//saves//{self.name}.json", mode='r') as file:
            game = json.load(file)

        # if gamestate already exists, load that gamestate, else create new gamestate
        if gamestate_name in game['gamestates'].keys():
            self.current_gamestate = game['gamestates'][gamestate_name]

        else:
            self.current_gamestate = self.make_new_gamestate()

        self.running = True

    def make_new_gamestate(self):
        """
        create a new gamestate of this game
        :return: the new gamestate
        """
        new_gamestate = {
            'person_order': [],
            'things': [],
            'alive_status': [],
            'killcount': [],
            'available_things': []
        }

        # set the person order for the new game
        players_copy = self.persons.copy()
        random.shuffle(players_copy)
        new_gamestate['person_order'] = players_copy

        # set the available things for the new game
        new_gamestate['available_things'] = self.things.copy()

        # set the things, alive_status and killcount for the new game
        for person in self.persons:
            if len(new_gamestate['available_things']) == 0:
                new_gamestate['available_things'] = self.things.copy()

            thing = random.choice(new_gamestate['available_things'])
            new_gamestate['available_things'].remove(thing)

            new_gamestate['things'].append(thing)
            new_gamestate['alive_status'].append("True")
            new_gamestate['killcount'].append("0")

        return new_gamestate

    def get_available_gamestates(self):
        if not exists(f"..//saves//{self.name}.json"):
            return []

        with open(f"..//saves//{self.name}.json", mode='r') as file:
            gamestates = json.load(file)['gamestates']
        return gamestates

    def start_new_game(self):
        self.current_gamestate = self.make_new_gamestate()
        self.running = True
        self.save_gamestate()

    # =====================================================================================

    # ========================== handle game mechanics ====================================

    def add_thing(self, thing):
        self.things.append(thing)
        self.current_gamestate['available_things'].append(thing)
        random.shuffle(self.current_gamestate['available_things'])

    def add_person(self, person):
        self.persons.append(person)
        self.persons.sort()

    def get_players(self):
        players_copy = self.current_gamestate['person_order'].copy()
        players_copy.sort()
        return players_copy

    def _index_of(self, name):
        return self.current_gamestate['person_order'].index(name)

    def is_alive(self, name):
        alive_status = self.current_gamestate['alive_status']
        return alive_status[self._index_of(name)] == "True"

    def renew_thing(self, name):
        available_things = self.current_gamestate['available_things']
        if len(available_things) == 0:
            available_things = self.things.copy()

        thing = random.choice(available_things)
        available_things.remove(thing)

        self.current_gamestate['things'][self._index_of(name)] = thing

    def get_victim(self, name):
        ind = self._index_of(name)
        person_order = self.current_gamestate['person_order']
        alive_status = self.current_gamestate['alive_status']
        for i in range(ind + 1, len(self.persons) + ind + 1):
            if alive_status[i % len(person_order)] == "True":
                victim = person_order[i % len(person_order)]
                return victim
        return ""

    def get_thing(self, name):
        ind = self._index_of(name)
        return self.current_gamestate['things'][ind]

    def has_killed(self, killer_name):
        victim_index = self._index_of(self.get_victim(killer_name))
        killer_index = self._index_of(killer_name)
        alive_status = self.current_gamestate['alive_status']
        killcount = self.current_gamestate['killcount']
        self.renew_thing(killer_name)
        killcount[killer_index] = f"{ int(killcount[killer_index]) + 1 }"
        alive_status[victim_index] = "False"
        print(f"{killer_name} hat {self.get_victim(killer_name)} getötet! Insgesamt tötete {killer_name} {killcount[killer_index]}!")

    def get_dead(self):
        dead_people = []
        for person in self.current_gamestate['person_order']:
            if not self.is_alive(person):
                dead_people.append(person)
        return dead_people

# =====================================================================================
