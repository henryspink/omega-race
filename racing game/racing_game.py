"""
Henry Spink, 2/5/24
game for applied computing 1/2
"""
# pylint: disable=line-too-long
#* imports
import os
import turtle
import sys
import time as timer
from datetime import datetime as time
from racing_game_classes import Player, SpriteAttributes, Util
from racing_game_constants import SCR

if not os.getcwd().endswith("final game"):                                  # check if the user is in the correct directory
    os.chdir("final game")                                                  # switch to the correct directory if not

#* setups
PLAYER_ONE = Player(                                                        # create player one
                name="PLAYER ONE",
                num=1,
                x=-45,
                y=330,
                heading=90,
                attributes=SpriteAttributes(
                                size=2.0,
                                color="blue",
                                shape="f1carPLAYER ONE",
                                sprite="f1car",
                                collision=True
                            )
            )
PLAYER_TWO = Player(                                                        # create player two
                name="PLAYER TWO",
                num=2,
                x=-45,
                y=270,
                heading=90,
                attributes=SpriteAttributes(
                                size=2.0,
                                color="orange",
                                shape="f1carPLAYER TWO",
                                sprite="f1car",
                                collision=True
                            )
            )
SPRITES = [PLAYER_ONE, PLAYER_TWO]                                              # iterable list of all the sprites
util = Util(PLAYER_ONE, PLAYER_TWO, SCR)                                        # utility class, also includes many subclasses
util.game_state = "init"                                                        # start running the game
#* game loop
while util.game_state != "quit":                                                # game is running
    try:
        match util.game_state:
            case "init":                                                        # initialisation of the game
                util.setup_screen()                                             # create the screen
                util.handle_keybinds()                                          # register keybindings
                total_laps: int = 10                                            # default to 10 laps needed to win
                util.sub.data.load()                                            # load the database, ready for any new entries
                for sprite in SPRITES:
                    sprite.construct()                                          # register the sprites
                    sprite.score.coins = util.sub.data.db[sprite.name]["coins"]
                util.sub.draw.menu()                                            # draw the menu
                util.game_state = "menu"
            case "menu":
                util.sub.update.menu()                                          # update the menu cars
            case "options menu":
                util.sub.draw.options()                                         # draw the options menu
                laps_input = turtle.numinput("Input", "Number of laps to win:") # the total number laps needed to win
                total_laps = int(laps_input) if laps_input is not None else 10  # default to 10 laps if no input is given
                PLAYER_ONE.score.total_laps = total_laps                        # pass in total laps needed to win
                PLAYER_TWO.score.total_laps = total_laps                        # pass in total laps needed to win
                util.handle_keybinds()                                          # reregister keybinds as they are lost when an input box is opened
                util.game_state = "menu"
            case "options":
                util.sub.draw.options()
                laps_input = turtle.numinput("Input", "Number of laps to win:") # the total number laps needed to win
                total_laps = int(laps_input) if laps_input is not None else 10  # default to 10 laps if no input is given
                PLAYER_ONE.score.total_laps = total_laps                        # pass in total laps needed to win
                PLAYER_TWO.score.total_laps = total_laps                        # pass in total laps needed to win
                util.handle_keybinds()                                          # reregister keybinds as they are lost when an input box is opened
                util.game_state = "menu"
            case "leaderboard load":
                util.sub.draw.reset()
                util.sub.data.draw()                                            # draw the leaderboard
                util.game_state = "leaderboard"
            case "menu game mode load":
                util.sub.draw.game_mode()                                       # get the number of players
                util.game_state = "menu game mode"
            case "menu player name load":
                util.sub.draw.player_names()                                    # allow the player to select their name
                util.game_state = "menu player name"
            case "menu player name":
                util.sub.update.name()
            case "menu sprite select load":
                util.sub.draw.sprite_select()                                   # allow the player to select their sprite
                util.game_state = "menu sprite select"
            case "menu sprite select":
                util.sub.update.sprite_menu()                                   # update the car sprite and colour on the selection screen
            case "load":
                util.handle_keybinds()                                          # register keybindings
                util.sub.draw.track()                                           # draw main game screen
                util.sub.draw.coins()                                           # draw the coins counter
                util.sub.update.coins()                                         # update the coins counter to show number of coins at start of game
                for sprite in SPRITES:                                          # update and render each of the players
                    sprite.update()
                    sprite.render()
                util.game_state = "countdown"
            case "countdown":                                                   # countdown to start of game
                util.sub.draw.countdown("3")                                    # 3
                timer.sleep(1)
                util.sub.draw.countdown("2")                                    # 2
                timer.sleep(1)
                util.sub.draw.countdown("1")                                    # 1
                timer.sleep(1)
                util.sub.draw.countdown("0")                                    # GO!
                timer.sleep(1)
                util.sub.draw.countdown("clear")                                # clear
                util.game_state = "start"                                       # game now running
            case "start":
                for sprite in SPRITES:
                    sprite.construct()                                          # register the sprites
                    sprite.timer.start_time = time.now()                        # start the timer
                util.game_start_time = time.now()                               # start the main game timer
                util.sub.update.game_start_time = time.now()                    # start the main game timer
                util.sub.draw.game_start_time = time.now()                      # start the main game timer
                util.spawn_coins()                                              # spawn the coins
                util.game_state = "game"
            case "game":                                                        # main game is in progress
                for sprite in SPRITES:                                          # update and render each of the players
                    sprite.update()
                    sprite.render()
                util.sub.update.update()                                        # spedo, timer, score, and collision checking
                util.coins()                                                    # update the coins
                util.check_end()                                                # check if game should end for any reason
            case "paused":
                pass
            case "end win":
                util.sub.data.save()                                            # save the database to a json file
                timer.sleep(5)
                util.sub.draw.stats()                                           # after 5 seconds of showing to the winner move the to game statistics
                util.game_state = "stats"
            case "stats":
                pass
            case _:
                pass
        SCR.update()
    except (KeyboardInterrupt, turtle.Terminator):
        util.game_state = "quit"

util.sub.data.save()
sys.exit(0)
