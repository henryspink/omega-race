"""
Henry Spink, 2/5/24
Constant and Variables file for game for applied computing 1/2
"""
# imports
import turtle

# constants
GAME_RUNNING: bool = True   # is the game running or not
d_trtl = turtle.Turtle()    # drawing turtle
s_trtl = turtle.Turtle()    # updates the score
t_trtl = turtle.Turtle()    # updates the timer
ll_trtl = turtle.Turtle()   # left lap turtle
lr_trtl = turtle.Turtle()   # right lap turtle
p_trtl = turtle.Turtle()    # pause screen turtle
m_trtl = turtle.Turtle()    # menu turtle
n1_trtl = turtle.Turtle()   # speedometer needle turtle
n2_trtl = turtle.Turtle()   # speedometer needle turtle
c_trtl = turtle.Turtle()    # coin turtle
TURTLES = [                 # all the turtles to allow for iteration
            d_trtl,
            s_trtl,
            t_trtl,
            ll_trtl,
            lr_trtl,
            p_trtl,
            m_trtl,
            n1_trtl,
            n2_trtl,
            c_trtl
        ]
SCR = turtle.Screen()       # game window

class WrongFileError(Exception):
    """
    Custom Exception for when the user runs the wrong file (i.e not racing_game.py)
    """

if __name__ == "__main__":
    raise WrongFileError(
                """YOU RAN THE WRONG FILE AGAIN 🤦
                Make sure you are running `racing_game.py`"""
                )
