from point import Point
from maze import Maze, Room
from creature import *
from typing import List
from rand import rand, pick
import re


def flush_input():
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    # for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)


class Game:
    def __init__(self):
        self.maps = []  # type: List[Maze]
        m = Maze(10, 10)
        m.generate()
        self.maps.append(m)
        self.downstairs = []  # type: List[Point]
        for r in range(len(m)):
            for c in range(len(r)):
                p = Point(r, c)
                room = m.getRoom(p)
                if room.feature.type == "downstairs":
                    self.downstairs.append(p)

        self.commands = {"move": self.move, "look": self.commandLook, "quit": self.commandQuit,
                         "alias": self.createAlias, "map": self.commandPlayerMap, "wizardmap": self.commandWizardMap,
                         "help": self.commandHelp, "dealias": self.commandDealias}
        self.aliases = {"north": "move north", "east": "move east", "south": "move south", "west": "move west",
                        "n": "move north", "e": "move east", "w": "move west", "s": "move south", "l": "look",
                        "down": "move down", "d": "move down", "up": "move up", "u": "move up"}

        self.player = Player()
        self.player.hp = self.player.maxhp = 10
        self.player_floor = 0
        self.player_pos = Point(rand(10), rand(10))
        self.playerRoom().creature = self.player
        self.playerMaps = []  # type: List[Maze]
        player_map = Maze(m.rows, m.cols)
        self.playerMaps.append(player_map)
        self.updatePlayerMap()
        self.creatures = [self.player]
        self.player_moved = True
        self.game_running = True
        self.processTime()

    def commandDealias(self, args):
        alias = ""
        try:
            alias = args[0]
        except IndexError:
            alias = ""

        if alias == "":
            print("Enter an alias name to delete. For a list of currently-defined aliases, type 'alias'.")
        elif alias not in self.aliases:
            print("%s is not defined as an alias. For a list of currently-defined aliases, type 'alias'.".format(alias))
        else:
            del(self.aliases[alias])
            print("Alias %s deleted.".format(alias))


    def commandHelp(self, args):
        command = ""
        try:
            command = args[0]
        except IndexError:
            command = ""

        if command == "":
            print("To play console-dungeon, enter a command at the prompt (ends with '>').")
            print("Available commands:")
            for cmd in self.commands:
                if cmd[0:6] != "wizard":
                    print("    %s".format(cmd))
            print("For more information about a command, type 'help <command>'")
            print("You can also enter a command alias as a shortcut to a command.")
            print("To see a list of aliases currently defined, type 'alias'.")
            print("Type 'help alias' for more information.")
        elif command in self.commands:
            try:
                with open("help/%s.help".format(command), "r") as f:
                    print(f.read())
            except FileNotFoundError:
                print("Help file for %s not found. Please alert the developer!".format(command))
        else:
            print("Unknown command: %s. Type 'help' for a list of commands.".format(command))

    def commandWizardMap(self, args):
        try:
            map = self.maps[int(args[0])]
        except (ValueError, IndexError):
            map = self.maps[self.player_floor]

        print(map)

    def updatePlayerMap(self):
        room = self.playerRoom()
        map = self.playerMaps[self.player_floor]
        if map.getRoom(self.player_pos) is None:
            map.setRoom(self.player_pos, self.playerRoom())
        for direction, delta in Room.moves.items():
            if room.exits[direction]:
                map.setRoom(self.player_pos + delta, self.maps[self.player_floor].getRoom(self.player_pos + delta))

    def createAlias(self, args):
        if len(args) == 0:
            print("Aliases:")
            for name, cmd in self.aliases.items():
                print("{}:{}".format(name, cmd))
            return

        name = args.pop(0)
        if len(args) == 0:
            if name in self.aliases:
                print("{}:{}".format(name, self.aliases[name]))
            else:
                print("{}: Not an alias".format(name))
            return

        cmd = args[0]
        if name in self.commands:
            print("'{}' is already a command".format(name))
        elif cmd not in self.commands:
            print("'{}': unknown command".format(cmd))
        else:
            if name in self.aliases:
                print("Replacing alias for '{}' (was: '{}')".format(name, self.aliases[name ]))
            self.aliases[name] = " ".join(args)

    def commandPlayerMap(self, args = None):
        print(self.playerMaps[self.player_floor])

    def playerRoom(self):
        return self.maps[self.player_floor].getRoom(self.player_pos)

    def playerCommand(self):
        self.player_moved = False
        cmd = ""
        while cmd == "":
            flush_input()
            cmd = input(self.prompt())
            cmd = re.sub(r"^ +", "", cmd)
            cmd = re.sub(r" +$", "", cmd)
        self.command(cmd)

    def printPlayerLookMap(self):
        room = self.playerRoom()
        floor = self.maps[self.player_floor]
        m = Maze(1, 1)
        m.setRoom(Point(0, 0), room)
        for direction, delta in Room.moves.items():
            if room.exits[direction]:
                m.setRoom(delta, floor.getRoom(self.player_pos + Room.moves[direction]))

        print(m)
        exits = []
        for direction, valid in room.exits:
            if valid:
                exits.push(direction)
        print("[Exits: %s]".format(", ".join(exits)))

    def prompt(self) -> str:
        return "HP: {}/{} >".format(self.player.hp, self.player.maxhp)

    def command(self, cmdstr: str):
        cmdstr = re.sub(r" +", " ", cmdstr)
        words = cmdstr.split(" ")
        cmd = words.pop(0)
        if cmd in self.aliases:
            words2 = self.aliases[cmd].split(" ")
            cmd = words2.pop(0)
            words = words2 + words

        if cmd in self.commands:
            self.commands[cmd](words)
        else:
            print("Unknown command: %s" % cmd)

    def commandQuit(self, args = None):
        print("Quitting")
        self.game_running = False

    def move(self, args: List[str]):
        moveOK = True
        direction = args[0]
        room = self.playerRoom()
        if direction not in Room.directions and direction not in room.exits:
            print("You don't know how to move {}wards".format(direction))
            moveOK = False
        elif direction not in room.exits:
            print("The wall refuses to move.")
            moveOK = False
        else:
            if direction == "up":
                if room.feature is not None and room.feature.type == "upstairs":
                    moveOK = True
            elif direction == "down":
                if room.feature is not None and room.feature.type == "downstairs":
                    moveOK = True
            else:
                destPos = self.player_pos + Room.moves[direction]
                destRoom = self.maps[self.player_floor].getRoom(destPos)
                if destRoom.creature is not None:
                    print("The " + destRoom.creature.name + " is in the way!")
                    moveOK = False

        if moveOK:
            room.creature = None
            if direction == "up":
                self.player_floor -= 1
            elif direction == "down":
                self.player_floor += 1
                if self.player_floor == len(self.maps):
                    m = Maze(self.maps[0].rows, self.maps[0].cols)
                    m.generate()
                    self.maps.append(m)

                    m = Maze(m.rows, m.cols)
                    self.playerMaps.append(m)
            else:
                self.player_pos += Room.moves[direction]
            room = self.playerRoom()
            room.creature = self.player
            self.updatePlayerMap()
            self.player_moved = True
            self.player.waitTime = 100
            self.processTime()
        else:
            self.playerCommand()

    def commandLook(self, args = None):
        self.printPlayerLookMap()
        self.playerCommand()

    def processTime(self):
        while self.game_running:
            for creature in self.creatures:
                if creature.waitTime > 0:
                    creature.waitTime -= creature.speed

            for creature in self.creatures:
                while creature.waitTime <= 0:
                    self.actCreature(creature)
                    if not self.game_running:
                        break

    def actCreature(self, creature: Creature):
        if creature.player:
            if self.player_moved:
                self.printPlayerLookMap()
            self.playerCommand()
        else:
            creature.waitTime = 100  # creature logic, tbd


if __name__ == "__main__":
    g = Game()
