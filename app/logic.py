"""
This Module handles all the game-mechanics for the toeten-game
"""

import random
import json
from os.path import exists
from os import mkdir


class Session:
    """
    This Class handles all the game-mechanics for the toeten-game
    """
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
        """
        Returns a dict-representation of the session
        :return: a repr of the session as dict
        """
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
        create a new game from this session
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
        for _ in self.players:
            if len(new_game.get('available_things')) == 0:
                if len(self.things) == 0:
                    new_game.get('available_things').append("")
                else:
                    new_game['available_things'] = self.things.copy()

            thing = random.choice(new_game.get('available_things'))
            new_game.get('available_things').remove(thing)

            new_game.get('things').append(thing)
            new_game.get('alive_status').append("True")
            new_game.get('kill_count').append("0")

        return new_game

    def save(self):
        """
        save this session
        :return: None
        """
        if not exists("..//saves//"):
            mkdir("..//saves//")

        file_name = f"..//saves//{self.name}.json"
        with open(file_name, mode='w', encoding="utf-8") as file:
            file.write(json.dumps(self.as_dict()))
            print(f"Session.save: {json.dumps(self.as_dict())}")

    def start_new_game(self):
        """
        start a new game from this session
        :return: None
        """
        self.current_game = self.make_new_game()
        self.running = True
        self.save()

    def end_game(self):
        """
        End the game that is running in ths session if there is one
        :return: None
        """
        self.current_game = {}
        self.running = False
        self.save()

    # =====================================================================================

    # ========================== handle game mechanics ====================================

    def _index_of(self, name):
        """
        Returns the index of the player
        :param name: name of the the player as str
        :return: the index of the Player in player-order in the game if there is a
        running game, else None.
        """
        return self.current_game.get('player_order').index(name)

    def add_thing(self, thing):
        """
        Add a thing to this session. If there is a game running add the new thing
        to the running game.
        :param thing: the name of the thing as str
        :return: None.
        """
        self.things.append(thing)
        if self.running:
            self.current_game.get('available_things').append(thing)
            random.shuffle(self.current_game.get('available_things'))

    def add_player(self, person):
        """
        Add a player to the session.
        :param person: the name of the player to add
        :return: None
        """
        self.players.append(person)
        self.players.sort()

    def remove_player(self, player):
        """
        Remove a player from the session, if he exists
        :param player: the name of the player
        :return: None
        """
        print(f"remove '{player}' from {self.players}")
        self.players.remove(player)
        if self.running:
            ind = self._index_of(player)
            del self.current_game.get('player_order')[ind]
            del self.current_game.get('things')[ind]
            del self.current_game.get('alive_status')[ind]
            del self.current_game.get('kill_count')[ind]

    def get_players(self):
        """
        Returs a copy of the players of the current game.
        :return: a list with the names of the players
        """
        players_copy = self.current_game.get('player_order').copy()
        players_copy.sort()
        return players_copy

    def player_in_game(self, player):
        """
        Checks wether a player in the session is also in the current game,
        if it is running
        :param player: the name of the player
        :return: True if the player is in the game, else False
        """
        return player in self.get_players()

    def is_alive(self, name):
        """
        Checks wether a player is alive
        :param name: name of the player
        :return: True if the player is alive, else False
        """
        alive_status = self.current_game.get('alive_status')
        return alive_status[self._index_of(name)] == "True"

    def renew_thing(self, name):
        """
        renew the thing of a player.
        Randomly pick a new thing from available_things.
        :param name: name of the player
        :return: None
        """
        available_things = self.current_game.get('available_things')
        if len(available_things) == 0:
            available_things = self.things.copy()

        thing = random.choice(available_things)
        available_things.remove(thing)

        self.current_game.get('things')[self._index_of(name)] = thing

    def get_victim(self, name):
        """
        Find the victim of a player
        :param name: the name of the player
        :return: the name of the victim
        """
        ind = self._index_of(name)
        player_order = self.current_game.get('player_order')
        alive_status = self.current_game.get('alive_status')
        for i in range(ind + 1, len(self.players) + ind + 1):
            if alive_status[i % len(player_order)] == "True":
                victim = player_order[i % len(player_order)]
                return victim
        return ""

    def get_thing(self, name):
        """
        Get the murder-weapon of a player
        :param name: name of a player
        :return: name of the weapon
        """
        ind = self._index_of(name)
        return self.current_game.get('things')[ind]

    def has_killed(self, killer_name):
        """
        Call if a player has killed.
        Afterwards the victim of the player will be dead and the player will have a new weapon.
        :param killer_name: the name of the killer
        :return: None
        """
        victim_index = self._index_of(self.get_victim(killer_name))
        killer_index = self._index_of(killer_name)
        alive_status = self.current_game.get('alive_status')
        kill_count = self.current_game.get('kill_count')
        self.renew_thing(killer_name)
        kill_count[killer_index] = f"{ int(kill_count[killer_index]) + 1 }"
        alive_status[victim_index] = "False"
        print(f"{killer_name} hat {self.get_victim(killer_name)} getötet! "
              f"Insgesamt tötete {killer_name} {kill_count[killer_index]}!")

    def get_dead(self):
        """
        Returns a list of all the players that already have been killed.
        :return: the list of dead players
        """
        dead_people = []
        for person in self.current_game.get('player_order'):
            if not self.is_alive(person):
                dead_people.append(person)
        return dead_people

    def get_kill_count(self, player_name):
        """
        Get the number of players that a player has killed
        :param player_name: the name of the killer
        :return: the number of victims
        """
        return self.current_game.get('kill_count')[self._index_of(player_name)]

# =====================================================================================


def load_session(session_name):
    """
    load a session. If there already exists a save-file that corresponds to
    the session-name, return a session that has the same state as the save-
    file, else return a new session.
    To be used as factory-function for Sessions.
    :param session_name: the name of the session
    :return: a Session
    """
    file_name = f"..//saves//{session_name}.json"
    if not exists(file_name):
        session = Session(session_name, [], [])
    else:
        with open(file_name, mode='r', encoding="utf-8") as file:
            session_dict = json.load(file)

        running = session_dict.get('running')
        players = session_dict.get('players')
        things = session_dict.get('things')
        current_game = session_dict.get('current_game')

        session = Session(session_name, players, things)
        session.running = running
        session.current_game = current_game
    session.save()
    return session
