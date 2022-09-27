import random
import json
from os.path import exists
from os import mkdir


class Session:

    def __init__(self, name, players, things):
        self.name = name
        self.running = False
        self.players = players
        self.things = things
        self.current_game = {
            'player_order': [],
            'things': [],
            'alive_status': [],
            'kill_count': [],
            'available_things': []
        }

    def __repr__(self):
        return \
            f"""Game: {{
    name: {self.name}
    persons: {self.players}
    things: {self.things}
    current_game: {self.current_game}
}}"""

    def as_dict(self):
        return {
            'name': self.name,
            'running': self.running,
            'players': self.players,
            'things': self.things,
            'current_game': self.current_game
        }

    # ========================= handle the saving and loading ============================

    def make_new_game(self):
        """
        create a new game of this game
        :return: the new game
        """
        new_game = {
            'player_order': [],
            'things': [],
            'alive_status': [],
            'kill_count': [],
            'available_things': []
        }

        # set the person order for the new game
        players_copy = self.players.copy()
        random.shuffle(players_copy)
        new_game['player_order'] = players_copy

        # set the available things for the new game
        new_game['available_things'] = self.things.copy()

        # set the things, alive_status and kill_count for the new game
        for person in self.players:
            if len(new_game['available_things']) == 0:
                if len(self.things) == 0:
                    new_game['available_things'].append("")
                else:
                    new_game['available_things'] = self.things.copy()

            thing = random.choice(new_game['available_things'])
            new_game['available_things'].remove(thing)

            new_game['things'].append(thing)
            new_game['alive_status'].append("True")
            new_game['kill_count'].append("0")

        return new_game

    def save(self):
        if not exists("..//saves//"):
            mkdir("..//saves//")

        file_name = f"..//saves//{self.name}.json"
        with open(file_name, mode='w') as file:
            file.write(json.dumps(self.as_dict()))
            print(f"Session.save: {json.dumps(self.as_dict())}")

    def start_new_game(self):
        self.current_game = self.make_new_game()
        self.running = True
        self.save()

    def end_game(self):
        self.current_game = {}
        self.running = False
        self.save()

    # =====================================================================================

    # ========================== handle game mechanics ====================================

    def _index_of(self, name):
        return self.current_game['player_order'].index(name)

    def add_thing(self, thing):
        self.things.append(thing)
        if self.running:
            self.current_game['available_things'].append(thing)
            random.shuffle(self.current_game['available_things'])

    def add_player(self, person):
        self.players.append(person)
        self.players.sort()

    def get_players(self):
        players_copy = self.current_game['player_order'].copy()
        players_copy.sort()
        return players_copy

    def is_alive(self, name):
        alive_status = self.current_game['alive_status']
        return alive_status[self._index_of(name)] == "True"

    def renew_thing(self, name):
        available_things = self.current_game['available_things']
        if len(available_things) == 0:
            available_things = self.things.copy()

        thing = random.choice(available_things)
        available_things.remove(thing)

        self.current_game['things'][self._index_of(name)] = thing

    def get_victim(self, name):
        ind = self._index_of(name)
        player_order = self.current_game['player_order']
        alive_status = self.current_game['alive_status']
        for i in range(ind + 1, len(self.players) + ind + 1):
            if alive_status[i % len(player_order)] == "True":
                victim = player_order[i % len(player_order)]
                return victim
        return ""

    def get_thing(self, name):
        ind = self._index_of(name)
        return self.current_game['things'][ind]

    def has_killed(self, killer_name):
        victim_index = self._index_of(self.get_victim(killer_name))
        killer_index = self._index_of(killer_name)
        alive_status = self.current_game['alive_status']
        kill_count = self.current_game['kill_count']
        self.renew_thing(killer_name)
        kill_count[killer_index] = f"{ int(kill_count[killer_index]) + 1 }"
        alive_status[victim_index] = "False"
        print(f"{killer_name} hat {self.get_victim(killer_name)} getötet! Insgesamt tötete {killer_name} {kill_count[killer_index]}!")

    def get_dead(self):
        dead_people = []
        for person in self.current_game['player_order']:
            if not self.is_alive(person):
                dead_people.append(person)
        return dead_people

    def get_kill_count(self, player_name):
        return self.current_game['kill_count'][self._index_of(player_name)]

# =====================================================================================


def load_session(session_name):
    file_name = f"..//saves//{session_name}.json"
    if not exists(file_name):
        session = Session(session_name, [], [])
    else:
        with open(file_name, mode='r') as file:
            session_dict = json.load(file)

        running = session_dict['running']
        players = session_dict['players']
        things = session_dict['things']
        current_game = session_dict['current_game']

        session = Session(session_name, players, things)
        session.running = running
        session.current_game = current_game
    session.save()
    return session



