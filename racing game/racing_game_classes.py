"""
Henry Spink, 2/5/24
Classes file for game for applied computing 1/2
"""
# pylint: disable=line-too-long,too-many-lines
#* imports
import os
# install pandas if not already installed
try:
    import pandas as pd
except ImportError:
    os.system("py -m pip install pandas")
    os.system("py -m pip install pandas-stubs")
finally:
    import pandas as pd
import turtle
import dataclasses
import math
import random
import json
import datetime
from datetime import datetime as time
from racing_game_constants import SCR, TURTLES, d_trtl, s_trtl, t_trtl, ll_trtl, lr_trtl, p_trtl, m_trtl, n1_trtl, n2_trtl, c_trtl, WrongFileError

#* classes
#?   dataclasses
@dataclasses.dataclass
class SpriteAttributes:
    """
    defines some visual properties of the sprite
    """
    size: float         # size of the sprite
    color: str          # colour of the sprite
    shape: str          # shape of the sprite
    sprite: str         # the sprite of the sprite
    collision: bool     # whether collision is enabled for the sprite

@dataclasses.dataclass
class _PlayerScore:
    """
    timer and lap counter for the player
    """
    total_laps: int             # amount of laps required for a player to win
    timer: int                  # unused
    laps: int                   # number of laps completed
    won: bool                   # whether the player has won or not
    pos: str                    # position (1st, 2nd, draw)
    collisions: int             # number of collisions with the other player
    colliding: bool             # if the player is currently colliding with the other player
    coins: int                  # number of coins collected
    lap_marker_top: bool        # top fnish line marker
    lap_marker_bottom: bool     # bottom finish line
    lap_marker_left: bool       # left finish line
    lap_marker_right: bool      # right finish line

@dataclasses.dataclass
class _Movement:
    """
    movement properties for the player
    """
    rotating_left: bool     # ----------
    rotating_right: bool    # keybind properties
    accelerating: bool      # to define where the player should move
    decel: bool             # ----------
    timer: int              # unused
    time_accel: int         # amount of time the player has been accelerating for (pos direction)
    time_decel: int         # amount of time the player has been decelerating for (neg direction)
    accel: int              # acceleration factor

@dataclasses.dataclass
class _Timer:
    """
    extra timing properties
    """
    start_time: time                # timestamp of the lap start time
    end_time: time                  # timestamp of the lap end time
    lap_time: datetime.timedelta    # time taken to complete a lap
    laps: list                      # list of all the lap times (index is lap number)

#?   object classes
class Sprite:
    """
    Sprite Class

    Parent class for all sprites used in the game
    """
    def __init__(
            self,
            x: float = 0,
            y: float = 0,
            heading: float = 90,
            attributes: SpriteAttributes = SpriteAttributes(
                                                size=1.0,
                                                color="white",
                                                shape="square",
                                                sprite="square",
                                                collision=True
                                                )
        ):
        """
        define variables - does not make sprite, use `construct()`
        """
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.heading = heading
        self.attr = attributes
        self.active = True
        self.turtle = turtle.Turtle()

    def construct(self) -> None:
        """
        Constructs the sprite and registers it

        This method creates a test sprite object and registers it with the name "hi".
        
        Parameters:
        None

        Returns:
        None
        """
        # HI sprite
        sprite_obj = turtle.Shape("compound")
        sprite_obj.addcomponent([(0,0),(-5,0),(-5,5),(-5,-5),(-5,0),(0,0),(0,5),(0,-5)], "", "white")
        sprite_obj.addcomponent([(5,-5),(5,5)], "", "white")
        turtle.register_shape("hi", sprite_obj)

    def update(self) -> None:
        """
        Updates the location and speed of the sprite.

        This method is responsible for updating the position of the sprite based on its current speed (dx, dy).
        It also performs collision detection and handles collisions with the edges of the screen.

        Returns:
            None
        """
        # movement
        self.x += self.dx
        self.y += self.dy
        # collision detection
        collided, where = self._check_collision()
        if collided:
            match where:
                case "top":         # collision with top of screen
                    self.y = 450
                case "bottom":      # collision with bottom of screen
                    self.y = -450
                case "right":       # collision with right side of screen
                    self.x = 900
                case "left":        # collision with left side of screen
                    self.x = -900
                case _:
                    pass

    def _check_collision(self) -> tuple[bool, str|None]:
        """
        check if sprite is off the screen

        returns a tuple of (True, "top"|"bottom"|"left"|"right") if colliding
        or a tuple of (False, "nowhere") if not colliding
        or a tuple of (False, None) if collision is not enabled for the sprite
        """
        if self.attr.collision:
            if self.x > (SCR.window_width()/2) - (22*self.attr.size):   # right border
                return (True, "right")
            if self.x < (SCR.window_width()/-2) + (22*self.attr.size):  # left border
                return (True, "left")
            if self.y > (SCR.window_height()/2) - (22*self.attr.size):  # top border
                return (True, "top")
            if self.y < (SCR.window_height()/-2) + (22*self.attr.size): # bottom border
                return (True, "bottom")
            return (False, "nowhere")
        return (False, None)

    def render(self) -> None:
        """
        Updates the location and visuals of the sprite on the screen

        Parameters:
            None

        Returns:
            None
        """
        if self.active:
            self.turtle.hideturtle()
            self.turtle.clear()
            self.turtle.penup()
            self.turtle.goto(self.x, self.y)
            self.turtle.seth(self.heading)
            self.turtle.shapesize(self.attr.size)
            self.turtle.shape(self.attr.shape)
            self.turtle.color(self.attr.color)
            self.turtle.stamp()

class Player(Sprite):
    """
    Player Class

    Child class of 'Sprite', controllable by the player
    """
    def __init__(
            self,
            x: float = 0,
            y: float = 0,
            heading: float = 90,
            attributes: SpriteAttributes = SpriteAttributes(
                                                size=1.0,
                                                color="white",
                                                shape="circle",
                                                sprite="circle",
                                                collision=True
                                            ),
            name: str = "PLAYER ONE",
            num: int = 1
            ) -> None:
        super().__init__(x=x, y=y, heading=heading, attributes=attributes)
        self.score = _PlayerScore(
                        timer=0,
                        total_laps=10,
                        laps=0,
                        won=False,
                        pos="Draw",
                        collisions=0,
                        colliding=False,
                        coins=0,
                        lap_marker_bottom=False,
                        lap_marker_top=False,
                        lap_marker_right=False,
                        lap_marker_left=False
                    )
        self.movement = _Movement(
                            rotating_left=False,
                            rotating_right=False,
                            accelerating=False,
                            decel=False,
                            timer=0,
                            time_accel=0,
                            time_decel=0,
                            accel=2
                        )
        self.timer = _Timer(
                        start_time=time.now(),
                        end_time=time.now(),
                        lap_time=datetime.timedelta(seconds=0),
                        laps=[]
                    )
        self.name = name            # name of the player
        self.ax: float = 0          # acceleration delta in the x directio
        self.ay: float = 0          # accleration delta in the y direction
        self.speed: float = 0       # speed of the player in "kmph"
        self.player_num: int = 2    # total number of players playing
        self.num: int = num         # the player id of this player instance (either 1 or 2)

    def _main_f1(self) -> turtle.Shape:
        """
        f1 car sprite going straight
        
        Parameters:
            None

        Returns:
            the turtle shape object of the f1 car
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # front spoiler
            [(20,0),(20,10),(17.5,10),(17.5,1.75),(20,0),(17.5,-1.75),(17.5,-10),(20,-10),(20,0)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # main body
            [(-15,0),(-15,3.5),(-10,3.5),(-7.5,7.5),(1,7.5),(10,3.5),(15,3.5),(20,0),(15,-3.5),(10,-3.5),(1,-7.5),(-7.5,-7.5),(-10,-3.5),(-15,-3.5),(-15,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # window
            [(-4,0),(-4,2.5),(1,2.5),(5,0),(1,-2.5),(-4,-2.5)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-10,7),(-10,11),(-17,11),(-17,10),(-15,10),(-15,7),(-12,7),(-12,3.5),(-12,7),(-14,7),(-14,3.5),(-14,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-10,-7),(-10,-11),(-17,-11),(-17,-10),(-15,-10),(-15,-7),(-12,-7),(-12,-3.5),(-12,-7),(-14,-7),(-14,-3.5),(-14,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(10,7),(10,10),(16,10),(16,7),(14,7),(14,3.5),(14,7),(12,7),(12,3.5),(12,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(10,-7),(10,-10),(16,-10),(16,-7),(14,-7),(14,-3.5),(14,-7),(12,-7),(12,-3.5),(12,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # back spoiler
            [(-15,0),(-15,10),(-20,10),(-20,-10),(-15,-10),(-15,0)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _right_f1(self) -> turtle.Shape:
        """
        f1 car sprite going right
        
        Parameters:
            None

        Returns:
            the turtle shape object of the f1 car
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # front spoiler
            [(20,0),(20,10),(17.5,10),(17.5,1.75),(20,0),(17.5,-1.75),(17.5,-10),(20,-10),(20,0)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # main body
            [(-15,0),(-15,3.5),(-10,3.5),(-7.5,7.5),(1,7.5),(10,3.5),(15,3.5),(20,0),(15,-3.5),(10,-3.5),(1,-7.5),(-7.5,-7.5),(-10,-3.5),(-15,-3.5),(-15,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # window
            [(-4,0),(-4,2.5),(1,2.5),(5,0),(1,-2.5),(-4,-2.5)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-10,7),(-10,11),(-17,11),(-17,10),(-15,10),(-15,7),(-12,7),(-12,3.5),(-12,7),(-14,7),(-14,3.5),(-14,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-10,-7),(-10,-11),(-17,-11),(-17,-10),(-15,-10),(-15,-7),(-12,-7),(-12,-3.5),(-12,-7),(-14,-7),(-14,-3.5),(-14,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(10,7),(10,10),(16,10),(16,7),(14,7),(14,3.5),(14,7),(12,7),(12,3.5),(12,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(10,-7),(10,-10),(16,-10),(16,-7),(14,-7),(14,-3.5),(14,-7),(12,-7),(12,-3.5),(12,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # back spoiler
            [(-15,0),(-15,10),(-20,10),(-20,-10),(-15,-10),(-15,0)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _left_f1(self) -> turtle.Shape:
        """
        f1 car sprite going left
        
        Parameters:
            None

        Returns:
            the turtle shape object of the f1 car
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # front spoiler
            [(20,0),(20,10),(17.5,10),(17.5,1.75),(20,0),(17.5,-1.75),(17.5,-10),(20,-10),(20,0)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # main body
            [(-15,0),(-15,3.5),(-10,3.5),(-7.5,7.5),(1,7.5),(10,3.5),(15,3.5),(20,0),(15,-3.5),(10,-3.5),(1,-7.5),(-7.5,-7.5),(-10,-3.5),(-15,-3.5),(-15,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # window
            [(-4,0),(-4,2.5),(1,2.5),(5,0),(1,-2.5),(-4,-2.5)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-10,7),(-10,11),(-17,11),(-17,10),(-15,10),(-15,7),(-12,7),(-12,3.5),(-12,7),(-14,7),(-14,3.5),(-14,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-10,-7),(-10,-11),(-17,-11),(-17,-10),(-15,-10),(-15,-7),(-12,-7),(-12,-3.5),(-12,-7),(-14,-7),(-14,-3.5),(-14,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(10,7),(10,10),(16,10),(16,7),(14,7),(14,3.5),(14,7),(12,7),(12,3.5),(12,7)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(10,-7),(10,-10),(16,-10),(16,-7),(14,-7),(14,-3.5),(14,-7),(12,-7),(12,-3.5),(12,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # back spoiler
            [(-15,0),(-15,10),(-20,10),(-20,-10),(-15,-10),(-15,0)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _main_ute(self) -> turtle.Shape:
        """
        ute sprite going straight
        
        Parameters:
            None

        Returns:
            the turtle shape object of the ute
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # main body
            [(-20,0),(-20,10),(0,10),(20,10),(20,-10),(0,-10),(-20,-10),(-20,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # truck bed
            [(-19,0),(-19,9),(-7,9),(-7,-9),(-19,-9),(-19,0)],
            "black",
            "black"
        )
        obj.addcomponent(   # window
            [(-6,9),(7,9),(7,-9),(-6,-9),(-6,7),(3,7),(3,-7),(-6,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-17,15),(-9,15),(-9,10),(-17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-17,-15),(-9,-15),(-9,-10),(-17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(17,15),(9,15),(9,10),(17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(17,-15),(9,-15),(9,-10),(17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # front top stripe
            [(7,6),(20,6),(20,4),(7,4),(7,6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # front bottom stripe
            [(7,-6),(20,-6),(20,-4),(7,-4),(7,-6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # middle stripe
            [(-6,-2),(3,-2),(3,2),(-6,2),(-6,-2)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _right_ute(self) -> turtle.Shape:
        """
        ute sprite going right
        
        Parameters:
            None

        Returns:
            the turtle shape object of the ute
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # main body
            [(-20,0),(-20,10),(0,10),(20,10),(20,-10),(0,-10),(-20,-10),(-20,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # truck bed
            [(-19,0),(-19,9),(-7,9),(-7,-9),(-19,-9),(-19,0)],
            "black",
            "black"
        )
        obj.addcomponent(   # window
            [(-6,9),(7,9),(7,-9),(-6,-9),(-6,7),(3,7),(3,-7),(-6,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-17,15),(-9,15),(-9,10),(-17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-17,-15),(-9,-15),(-9,-10),(-17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(17,15),(9,15),(9,10),(17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(17,-15),(9,-15),(9,-10),(17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # front top stripe
            [(7,6),(20,6),(20,4),(7,4),(7,6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # front bottom stripe
            [(7,-6),(20,-6),(20,-4),(7,-4),(7,-6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # middle stripe
            [(-6,-2),(3,-2),(3,2),(-6,2),(-6,-2)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _left_ute(self) -> turtle.Shape:
        """
        ute sprite going left
        
        Parameters:
            None

        Returns:
            the turtle shape object of the ute
        """
        obj = turtle.Shape("compound")
        obj.addcomponent(   # main body
            [(-20,0),(-20,10),(0,10),(20,10),(20,-10),(0,-10),(-20,-10),(-20,0)],
            "white",
            "white"
        )
        obj.addcomponent(   # truck bed
            [(-19,0),(-19,9),(-7,9),(-7,-9),(-19,-9),(-19,0)],
            "black",
            "black"
        )
        obj.addcomponent(   # window
            [(-6,9),(7,9),(7,-9),(-6,-9),(-6,7),(3,7),(3,-7),(-6,-7)],
            "black",
            "black"
        )
        obj.addcomponent(   # top left wheel
            [(-17,15),(-9,15),(-9,10),(-17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # bottom left wheel
            [(-17,-15),(-9,-15),(-9,-10),(-17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # top right wheel
            [(17,15),(9,15),(9,10),(17,10)],
            "black",
            "black"
        )
        obj.addcomponent(   # botttom right wheel
            [(17,-15),(9,-15),(9,-10),(17,-10)],
            "black",
            "black"
        )
        obj.addcomponent(   # front top stripe
            [(7,6),(20,6),(20,4),(7,4),(7,6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # front bottom stripe
            [(7,-6),(20,-6),(20,-4),(7,-4),(7,-6)],
            self.attr.color,
            self.attr.color
        )
        obj.addcomponent(   # middle stripe
            [(-6,-2),(3,-2),(3,2),(-6,2),(-6,-2)],
            self.attr.color,
            self.attr.color
        )
        return obj

    def _move(self) -> None:
        """
        Handles all movement of the player:
        - turning left/right
        - moving forwards and backwards
        - stopping

        Parameters:
        None

        Returns:
        None
        """

        # respond to keypresses
        if self.movement.rotating_left:                                                 # turn left
            self.heading += 2
            self.attr.shape = f"{self.attr.sprite}{self.name}left"

        if self.movement.rotating_right:                                                # turn right
            self.heading -= 2
            self.attr.shape = f"{self.attr.sprite}{self.name}right"

        if self.movement.accelerating:                                                  # forwards
            if self.movement.time_decel < 0:                                            # start accel from reversing
                self.movement.time_accel = 0                                            # ensure no forwards slipping through
                self.movement.time_decel += self.movement.accel * 5
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_decel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_decel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02
            else:                                                                       # just accel from stopped
                self.attr.shape = f"{self.attr.sprite}{self.name}"
                self.movement.time_decel = 0                                            # ensure no backward slipping through
                if self.movement.time_accel < 1500:                                     # forward speed capped to 1500
                    self.movement.time_accel += self.movement.accel
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_accel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_accel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02

        elif self.movement.decel:                                                       # backwards
            if self.movement.time_accel > 0:                                            # finish moving forward
                self.movement.time_decel = 0                                            # ensure no backward slipping through
                self.movement.time_accel -= self.movement.accel * 5
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_accel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_accel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02
            else:                                                                       # start moving back
                self.movement.time_accel = 0                                            # ensure no forward slipping through
                if self.movement.time_decel > -500:                                     # reversing speed capped to 700
                    self.movement.time_decel -= self.movement.accel
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_decel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_decel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02

        if self.movement.accelerating and self.movement.decel:                          # both forwards and backwards keys pressed
            if self.movement.time_accel > 0 and self.movement.time_decel == 0:          # moving forward
                self.movement.time_accel -= self.movement.accel * 5
                if self.movement.time_accel < 5:
                    self.movement.time_accel = 0                                        # catch edge case where it goes negative
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_accel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_accel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02
            elif self.movement.time_decel < 0 and self.movement.time_accel == 0:        # moving backward
                self.movement.time_decel += self.movement.accel * 5
                if self.movement.time_decel > -5:
                    self.movement.time_decel = 0                                        # catch edge case where it goes positive
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_decel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_decel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02

        if not self.movement.accelerating and not self.movement.decel:                  # no forwards or backwards - stop movement
            if self.movement.time_accel > 0 and self.movement.time_decel == 0:          # moving forward
                self.movement.time_accel -= int(self.movement.accel * 2.5)
                if self.movement.time_accel < 5:
                    self.movement.time_accel = 0                                        # catch edge case where it goes negative
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_accel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_accel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02
            elif self.movement.time_decel < 0 and self.movement.time_accel == 0:        # moving backward
                self.movement.time_decel += int(self.movement.accel * 2.5)
                if self.movement.time_decel > -5:
                    self.movement.time_decel = 0                                        # catch edge case where it goes positive
                self.ax = (self.ax + 0.75 * math.sin(math.radians(self.heading)) * self.movement.time_decel)/2
                self.ay = (self.ay - 0.75 * math.cos(math.radians(self.heading)) * self.movement.time_decel)/2
                self.x += self.ax * 0.02
                self.y += self.ay * 0.02

    def _collision(self) -> None:
        """
        Handles all collision of the player with the screen and track.
        Does not handle collision with other players.
        """
        # collision detection
        #   with screen edge
        collided, where = self._check_collision()
        if collided:
            self.movement.time_accel = 0
            self.movement.time_decel = 0
            match where:
                case "top":         # collision with top of screen
                    self.y = (SCR.window_height()/2) - (22*self.attr.size)
                case "bottom":      # collision with bottom of screen
                    self.y = (-SCR.window_height()/2) + (22*self.attr.size)
                case "right":       # collision with right side of screen
                    self.x = (SCR.window_width()/2) - (22*self.attr.size)
                case "left":        # collision with left side of screen
                    self.x = (-SCR.window_width()/2) + (22*self.attr.size)
                case _:
                    pass
        #   with track
        if self._off_track():
            if self.movement.time_accel > 0 and self.movement.time_decel == 0:      # moving forwards
                if self.movement.time_accel > 100:
                    self.movement.time_accel -= 20
                    self.movement.accel = 1
                    self.heading += random.randint(-4,4)                            # makes it harder to control on grass
            elif self.movement.time_decel < 0 and self.movement.time_accel == 0:    # moving backwards
                if self.movement.time_decel < -100:
                    self.movement.time_decel += 20
                    self.movement.accel = 1
                    self.heading += random.randint(-4,4)                            # makes it harder to control on grass
            else:
                pass
        else:                                                                       # definitely on the track and will run every frame
            if self.movement.time_accel > 500:                                      # slower acceleration after 100"kmph" (500 frames of accelerating)
                self.movement.accel = 2
            else:
                self.movement.accel = 3

    def _off_track(self) -> bool:
        """
        Checks if the player is on the track or not.
        
        Returns:
            True if the player is off the track, else False.
        """
        x = round(self.x)
        y = round(self.y)
        dist_left = ((((x+450)**2)+((y-50)**2))**(1/2))
        dist_right = ((((x-450)**2)+((y-50)**2))**(1/2))
        # conditions
        on_track_straight = ((200 < y < 400) and (-450 <= x <= 450)) or ((-300 < y < -100) and (-450 <= x <= 450))  # box encasing the straights of the track at the top and bottom
        on_track_curve_left = (x <= -450) and (150 < dist_left < 350)                                               # checks whether the distance between the player and the origin of the left semi-circle is within the range of the track
        on_track_curve_right = (x >= 450) and (150 < dist_right < 350)                                              # checks whether the distance between the player and the origin of the left semi-circle is within the range of the track
        # returns
        if not on_track_straight and not on_track_curve_left and not on_track_curve_right:
            return True     # player is off the track
        return False        # player is on the track

    def _win_condition(self) -> None:
        """
        Checks if the player has won the game.

        If the number of laps completed by the player is greater than or equal to the total number of laps,
        sets the `won` attribute of the `score` object to True.

        Returns:
            None
        """
        if self.score.laps >= self.score.total_laps:
            self.score.won = True
            return

    def _score(self) -> None:
        """
        Update the score/num of laps, and the times for each lap.
.
        It checks if the player has passed through the lap markers and the finish line, and updates the score accordingly.
        It also calculates and stores the lap times for the stats screen.

        Returns:
            None
        """
        if not self._off_track() and (-10 < round(self.x) < 10) and (round(self.y)>0):      # top marker
            self.score.lap_marker_top = True
        elif not self._off_track() and (-10 < round(self.x) < 10) and (round(self.y)<0):    # bottom marker
            self.score.lap_marker_bottom = True
        elif not self._off_track() and (-10 < round(self.y) < 10) and (round(self.x)<0):    # left marker
            self.score.lap_marker_left = True
        elif not self._off_track() and (-10 < round(self.y) < 10) and (round(self.x)>0):    # right marker
            self.score.lap_marker_right = True
        else:
            pass
        if ((sum([                                                                          # the sum function will return the number of True values in the list
                self.score.lap_marker_top,
                self.score.lap_marker_bottom,
                self.score.lap_marker_left,
                self.score.lap_marker_right
                ]) >= 3)                                                                    # must get at least 3 of the 4 markers for a lap to be counted
            and not self._off_track() and (-10 < round(self.x) < 10) and (round(self.y)>0)  # lap is only counted when on the track and passing through the finish line
            ):
            self.score.laps += 1
            self.score.lap_marker_top = False                                               # reset all markers
            self.score.lap_marker_bottom = False
            self.score.lap_marker_left = False
            self.score.lap_marker_right = False
            self.timer.end_time = time.now()
            lap_time = self.timer.end_time-self.timer.start_time
            self.timer.laps.append(lap_time)                                                # update list of lap times for stats
            self.timer.start_time = time.now()
            self._win_condition()                                                           # check if the player won
        self.timer.lap_time = time.now()-self.timer.start_time                              # running lap timer to display while game is running

    def _spedo(self) -> None:
        """
        Constantly update the speed value to display on the speedometer.

        This method calculates the speed based on the time acceleration and deceleration values
        and updates the `speed` attribute of the player. The speed value is rounded to the nearest
        integer and multiplied by 0.2 to get a psuedo "kilometers per hour" value

        Args:
            None

        Returns:
            None
        """
        self.speed = round(abs(self.movement.time_accel - self.movement.time_decel) * 0.2)

    def construct(self) -> None:
        """
        Register all vehicle sprites.

        This method registers the all the vehicle sprites for the player. It uses the `_main_<car name>()`,
        `_left_<car name>()`, and `_right_<car name>()` methods to generate the shapes for the car sprites.
        It also calls the `construct()` method of the super class to ensure that the "HI" sprite is also registered.

        Returns:
            None
        """
        turtle.register_shape(f"f1car{self.name}", self._main_f1())
        turtle.register_shape(f"f1car{self.name}left", self._left_f1())
        turtle.register_shape(f"f1car{self.name}right", self._right_f1())
        turtle.register_shape(f"ute{self.name}", self._main_ute())
        turtle.register_shape(f"ute{self.name}left", self._left_ute())
        turtle.register_shape(f"ute{self.name}right", self._right_ute())
        super().construct()     # make sure "HI" sprite is registered

    def update(self) -> None:
        """
        Update the Player to a new state.

        This method updates the state of the Player object. It does not change anything visually on the screen.
        To update the visual representation of the Player, use the `render()` method.

        This method performs the following actions:
        - Moves the player based on input.
        - Checks if the player has collided with anything.
        - Updates the score and lap times for the player.
        - Updates the speedometer value internally.

        Returns:
        None
        """
        self._move()        # moved the player based off input
        self._collision()   # checks if the player has collided with anything
        self._score()       # updates the score and lap times for the player
        self._spedo()       # updates the speedometer value (internally)

    def player_collision(self, player: Sprite) -> bool:
        """
        Check if a player is colliding with another player.

        Args:
            player (Sprite): The player to check collision with.

        Returns:
            bool: True if the provided player is colliding with the player, False otherwise.
        """
        x = round(self.x)
        y = round(self.y)
        px = round(player.x)
        py = round(player.y)
        valid_state = ((player.attr.collision) and (self.attr.collision)) and ((player.active) and (self.active))   # check if both players are active (rendered on the screen) and have collision enabled
        if (px-50 <= x <= px+50) and (py-50 <= y <= py+50) and valid_state:                                         # collision with a box 50px by 50px around the other player
            # need to make something happen when they collide - for now just says hi
            self.attr.shape = "hi"
            if not self.score.colliding: # allow for accurate collision count - only goes up by 1 for each collision, doesnt keep going up if they stay ontop of each other
                self.score.collisions += 1
            self.score.colliding = True
            return True
        self.score.colliding = False
        return False

    def rotate_left_start(self) -> None:
        """
        start turning left
        """
        self.movement.rotating_left = True

    def rotate_left_stop(self) -> None:
        """
        stop turning left
        """
        self.movement.rotating_left = False

    def rotate_right_start(self) -> None:
        """
        start turning right
        """
        self.movement.rotating_right = True

    def rotate_right_stop(self) -> None:
        """
        stop turning right
        """
        self.movement.rotating_right = False

    def accelerate_start(self) -> None:
        """
        start accelerating
        """
        self.movement.accelerating = True

    def accelerate_stop(self) -> None:
        """
        stop accelerating
        """
        self.movement.accelerating = False

    def decel_start(self) -> None:
        """
        start deceling
        """
        self.movement.decel = True

    def decel_stop(self) -> None:
        """
        stop deceling
        """
        self.movement.decel = False

    def best_lap(self) -> str:
        """
        Returns the time of the best lap the player has completed.

        This method is a helper function for the score area updater.

        Returns:
            str: The time of the best lap in the format 'hh:mm:ss.mms'.
                 If no laps have been completed, returns '-         '.
        """
        if not self.timer.laps:
            return "-         "
        lap_time = min(self.timer.laps)
        return str(lap_time)[:-3] # cut off the last 3 digits of the time bc dont need microsecond accuracy - millisecond is fine

    def collect_coin(self, coin) -> None:
        """
        Collect a coin
        - Hide the coin
        - Update the number of coins the player has collected
        """
        coin.hide()
        self.score.coins += 1

    def check_collision(self, sprite: Sprite) -> bool:
        """
        Check if the player is colliding with a sprite.

        Arguments:
            sprite (Sprite): the sprite to check

        Returns:
            bool: whether the player is colliding with the sprite
        """
        if sprite.attr.collision:                                                               # check that collision is enabled for the given sprite
            if (self.x-50 <= sprite.x <= self.x+50) and (self.y-50 <= sprite.y <= self.y+50):   # collision with a box 50px by 50px around the sprite
                return True
        return False

    def reset(self) -> None:
        """
        Reset all values to original state.

        Parameters:
            None
        
        Returns:
            None
        """
        if self.num == 1:
            super().__init__(x=-45, y=330, heading=90, attributes=self.attr)
        else:
            super().__init__(x=-45, y=270, heading=90, attributes=self.attr)
        self.score = _PlayerScore(
                        timer=0,
                        total_laps=self.score.total_laps,
                        laps=0,
                        won=False,
                        pos="Draw",
                        collisions=0,
                        colliding=False,
                        coins=self.score.coins,
                        lap_marker_bottom=False,
                        lap_marker_top=False,
                        lap_marker_right=False,
                        lap_marker_left=False
                    )
        self.movement = _Movement(
                            rotating_left=False,
                            rotating_right=False,
                            accelerating=False,
                            decel=False,
                            timer=0,
                            time_accel=0,
                            time_decel=0,
                            accel=2
                        )
        self.timer = _Timer(
                        start_time=time.now(),
                        end_time=time.now(),
                        lap_time=datetime.timedelta(seconds=0),
                        laps=[]
                    )
        self.ax = 0
        self.ay = 0
        self.speed = 0

class Coin(Sprite):
    """
    Coin Class
    Sub-class of Sprite, used to create coins for the player to collect on the track
    """
    def __init__(
            self,
            x: float = 0,
            y: float = 0,
            attributes: SpriteAttributes = SpriteAttributes(
                                                size=1.0,
                                                color="yellow",
                                                shape="circle",
                                                sprite="circle",
                                                collision=True
                                            )
        ) -> None:
        super().__init__(x=x, y=y, heading=0, attributes=attributes) # pass all the args on through

    def show(self) -> None:
        """
        Show the coin on the screen.

        This method shows the coin on the screen by setting the `active` attribute to True.
        Will usually be called a while after the player collects the coin, when it is set to respawn

        Returns:
            None
        """
        self.active = True

    def hide(self) -> None:
        """
        Hide the coin from the screen.

        This method hides the coin from the screen by setting the `active` attribute to False.
        Will usually be called when the player collects the coin.

        Returns:
            None
        """
        self.active = False
        self.turtle.clear()

#?   util classes
class Background:
    """
    General UI elements and racetrack
    """
    def ui_omega_race(self) -> None:
        """
        Draw UI for omega race game
        """
        d_trtl.pencolor("white")
        d_trtl.penup()
        d_trtl.goto((-250,150))     # start inside box
        d_trtl.pendown()
        d_trtl.goto(-250,-150)
        d_trtl.goto(250,-150)
        d_trtl.goto(250,150)
        d_trtl.goto(-250,150)       # finish inside box
        d_trtl.penup()
        d_trtl.goto(0,-150)         # Bottom finish line
        d_trtl.pendown()
        d_trtl.goto(0,-300)
        d_trtl.penup()
        d_trtl.goto(0,150)          # Top finish line
        d_trtl.pendown()
        d_trtl.goto(0, 300)
        d_trtl.penup()
        d_trtl.goto(0, 100)         # Title
        d_trtl.write("Omega Race", False, align="center", font=("Arial", 25, "normal"))
        d_trtl.goto(-180,20)        # Label for player one score
        d_trtl.write("Player 1", align="center", font=("Arial", 15, "normal"))
        d_trtl.goto(180,20)         # Label for player two score
        d_trtl.write("Player 2", align="center", font=("Arial", 15, "normal"))

    def _hgoto(self, x: int|float, y: int|float, t: turtle.Turtle = d_trtl) -> None:
        """
        Version of `turtle.Turtle().goto()` that does not draw a line.
        Puts the pen down after completion so be careful in subsequent movements

        Args:
            x (int|float): The x-coordinate to move to.
            y (int|float): The y-coordinate to move to.
            t (turtle.Turtle): The turtle object to perform the movement. Defaults to d_trtl.

        Returns:
            None
        """
        t.pu()
        t.goto(x, y)
        t.pd()

    def _red_dash_circle(self, rad: int, extent: int = 360, step: int = 5) -> None:
        """
        Helper function to create a red dashed circle around turns.

        Parameters:
        - rad (int): The radius of the circle.
        - extent (int): The extent of the circle in degrees. Default is 360.
        - step (int): The length of each colour segment. Default is 5.

        Returns:
            None
        """
        deg = 0
        d_trtl.width(25)
        while deg < extent:
            deg += step
            if (deg % (step*2)) == 0:   # only true on every second iteration
                d_trtl.pencolor("red")
            else:
                d_trtl.pencolor("white")
            d_trtl.circle(rad,step)     # continue the circle
        d_trtl.pencolor("white")        # reset
        d_trtl.width(4)

    def _start_finish(self, sx: int = -450, gap: int = 4) -> None:
        """
        Draw the start/finish line.

        Parameters:
        - sx (int): starting x coordinate
        - gap (gap): gap between the lines, should be half of the width
        
        Returns:
        None
        """
        d_trtl.width(8)
        d_trtl.goto(sx, 204)
        d_trtl.pd()

                                                    # 192 is the width of the track
        for _ in range(int(196 / (gap * 2))):       # 1st line (up)
            d_trtl.pencolor("white")
            d_trtl.goto(sx, d_trtl.ycor() + gap)
            d_trtl.pencolor("black")
            d_trtl.goto(sx, d_trtl.ycor() + gap)

        d_trtl.goto(sx + d_trtl.width(), d_trtl.ycor() - (gap - gap / 2))

        for _ in range(int(192 / (gap * 2))):       # 2nd line (down)
            d_trtl.pencolor("white")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() - gap)
            d_trtl.pencolor("black")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() - gap)

        d_trtl.goto(sx + (d_trtl.width() * 2), d_trtl.ycor() + (gap - gap / 2))

        for _ in range(int(196 / (gap * 2))):       # 3rd line (up)
            d_trtl.pencolor("white")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() + gap)
            d_trtl.pencolor("black")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() + gap)

        d_trtl.goto(sx + (d_trtl.width() * 3), d_trtl.ycor() - (gap - gap / 2))

        for _ in range(int(192 / (gap * 2))):       # 4th line (down)
            d_trtl.pencolor("white")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() - gap)
            d_trtl.pencolor("black")
            d_trtl.goto(d_trtl.xcor(), d_trtl.ycor() - gap)

        d_trtl.pu()
        d_trtl.pencolor("white")                    # reset

    def _spedo_tick(self, sx: float = 0) -> None:
        """
        Draws a tick mark to represent a speedometer tick.

        Parameters:
        - sx (float): The x-coordinate of the tick mark's starting position. Default is 0.

        Returns:
        - None
        """
        t = d_trtl
                                        # create tick sprite
        tick = turtle.Shape("compound")
        tick.addcomponent(((0,0),(-40,0),(-40,5),(0,5),(0,-5),(-40,-5),(-40,0),(0,0)), "white", "white")
        turtle.register_shape("tick", tick)
        t.shape("tick")
        t.pd()                          # goto starting position
        t.goto(sx,-430)
        t.seth(90)
        t.shapesize(0.2)
        deg = 0
        step = 5
        while deg < 175:                # same algorithm as the red dash circle, but extent is hardcoded as 175, as is step as 5
            deg += step                 # (not 180 to account for the first tick being drawn at the start)
            if (deg % (step*2)) == 0:
                t.seth(deg+90)
                t.stamp()
            t.circle(110, step)
        t.shape("turtle")               # reset

    def _spedo(self, p1: Player) -> None:
        """
        Draws the speedometer for both players.

        Parameters:
        - p1: The player object. Used to determine the number of players.

        Returns:
        - None
        """
        d_trtl.pencolor("white")
        n1_trtl.pencolor("red")
        n1_trtl.width(4)
        n2_trtl.pencolor("red")
        n2_trtl.width(4)
        if p1.player_num == 2:
            # ---- Player 1 -----
            d_trtl.width(2)
            self._hgoto(-25,-430)
            d_trtl.setheading(90)
            d_trtl.fillcolor("#222222")
            d_trtl.begin_fill()
            self._spedo_tick(-25)
            d_trtl.goto(-245, -500)
            d_trtl.goto(-25, -500)
            d_trtl.goto(-25, -430)
            d_trtl.width(1)
            d_trtl.goto(-245, -430)
            d_trtl.end_fill()
            # ---- Player 2 -----
            d_trtl.width(2)
            self._hgoto(240,-430)
            d_trtl.setheading(90)
            d_trtl.fillcolor("#222222")
            d_trtl.begin_fill()
            self._spedo_tick(240)
            d_trtl.goto(20, -500)
            d_trtl.goto(240, -500)
            d_trtl.goto(240, -430)
            d_trtl.width(1)
            d_trtl.goto(20, -430)
            d_trtl.end_fill()
        else:
            # ---- Player 1 -----
            d_trtl.width(2)
            self._hgoto(100,-430)
            d_trtl.setheading(90)
            d_trtl.fillcolor("#222222")
            d_trtl.begin_fill()
            self._spedo_tick(100)
            d_trtl.goto(-120, -500)
            d_trtl.goto(100, -500)
            d_trtl.goto(100, -430)
            d_trtl.width(1)
            d_trtl.goto(-120, -430)
            d_trtl.end_fill()

    def _title(self) -> None:
        """
        Draws the title of the game.

        Args:
            None

        Returns:
            None
        """
        d_trtl.pu()
        d_trtl.goto(0, -25)
        d_trtl.write('"omega race"', False, "center", ("comic sans", 100, "bold"))

    def _track(self) -> None:
        """
        Draws the entire racetrack and colors it in.

        The track consists of three parts:
        - The concrete middle: A grey-colored filled shape in the middle of the track.
        - The outer edge: A black-colored filled shape that outlines the outer edge of the track.
        - The inner edge: A black-colored filled shape that outlines the inner edge of the track.
        
        Returns:
        None
        """
        d_trtl.pd()
        # concrete middle
        self._hgoto(-450,200)
        d_trtl.fillcolor("grey")
        d_trtl.begin_fill()
        d_trtl.goto(450,200)
        d_trtl.circle(-145,180)
        d_trtl.goto(-450,-90)
        d_trtl.circle(-145,180)
        d_trtl.end_fill()
        # outer edge
        self._hgoto(-450,400)
        d_trtl.fillcolor("#222222")
        d_trtl.begin_fill()
        d_trtl.goto(450,400)
        self._hgoto(450,410)
        self._red_dash_circle(-360,180,5)
        self._hgoto(450,-300)
        d_trtl.goto(-450,-300)
        self._hgoto(-450,-310)
        self._red_dash_circle(-360,180,5)
        # inner edge
        self._hgoto(-450,200)
        d_trtl.goto(450,200)
        self._hgoto(450,190)
        self._red_dash_circle(-135,180,10)
        self._hgoto(450,-90)
        d_trtl.goto(-450,-90)
        self._hgoto(-450,-80)
        self._red_dash_circle(-135,180,10)
        d_trtl.end_fill()
        d_trtl.pu()

    def rounded_rectangle(self, t: turtle.Turtle, short: int, long: int, radius: int, colour: str = "grey", outline: str = "grey") -> None:
        """
        Draws a rounded rectangle using the given turtle object.

        Parameters:
        - t (turtle.Turtle): The turtle object to draw with.
        - short (int): The length of the shorter side of the rectangle.
        - long (int): The length of the longer side of the rectangle.
        - radius (int): The radius of the rounded corners.
        - colour (str): The fill color of the rectangle. Defaults to "grey".
        - outline (str): The outline color of the rectangle. Defaults to "grey".

        Returns:
        None

        This function is a helper function for making the rounded rectangles used to show stats during the racing. (and now all buttons and elements in the menu and setup)
        """
        diameter = radius*2
        heading = t.heading()
        t.seth(270)
        # go to corner of rectangle
        self._hgoto(t.xcor()-(long/2),t.ycor()-(short/2)+radius)
        t.fillcolor(colour)
        t.pencolor(outline)
        t.begin_fill()
        # rounded rectangle
        for _ in range(2):
            t.circle(radius, 90)
            t.forward(long-diameter)
            t.circle(radius, 90)
            t.forward(short-diameter)
        t.end_fill()
        t.pencolor("white")
        # reset
        t.seth(heading)
        t.pu()

    def _score_area(self, p1: Player, p2: Player) -> None:
        """
        Draws the area where stats are located during the game.
        Including lap number, place, current lap time, and best lap time.
        
        Parameters:
        - p1: Player 1 object
        - p2: Player 2 object
        
        This method requires player1 and player2 to be passed in to use player colours as background.
        
        Returns:
        None
        """
        t = d_trtl
        t.pencolor("white")
        # ---- Player 1 side ----
        t.fillcolor(p1.attr.color)
        t.begin_fill()
        self._hgoto(-960, -300)
        t.goto(-460, -300)
        t.goto(-460, -540)
        t.goto(-960, -540)
        t.goto(-960, -300)
        t.end_fill()
        self._hgoto(-470,-345)
        t.goto(-940,-345)
        t.pu()
        t.goto(-825,-390)
        self.rounded_rectangle(t, 50, 200, 10)
        t.goto(-590,-390)
        self.rounded_rectangle(t, 50, 200, 10)
        t.goto(-590,-470)
        self.rounded_rectangle(t, 50, 200, 10)
        t.goto(-825,-470)
        self.rounded_rectangle(t, 50, 200, 10)
        t.goto(-935,-345)
        t.write(p1.name, True, "left", ("comic sans", 20, "bold"))
        t.goto(-910,-405)
        t.write("Lap", True, "left", ("comic sans", 20, "bold"))
        t.goto(-910,-485)
        t.write("Place", True, "left", ("comic sans", 20, "bold"))
        t.goto(-665,-390)
        t.write("Current Lap Time", True, "left", ("comic sans", 15, "normal"))
        t.goto(-650,-470)
        t.write("Best Lap Time", True, "left", ("comic sans", 15, "normal"))
        t.pd()
        # ---- Player 2 side ---------------------------------------------------
        if p1.player_num == 2:
            t.fillcolor(p2.attr.color)
            t.begin_fill()
            self._hgoto(960, -300)
            t.goto(460, -300)
            t.goto(460, -540)
            t.goto(960, -540)
            t.goto(960, -300)
            t.end_fill()
            self._hgoto(470,-345)
            t.goto(940,-345)
            t.pu()
            t.goto(825,-390)
            self.rounded_rectangle(t, 50, 200, 10)
            t.goto(590,-390)
            self.rounded_rectangle(t, 50, 200, 10)
            t.goto(590,-470)
            self.rounded_rectangle(t, 50, 200, 10)
            t.goto(825,-470)
            self.rounded_rectangle(t, 50, 200, 10)
            t.goto(750,-345)
            t.write(p2.name, True, "left", ("comic sans", 20, "bold"))
            t.goto(505,-405)
            t.write("Lap", True, "left", ("comic sans", 20, "bold"))
            t.goto(505,-485)
            t.write("Place", True, "left", ("comic sans", 20, "bold"))
            t.goto(750,-390)
            t.write("Current Lap Time", True, "left", ("comic sans", 15, "normal"))
            t.goto(765,-470)
            t.write("Best Lap Time", True, "left", ("comic sans", 15, "normal"))
            t.pd()

    def race_track(self, p1: Player, p2: Player) -> None:
        """
        Draws racetrack background for improved game.

        Parameters:
        - p1: Player 1 object
        - p2: Player 2 object

        Returns:
        None
        """
        # setup
        d_trtl.pencolor("white")
        d_trtl.width(5)
        d_trtl.seth(0)
        # draw elements
        self._score_area(p1, p2)
        self._track()
        self._start_finish(0,8)
        self._title()
        self._spedo(p1)

    def win_screen(self, wp: Player, nwp: Player, db: dict) -> None:
        """
        Display the win screen when a player wins.

        Args:
            wp (Player): The winning player.
            nwp (Player): The non-winning player.

        Returns:
            None
        """
        SCR.bgcolor("black")
        if wp.player_num == 1:
            if pd.to_timedelta(wp.best_lap()) <= pd.to_timedelta(db[wp.name]["best"]): # player has got a new best time
                self._hgoto(0,100)
                d_trtl.write("NEW BEST TIME!!!", False, "center", ("comic sans", 100, "bold"))
                self._hgoto(0,0)
                d_trtl.write(f"Congratulations {wp.name}!!", False, "center", ("comic sans", 50, "bold"))
                self._hgoto(0,-60)
                d_trtl.write(f"You achieved a new best time of {wp.best_lap()}!!", False, "center", ("comic sans", 50, "bold"))
            else:
                self._hgoto(0,100)
                d_trtl.write("Better luck next time", False, "center", ("comic sans", 100, "bold"))
                self._hgoto(0,0)
                d_trtl.write("Unfortunatly you did not achieve a new best time", False, "center", ("comic sans", 50, "bold"))
        else:
            self._hgoto(0,0)
            d_trtl.write(f"{wp.name.upper()} WON!!!!!!!!!!!!", False, "center", ("comic sans", 100, "bold"))
            self._hgoto(0,-50)
            d_trtl.write(f"Better luck next time {nwp.name}", False, "center", ("comic sans", 20, "bold"))

    def stats_screen(self, p1: Player, p2: Player, start_time: time) -> None:
        """
        Display the end statistics screen.

        Parameters:
        - p1 (Player): The first player object.
        - p2 (Player): The second player object.
        - start_time: The start time of the game.

        Returns:
        None
        """
        # get statistics
        # player 1
        total_time = str(time.now()-start_time)[:-3]
        p1laps = datetime.timedelta(seconds=0)
        p1avgtime: datetime.timedelta|str = "-"
        for lap in p1.timer.laps:
            p1laps += lap
        if len(p1.timer.laps) != 0:
            p1avgtime = p1laps/len(p1.timer.laps)
        # player 2
        p2laps = datetime.timedelta(seconds=0)
        p2avgtime: datetime.timedelta|str = "-"
        for lap in p2.timer.laps:
            p2laps += lap
        if len(p2.timer.laps) != 0:
            p2avgtime = p2laps/len(p2.timer.laps)
        # setup for drawing
        t = d_trtl
        t.clear()
        t.width(4)
        # draw the stats screen
        self._hgoto(0,400)
        t.goto(0,-500)
        self._hgoto(-900,400)
        t.goto(900,400)
        # ---- Player 1 ------
        self._hgoto(-900,410)
        t.write(f"{p1.name}'s Statistics", False, "left", ("comic sans", 50, "bold"))
        self._hgoto(-900,t.ycor()-60)
        t.write(f"Final Position: {p1.score.pos}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write(f"Number of Laps: {p1.score.laps}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write(f"Number of collisions with {p2.name}: {p1.score.collisions}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write(f"Fastest Lap: {p1.best_lap()}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write(f"Average Lap Time: {p1avgtime}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write(f"Total Time Taken: {total_time}", False, "left", ("comic sans", 30, "normal"))
        self._hgoto(-900,t.ycor()-50)
        t.write("Splits:", False, "left", ("comic sans", 30, "normal"))
        star = "*"
        n = ""
        for i, lap_time in enumerate(p1.timer.laps): # draw laps at bottom of stats screen
            if t.ycor() > -450:
                self._hgoto(-900, t.ycor()-50)
                t.write(f"Lap {i+1}: {str(lap_time)[:-3]}{star if str(lap_time) == p1.best_lap() else n}", False, "left", ("comic sans", 30, "normal"))
            else:
                self._hgoto(-900, t.ycor()-50)
                t.write("Too Many Laps to fit on screen", False, "left", ("comic sans", 30, "normal"))
                break

        # ---- Player 2 ------
        if p1.player_num == 2:
            self._hgoto(900,410)
            t.write(f"{p2.name}'s Statistics", False, "right", ("comic sans", 50, "bold"))
            self._hgoto(20,t.ycor()-60)
            t.write(f"Final Position: {p2.score.pos}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write(f"Number of Laps: {p2.score.laps}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write(f"Number of collisions with {p1.name}: {p2.score.collisions}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write(f"Fastest Lap: {p2.best_lap()}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write(f"Average Lap Time: {p2avgtime}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write(f"Total Time Taken: {total_time}", False, "left", ("comic sans", 30, "normal"))
            self._hgoto(20,t.ycor()-50)
            t.write("Splits:", False, "left", ("comic sans", 30, "normal"))
            x = "*"
            n = ""
            for i, lap_time in enumerate(p2.timer.laps): # draw laps at bottom of stats screen
                if t.ycor() > -450:
                    self._hgoto(20, t.ycor()-50)
                    t.write(f"Lap {i+1}: {str(lap_time)[:-3]}{x if str(lap_time) == p2.best_lap() else n}", False, "left", ("comic sans", 30, "normal"))
                else:
                    self._hgoto(20, t.ycor()-50)
                    t.write("Too Many Laps to fit on screen", False, "left", ("comic sans", 30, "normal"))
                    break

    def pause_screen(self) -> None:
        """
        Display the pause screen.

        This method draws a black bar across the screen and displays "PAUSED".
        Also includes options and a way to restart the game (maybe soon)

        Parameters:
        - None

        Returns:
        - None
        """
        p_trtl.fillcolor("black")
        p_trtl.pencolor("white")
        p_trtl.begin_fill()
        self._hgoto(960, 210, p_trtl)
        self._hgoto(960, -100, p_trtl)
        self._hgoto(-960, -100, p_trtl)
        self._hgoto(-960, 210, p_trtl)
        self._hgoto(960, 210, p_trtl)
        p_trtl.end_fill()
        self._hgoto(0, 0, p_trtl)
        p_trtl.write("PAUSED", False, "center", ("comic sans", 80, "bold"))

    def main_menu(self) -> None:
        """
        Draw the main menu.

        This method is responsible for drawing the main menu of the racing game.
        It displays the game title, options for playing the game, the leaderboard, and credits.

        Parameters:
        - None

        Returns:
        - None
        """
        t = d_trtl
        t.pencolor("white")
        self._hgoto(0,200)
        t.write('"omega race"'.upper(), False, "center", ("comic sans ms", 175, "bold"))
        self._hgoto(0,50)
        self.rounded_rectangle(t, 100, 500, 10)
        self._hgoto(5,10)
        t.write("PLAY GAME", False, "center", ("comic sans", 50, "normal"))
        self._hgoto(0,-100)
        self.rounded_rectangle(t, 100, 500, 10)
        self._hgoto(5,-140)
        t.write("OPTIONS", False, "center", ("comic sans", 50, "normal"))
        self._hgoto(0,-250)
        self.rounded_rectangle(t, 100, 500, 10)
        self._hgoto(5,-280)
        t.write("LEADERBOARD", False, "center", ("comic sans", 40, "normal"))
        self._hgoto(0,-400)
        self.rounded_rectangle(t, 100, 500, 10)
        self._hgoto(5,-440)
        t.write("QUIT", False, "center", ("comic sans", 50, "normal"))
        self._hgoto(-625,-475)
        t.fillcolor("#C0C0C0")
        t.begin_fill()
        t.pu()
        t.circle(300,360)
        t.end_fill()
        self._hgoto(625,-475)
        t.fillcolor("#C0C0C0")
        t.begin_fill()
        t.pu()
        t.circle(300,360)
        t.end_fill()
        self._hgoto(0,0)

class Updates:
    """
    Functions that update various parts of the game
    """
    def __init__(self, player1: Player, player2: Player, cars: dict) -> None:
        self.player1 = player1
        self.player2 = player2
        self.cars: dict = cars
        self.game_start_time = time.now()
        self.bg = Background()

    def spedo(self) -> None:
        """
        Updates the speed on the spedo.

        This method clears the spedo display and updates it with the current speed of the player(s).
        If there are two players, it displays the speeds of both players side by side.
        If there is only one player, it displays the speed of that player in the center.

        Parameters:
        None

        Returns:
        None
        """
        s_trtl.clear()
        if self.player1.player_num == 2:
            n1_trtl.clear()
            n2_trtl.clear()
            s_trtl.goto(-140,-505)
            s_trtl.write(self.player1.speed, True, "center", ("arial", 50, "normal"))
            s_trtl.goto(140,-505)
            s_trtl.write(self.player2.speed, True, "center", ("arial", 50, "normal"))
            speed1 = self.player1.speed*0.6
            speed2 = self.player2.speed*0.6
            n1_trtl.pu()
            n1_trtl.goto(-140,-430)
            n1_trtl.pd()
            n1_trtl.seth(180-speed1)
            n1_trtl.fd(80)
            n2_trtl.pu()
            n2_trtl.goto(140,-430)
            n2_trtl.pd()
            n2_trtl.seth(180-speed2)
            n2_trtl.fd(80)
        else:
            s_trtl.goto(0,-505)
            s_trtl.write(self.player1.speed, True, "center", ("arial", 50, "normal"))
            speed = self.player1.speed*0.6
            n1_trtl.clear()
            n1_trtl.pu()
            n1_trtl.goto(0,-430)
            n1_trtl.pd()
            n1_trtl.seth(180-speed)
            n1_trtl.fd(80)

    def timer(self) -> None:
        """
        Updates the main timer.
        It calculates the current time by subtracting the game start time from the current time,
        and it writes the current time on the screen.

        Parameters:
        None

        Returns:
        None
        """
        t_trtl.clear()
        t_trtl.goto(0,-75)
        current_time = time.now()-self.game_start_time
        t_trtl.write(str(current_time)[:-3], False, "center", ("comic sans", 20, "bold"))

    def score_area(self) -> None:
        """
        Updates the score area with the latest statistics.

        This method clears the score area and updates it with the current scores, positions, lap times, and best lap times
        for both players. It also determines the positions of the players based on the number of laps completed.

        Parameters:
        None

        Returns:
        None
        """
        ll = ll_trtl
        lr = lr_trtl
        ll.clear()
        lr.clear()
        self.player1.score.pos = "Draw"
        self.player2.score.pos = "Draw"
        if self.player1.score.laps > self.player2.score.laps:
            self.player1.score.pos = "1st"
            self.player2.score.pos = "2nd"
        elif self.player2.score.laps > self.player1.score.laps:
            self.player1.score.pos = "2nd"
            self.player2.score.pos = "1st"
        # ---Player 1----
        ll.goto(-740,-405)
        ll.write(f"{int(self.player1.score.laps)}/{int(self.player1.score.total_laps)}", False, "right", ("comic sans", 20, "normal"))
        ll.goto(-740,-485)
        ll.write(self.player1.score.pos, False, "right", ("comic sans", 20, "normal"))
        ll.goto(-535,-415)
        ll.write(str(self.player1.timer.lap_time)[:-3], False, "right", ("comic sans", 15, "normal"))
        ll.goto(-535,-495)
        ll.write(self.player1.best_lap(), False, "right", ("comic sans", 15, "normal"))
        # ----Player 2--------------------------------------------------------------------------
        if self.player1.player_num == 2:
            lr.goto(680,-405)
            lr.write(f"{int(self.player2.score.laps)}/{int(self.player2.score.total_laps)}", False, "right", ("comic sans", 20, "normal"))
            lr.goto(680,-485)
            lr.write(self.player2.score.pos, False, "right", ("comic sans", 20, "normal"))
            lr.goto(880,-415)
            lr.write(str(self.player2.timer.lap_time)[:-3], False, "right", ("comic sans", 15, "normal"))
            lr.goto(880,-495)
            lr.write(self.player2.best_lap(), False, "right", ("comic sans", 15, "normal"))

    def player_collision(self) -> None:
        """
        Check collision between the players.

        This method checks for collision between the players.
        It calls the `player_collision` method of both players to handle the collision.

        Parameters:
        None

        Returns:
        None
        """
        self.player1.player_collision(self.player2)
        self.player2.player_collision(self.player1)

    def update(self) -> None:
        """
        Perform miscellaneous updates for the game.

        Including:
        - Checking for player collisions
        - Updating the score area
        - Handling the speedometer
        - Updating the timer

        This method does not return any value.
        """
        self.player_collision()
        self.score_area()
        self.spedo()
        self.timer()

    def menu(self) -> None:
        """
        Updates the main menu.

        This method updates the main menu cars with their new colour, and the player name

        Parameters:
        None

        Returns:
        None
        """
        # cars
        p1 = self.player1
        p2 = self.player2
        p1.turtle.clear()
        p1.turtle.penup()
        p1.turtle.goto(-650,-150)
        p1.turtle.seth(50)
        p1.turtle.shapesize(10)
        p1.turtle.shape(p1.attr.shape)
        p1.turtle.color(p1.attr.color)
        p1.turtle.stamp()
        p2.turtle.clear()
        p2.turtle.penup()
        p2.turtle.goto(650,-150)
        p2.turtle.seth(-50)
        p2.turtle.shapesize(10)
        p2.turtle.shape(p2.attr.shape)
        p2.turtle.color(p2.attr.color)
        p2.turtle.stamp()

    def name(self) -> None:
        """
        Updates the player name in the selection screen.

        Parameters:
        None

        Returns:
        None
        """
        m_trtl.clear()
        # m_trtl.pu()
        d_trtl.pu()
        m_trtl.pencolor("white")
        if self.player1.player_num == 1:
            m_trtl.goto(0-len(self.player1.name*50)/2,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name)*50, 10, "dark grey")
            m_trtl.goto(0,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))
        else:
            # player 1
            m_trtl.goto(-300-len(self.player1.name*50)/2,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name)*50, 10, "dark grey")
            m_trtl.goto(-300,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))
            # player 2
            m_trtl.goto(300-len(self.player2.name*50)/2,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player2.name)*50, 10, "dark grey")
            m_trtl.goto(300,-50)
            m_trtl.write(self.player2.name, False, "center", ("comic sans", 50, "normal"))

    def sprite_menu(self) -> None:
        """
        Update the cars and colours on the sprite selection screen.

        Parameters:
        None
        
        Returns:
        None
        """
        p1 = self.player1
        p2 = self.player2
        c_trtl.clear()
        if p1.player_num == 1:
            # car
            p1.turtle.clear()
            p1.turtle.penup()
            p1.turtle.goto(-500,100)
            p1.turtle.seth(50)
            p1.turtle.shapesize(15)
            p1.turtle.shape(p1.attr.shape)
            p1.turtle.color(p1.attr.color)
            p1.turtle.stamp()
            # colour box
            d_trtl.width(25)
            d_trtl.goto(200,40)
            self.bg.rounded_rectangle(d_trtl, 100, 500, 10, p1.attr.color, "white")
            d_trtl.pd()
            # coins
            c_trtl.goto(800,-492.5)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
        else:
            # cars
            p1.turtle.clear()
            p1.turtle.penup()
            p1.turtle.goto(-650,-150)
            p1.turtle.seth(50)
            p1.turtle.shapesize(10)
            p1.turtle.shape(p1.attr.shape)
            p1.turtle.color(p1.attr.color)
            p1.turtle.stamp()
            p2.turtle.clear()
            p2.turtle.penup()
            p2.turtle.goto(650,-150)
            p2.turtle.seth(-50)
            p2.turtle.shapesize(10)
            p2.turtle.shape(p2.attr.shape)
            p2.turtle.color(p2.attr.color)
            p2.turtle.stamp()
            # colour box
            d_trtl.width(15)
            d_trtl.goto(-200,0)
            self.bg.rounded_rectangle(d_trtl, 50, 200, 10, p1.attr.color, "white")
            d_trtl.goto(200,0)
            self.bg.rounded_rectangle(d_trtl, 50, 200, 10, p2.attr.color, "white")
            # coins
            c_trtl.goto(-800,135)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
            c_trtl.goto(800,135)
            c_trtl.write(self.player2.score.coins, False, "center", ("comic sans", 20, "normal"))

    def purchase_button(self, state: str, player: Player, car: str = "") -> None:
        """
        updates the purchase button on the sprite select screen
        """
        match state:
            case "purchased":
                if player.player_num == 1:
                    m_trtl.clear()
                    m_trtl.pencolor("#212121")
                    m_trtl.goto(110,-130)
                    m_trtl.write("Purchased".upper(), False, "center", ("comic sans", 35, "bold"))
                    m_trtl.pencolor("white")
                else:
                    if player.num == 1:
                        m_trtl.pencolor("#212121")
                        m_trtl.clear()
                        m_trtl.goto(-155,-125)
                        m_trtl.write("Purchased".upper(), False, "center", ("comic sans", 30, "bold"))
                        m_trtl.pencolor("white")
                    else:
                        p_trtl.pencolor("#212121")
                        p_trtl.clear()
                        p_trtl.goto(155,-125)
                        p_trtl.write("Purchased".upper(), False, "center", ("comic sans", 30, "bold"))
                        p_trtl.pencolor("white")
            case "buy":
                if player.player_num == 1:
                    m_trtl.clear()
                    m_trtl.goto(110,-110)
                    m_trtl.write(self.cars[car], False, "center", ("comic sans", 35, "bold"))
                    m_trtl.goto(115,-150)
                    m_trtl.write("Buy Vehicle".upper(), False, "center", ("comic sans", 30, "normal"))
                    # coin icon
                    m_trtl.goto(50,-90)
                    m_trtl.fillcolor("gold")
                    m_trtl.begin_fill()
                    m_trtl.circle(10, 360)
                    m_trtl.end_fill()
                else:
                    if player.num == 1:
                        m_trtl.clear()
                        m_trtl.goto(-205,-100)
                        m_trtl.write(self.cars[car], False, "center", ("comic sans", 30, "bold"))
                        m_trtl.goto(-155,-150)
                        m_trtl.write("Buy Vehicle".upper(), False, "center", ("comic sans", 30, "normal"))
                        # coin icon
                        m_trtl.goto(-100,-90)
                        m_trtl.fillcolor("gold")
                        m_trtl.begin_fill()
                        m_trtl.circle(10, 360)
                        m_trtl.end_fill()
                    else:
                        p_trtl.clear()
                        p_trtl.goto(205,-100)
                        p_trtl.write(self.cars[car], False, "center", ("comic sans", 30, "bold"))
                        p_trtl.goto(155,-150)
                        p_trtl.write("Buy Vehicle".upper(), False, "center", ("comic sans", 30,"normal"))
                        # coin icon
                        p_trtl.goto(100,-90)
                        p_trtl.fillcolor("gold")
                        p_trtl.begin_fill()
                        p_trtl.circle(10, 360)
                        p_trtl.end_fill()

    def coins(self) -> None:
        """
        update the coin count display
        """
        c_trtl.clear()
        if self.player1.player_num == 1:
            c_trtl.goto(-800,482.5)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
        else:
            c_trtl.goto(-800,482.5)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
            c_trtl.goto(800,482.5)
            c_trtl.write(self.player2.score.coins, False, "center", ("comic sans", 20, "normal"))

class Drawing:
    """
    Functions that initiate the drawing of various screens of the game
    """
    def __init__(self, player1: Player, player2: Player, scr: turtle._Screen) -> None:
        self.player1 = player1
        self.player2 = player2
        self.scr = scr
        self.bg = Background()
        self.game_start_time = time.now()

    def reset(self) -> None:
        """
        reset the screen
        """
        self.scr.bgcolor("black")
        for turtl in TURTLES:
            turtl.clear()
        self.player1.turtle.clear()
        self.player2.turtle.clear()
        self.player1.turtle.hideturtle()
        self.player2.turtle.hideturtle()

    def menu(self) -> None:
        """
        draws the title screen and main menu
        """
        self.scr.bgcolor("black")
        self.bg.main_menu()

    def options(self) -> None:
        """
        draws the settings screen
        includes options like name and colour
        #! unused
        """

    def og(self) -> None:
        """og omega race track"""
        self.bg.ui_omega_race()

    def track(self) -> None:
        """
        draws the race track, including stats menu and speedometers,
        and places the players at the start line
        """
        d_trtl.clear()
        m_trtl.clear()
        self.scr.bgcolor("#117c13")
        self.bg.race_track(self.player1, self.player2)

    def stats(self) -> None:
        """
        draws the stats screen at the end of the game
        """
        self.bg.stats_screen(self.player1, self.player2, self.game_start_time)

    def game_mode(self) -> None:
        """
        screen for number of players
        """
        t = d_trtl
        self.reset()
        t.pencolor("white")
        t.pu()
        t.fillcolor("grey")
        t.goto(0,-400)
        self.bg.rounded_rectangle(t, 100, 500, 10)
        t.goto(0,-440)
        t.write("Next", False, "center", ("comic sans", 50, "normal"))
        t.goto(0,-500)
        t.write("Press 'b' to go back", False, "center", ("comic sans", 20, "normal"))
        t.goto(0,250)
        t.write("Number of Players", False, "center", ("comic sans", 100, "normal"))
        t.goto(-200,-150)
        t.begin_fill()
        t.circle(150,360)
        t.end_fill()
        t.goto(-200,0)
        t.write("1", False, "center", ("comic sans", 50, "normal"))
        t.goto(-200,-50)
        t.write("Player", False, "center", ("comic sans", 50, "normal"))
        t.goto(200,-150)
        t.begin_fill()
        t.circle(150,360)
        t.end_fill()
        t.goto(200,0)
        t.write("2", False, "center", ("comic sans", 50, "normal"))
        t.goto(200,-50)
        t.write("Players", False, "center", ("comic sans", 50, "normal"))

    def player_names(self) -> None:
        """
        allows the player to select their name
        """
        t = d_trtl
        self.reset()
        t.pencolor("white")
        t.pu()
        m_trtl.pu()
        t.goto(0,-400)
        self.bg.rounded_rectangle(t, 100, 500, 10)
        t.goto(0,-440)
        t.write("Next", False, "center", ("comic sans", 50, "normal"))
        t.goto(0,-500)
        t.write("Press 'b' to go back", False, "center", ("comic sans", 20, "normal"))
        if self.player1.player_num == 1:
            t.goto(0,250)
            t.write("Name of Player", False, "center", ("comic sans", 100, "normal"))
            t.goto(0,225)
            t.write("Click on the name to change it", False, "center", ("comic sans", 20, "normal"))
            t.goto(0,200)
            t.write("Name must be less that 10 characters", False, "center", ("comic sans", 20, "normal"))
            t.goto(0,50)
            t.write("Player 1:", False, "center", ("comic sans", 50, "normal"))
            m_trtl.goto(-250,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name)*50, 10, "dark grey")
            m_trtl.goto(0,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))
        else:
            t.goto(0,250)
            t.write("Name of Players", False, "center", ("comic sans", 100, "normal"))
            t.goto(0,225)
            t.write("Click on the name to change it", False, "center", ("comic sans", 20, "normal"))
            t.goto(0,200)
            t.write("Names must be less that 10 characters and cannot be the same", False, "center", ("comic sans", 20, "normal"))
            # player 1
            t.goto(-300,50)
            t.write("Player 1:", False, "center", ("comic sans", 50, "normal"))
            m_trtl.goto(-300,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name)*50, 10, "dark grey")
            m_trtl.goto(-300,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))
            # player 2
            t.pu()
            t.goto(300,50)
            t.write("Player 2:", False, "center", ("comic sans", 50, "normal"))
            m_trtl.goto(300,-50)
            self.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name)*50, 10, "dark grey")
            m_trtl.goto(300,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))

    def sprite_select(self) -> None:
        """
        select the sprite and colour for each player
        """
        t = d_trtl
        self.reset()
        t.pencolor("white")
        t.pu()
        # next button
        t.goto(0,-400)
        self.bg.rounded_rectangle(t, 100, 500, 10)
        t.goto(0,-440)
        t.write("Next", False, "center", ("comic sans", 50, "normal"))
        t.goto(0,-500)
        t.write("Press 'b' to go back", False, "center", ("comic sans", 20, "normal"))
        # sprite selection
        if self.player1.player_num == 1:
            t.goto(900,400)
            t.write("Select Vehicle and Colour", False, "right", ("comic sans", 70, "normal"))
            t.goto(900,360)
            t.write("Click on the car to switch between them", False, "right", ("comic sans", 30, "normal"))
            t.goto(900,325)
            t.write("Click on the colour box to change the accent colour", False, "right", ("comic sans", 30, "normal"))
            # Car
            t.goto(-500,-300)
            t.fillcolor("#C0C0C0")
            t.begin_fill()
            t.pu()
            t.circle(400,360)
            t.end_fill()
            t.goto(625,-475)
            # name
            t.goto(-50,100)
            t.write(f"{self.player1.name}", False, "left", ("comic sans", 50, "normal"))
            # purchase button
            t.goto(110,-100)
            self.bg.rounded_rectangle(t, 100, 350, 10)
            m_trtl.pencolor("#212121")
            m_trtl.goto(110,-130)
            m_trtl.write("Purchased".upper(), False, "center", ("comic sans", 35, "bold"))
            m_trtl.pencolor("white")
            # coins
            t.width(2)
            t.goto(825,-475)
            self.bg.rounded_rectangle(t, 50, 200, 10, "black", "white")
            t.width(1)
            t.goto(875,-485)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
            c_trtl.goto(800,-492.5)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
        else:
            t.goto(0,300)
            t.write("Select Vehicles and Colours", False, "center", ("comic sans", 70, "normal"))
            t.goto(0,270)
            t.write("Click on the car to switch between them", False, "center", ("comic sans", 20, "normal"))
            t.goto(0,240)
            t.write("Click on the colour box to change the accent colour", False, "center", ("comic sans", 20, "normal"))
            # Cars
            t.goto(-625,-475)
            t.fillcolor("#C0C0C0")
            t.begin_fill()
            t.pu()
            t.circle(300,360)
            t.end_fill()
            t.goto(625,-475)
            t.fillcolor("#C0C0C0")
            t.begin_fill()
            t.pu()
            t.circle(300,360)
            t.end_fill()
            t.goto(0,0)
            # Player name
            t.goto(-350,50)
            t.write(f"{self.player1.name}", False, "left", ("comic sans", 30, "normal"))
            t.goto(350,50)
            t.write(f"{self.player2.name}", False, "right", ("comic sans", 30, "normal"))
            # purchase button
            t.goto(160,-100)
            self.bg.rounded_rectangle(t, 100, 300, 10)
            t.goto(-160,-100)
            self.bg.rounded_rectangle(t, 100, 300, 10)
            m_trtl.pencolor("#212121")
            m_trtl.goto(-155,-125)
            m_trtl.write("Purchased".upper(), False, "center", ("comic sans", 30, "bold"))
            m_trtl.pencolor("white")
            p_trtl.pencolor("#212121")
            p_trtl.goto(155,-125)
            p_trtl.write("Purchased".upper(), False, "center", ("comic sans", 30, "bold"))
            p_trtl.pencolor("white")
            # coins
            # p1
            t.width(2)
            t.goto(-825,150)
            self.bg.rounded_rectangle(t, 50, 200, 10, "black", "white")
            t.width(1)
            t.goto(-875,140)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
            c_trtl.goto(-800,135)
            c_trtl.write(self.player1.score.coins, False, "center", ("comic sans", 20, "normal"))
            # p2
            t.width(2)
            t.goto(825,150)
            self.bg.rounded_rectangle(t, 50, 200, 10, "black", "white")
            t.width(1)
            t.goto(875,140)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
            c_trtl.goto(800,135)
            c_trtl.write(self.player2.score.coins, False, "center", ("comic sans", 20, "normal"))

    def coins(self) -> None:
        """
        draw the coin count display
        """
        t = d_trtl
        t.width(5)
        if self.player1.player_num == 1:
            t.pu()
            t.goto(-825,500)
            self.bg.rounded_rectangle(t, 50, 200, 10, "green", "white")
            t.goto(-875,500)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
        else:
            t.pu()
            t.goto(-825,500)
            self.bg.rounded_rectangle(t, 50, 200, 10, "green", "white")
            t.goto(825,500)
            self.bg.rounded_rectangle(t, 50, 200, 10, "green", "white")
            t.goto(-875,500)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
            t.goto(875,500)
            t.fillcolor("gold")
            t.begin_fill()
            t.circle(10, 360)
            t.end_fill()
        t.width(2)

    def countdown(self, num: str) -> None:
        """
        draw the countdown before game starts
        """
        t = m_trtl
        t.clear()
        t.pu()
        t.goto(215,180)
        t.pencolor("white")
        if num == "0":
            t.write("GO!", False, "center", ("comic sans", 150, "bold"))
        elif num == "clear":
            t.clear()
        else:
            t.write(num, False, "center", ("comic sans", 150, "bold"))
        self.scr.update()

class Database:
    """
    Database class
    """
    def __init__(self) -> None:
        self.db: dict = {}

    def load(self) -> dict:
        """
        loads the Database from a file to be displayed
        
        Returns:
        dict: the Database
        """
        try:
            with open("database.json", "r", encoding="utf-8") as dbfile:
                self.db = json.load(dbfile)
                return self.db
        except FileNotFoundError:
            with open("database.json", "w", encoding="utf-8") as dbfile:
                json.dump({}, dbfile)
            return {}

    def save(self) -> None:
        """
        saves the Database
        """
        with open("database.json", "w", encoding="utf-8") as dbfile:
            json.dump(self.db, dbfile)

    def create_player(self, player: Player, best: datetime.timedelta|None = None) -> None:
        """
        adds a player to the database if it is their first time playing
        """
        self.db[str(player.name)] = {"best": str(best), "coins": 0, "cars": ["f1car"]}

    def check_exist(self, player: Player) -> bool:
        """
        check if a player exists in the db with a time
        """
        if str(player.name) in self.db:
            return True
        self.create_player(player)
        return False

    def new_best(self, player: Player, best_time: datetime.timedelta) -> None:
        """
        adds a new best time for a player into the Database
        """
        if self.check_exist(player):
            prev_time = pd.to_timedelta(self.db[str(player.name)]["best"] if self.db[str(player.name)]["best"] != "None" else "9:99:99")
            best_time = best_time if best_time < pd.to_timedelta(prev_time) else prev_time  # check if the new time is a new best
            self.db[str(player.name)]["best"] = str(best_time)                              # update the db with a new best time
            self.db[str(player.name)]["coins"] = player.score.coins                         # update the amount of coins
        else:
            self.create_player(player, best_time)

    def get_sorted(self) -> dict:
        """
        returns a sorted decending version of the Database
        """
        time_db = {}
        for player, value in self.db.items():                                           # get just the times, not the coins or cars
            time_db[player] = value["best"]
        sorted_db = dict(sorted(time_db.items(), key=lambda a: a[1], reverse=False))    # sort the times in descending order
        return sorted_db

    def draw(self) -> None:
        """
        draws the leaderboard in the leaderboard menu option
        """
        t = d_trtl
        t.pu()
        t.goto(0,350)
        t.write("Leaderboard".upper(), False, "center", ("comic sans", 100, "bold"))
        pos = 0
        for player, best in self.get_sorted().items():
            if best != "None":
                pos += 1
                best = best[7:-3] # cut off the days (first 7 chars) and microseconds (last 3 chars)
                t.goto(0, t.ycor()-100)
                y = t.ycor()
                match pos:
                    case 1:             # first
                        t.goto(0,y+40)
                        Background().rounded_rectangle(t, 100, 1200, 10, "gold", "gold")
                        t.goto(-575, y)
                        t.write("🥇", False, "left", ("comic sans", 50, "normal"))
                        t.goto(-450, y)
                        t.write(f"{pos}:", False, "left", ("comic sans", 50, "bold"))
                        t.goto(-375, y)
                        t.write(f"{player}", False, "left", ("comic sans", 50, "bold"))
                        t.goto(550, y)
                        t.write(f"{best}", False, "right", ("comic sans", 50, "normal"))
                        t.goto(0, y-10)
                    case 2:             # second
                        t.goto(0,y+40)
                        Background().rounded_rectangle(t, 100, 1200, 10, "silver", "silver")
                        t.goto(-575, y)
                        t.write("", False, "left", ("comic sans", 50, "normal"))
                        t.goto(-450, y)
                        t.write(f"{pos}:", False, "left", ("comic sans", 50, "normal"))
                        t.goto(-375, y)
                        t.write(f"{player}", False, "left", ("comic sans", 50, "normal"))
                        t.goto(550, y)
                        t.write(f"{best}", False, "right", ("comic sans", 50, "normal"))
                        t.goto(0, y-10)
                    case 3:             # third
                        t.goto(0,y+40)
                        Background().rounded_rectangle(t, 100, 1200, 10, "#6E4D25", "#6E4D25")
                        t.goto(-450, y)
                        t.write(f"{pos}:", False, "left", ("comic sans", 50, "normal"))
                        t.goto(-375, y)
                        t.write(f"{player}", False, "left", ("comic sans", 50, "normal"))
                        t.goto(550, y)
                        t.write(f"{best}", False, "right", ("comic sans", 50, "normal"))
                        t.goto(0, y+15)
                    case _:             # rest
                        if t.ycor() > -500:
                            t.goto(-450, y-10)
                            t.write(f"{pos}:", False, "left", ("comic sans", 50, "normal"))
                            t.goto(-375, y)
                            t.write(f"{player}", False, "left", ("comic sans", 30, "normal"))
                            t.goto(550, y-10)
                            t.write(f"{best}", False, "right", ("comic sans", 50, "normal"))
                            t.goto(0, y+25)

    def purchase_car(self, player: Player, car: str) -> None:
        """
        reflects the purchase of a car in the database
        
        assume car is a valid car
        """
        self.db[player.name]["cars"].append(car)

@dataclasses.dataclass
class _Sub:
    """
    all the util subclasses (background, database, drawing, updates)
    """
    bg: Background
    data: Database
    draw: Drawing
    update: Updates

class Util:
    """
    Utility functions
    """
    def __init__(self, player1, player2, scr) -> None:
        # constants
        self.player1: Player = player1
        self.player2: Player = player2
        self.scr: turtle._Screen = scr
        # variables
        self.game_start_time: time = time.now()                                     # time the game started
        self.game_state: str = "not started"                                        # current "state" or "screen" of the game
        self.num_of_players: int = 2                                                # number of players in the game (either 1 or 2)
        self.coin_frames: int = 0                                                   # amount of frames since the coins were spawned
        self.coin_list: list[Coin] = [Coin((100*i)-400,-200) for i in range(9)]     # list of coin objects to draw on screen
        self.cars: dict[str, int] = {"f1car": 0, "ute": 500}#, "": 1000}            # list of vehicle options and their cost
        # index 0 is for player 1, index 1 is for player 2
        self.can_move_next: list[bool] = [True, True]                               # whether the player can move to the next setup screen
        self.car_select_index: list[int] = [0, 0]                                   # index of the currently selected vehicle in the list of vehicles
        self.colour_select_index: list[int] = [0, 0]                                # index of the currently selected colour in the list of colours
        # subclasses of util
        self.sub: _Sub = _Sub(
                            bg=Background(),
                            data=Database(),
                            draw=Drawing(player1, player2, scr),
                            update=Updates(player1, player2, self.cars)
                            )
        # self.bg: Background = Background()
        # self.db: Database = Database()
        # self.draw: Drawing = Drawing(player1, player2, scr)
        # self.update: Updates = Updates(player1, player2)

    def _check_win(self) -> tuple[bool, Player, Player]:
        """
        Check if a player has won

        Parameters:
            None
        
        Returns:
            tuple[bool, Player, Player]: (won, winning player, non winning player)
        """
        if self.player1.score.won:
            return (True, self.player1, self.player2)
        if self.player2.score.won:
            return (True, self.player2, self.player1)
        return False, self.player1, self.player2

    def _check_quit(self) -> bool:
        """
        Check if the game should quit without being finished
        #! unused so just return no
        """
        return False

    def _end_game_win(self, wp: Player, nwp: Player) -> None:
        """
        Ends the game with a winner
        
        Parameters:
            wp: winning player
            nwp: non winning player
        
        Return:
            None
        """
        self.sub.draw.reset()           # black screen with no visible turtles
        for coin in self.coin_list:     # clear the coins
            coin.turtle.clear()
        for player in [wp, nwp]:        # check if the player has a new best lap time
            if player.timer.laps:
                best = pd.to_timedelta(player.best_lap())
                self.sub.data.new_best(player, best)
        self.sub.bg.win_screen(wp, nwp, self.sub.data.db) # draw the win screen

    def _end_game(self) -> None:
        self.game_state = "quit"

    def check_end(self) -> bool:
        """
        Check if the game should be finished

        Parameters:
            None

        Returns:
            True if the game has ended, False otherwise
        """
        won, wp, nwp = self._check_win()
        quit_game = self._check_quit()
        if won:
            self.game_state = "end win"
            self._end_game_win(wp, nwp)
            return True
        if quit_game:
            self.game_state = "end"
            self._end_game()
            return True
        return False

    def handle_keybinds(self) -> None:
        """
        Registers the keybinds required for player movement.

        This method sets up the keybinds for player movement and other actions.
        It associates specific keys with corresponding player methods to handle
        keypress and keyrelease events.

        Keybinds for Player 1:
        - "w" and "W" keys for acceleration
        - "a" and "A" keys for rotating left
        - "s" and "S" keys for deceleration
        - "d" and "D" keys for rotating right

        Keybinds for Player 2:
        - "Up" key for acceleration
        - "Left" key for rotating left
        - "Down" key for deceleration
        - "Right" key for rotating right

        Additional keybinds:
        - "Return" key for skipping to the next screen
        - "Escape" key for pausing
        - "Shift + q" and "Delete" key for quitting the game
        - "r" key for restarting the game
        - Left mouse button click for button functionality

        Shhhhhhhhhhh:
        - "Shift + c" to cheat in money
        
        Parameters:
            None
        
        Returns:
            None
        """
        self.scr.listen()
        self.scr.onkeypress(self.player1.accelerate_start, "w")
        self.scr.onkeyrelease(self.player1.accelerate_stop, "w")
        self.scr.onkeypress(self.player1.rotate_left_start, "a")
        self.scr.onkeyrelease(self.player1.rotate_left_stop, "a")
        self.scr.onkeypress(self.player1.decel_start, "s")
        self.scr.onkeyrelease(self.player1.decel_stop, "s")
        self.scr.onkeypress(self.player1.rotate_right_start, "d")
        self.scr.onkeyrelease(self.player1.rotate_right_stop, "d")

        self.scr.onkeypress(self.player1.accelerate_start, "W")
        self.scr.onkeyrelease(self.player1.accelerate_stop, "W")
        self.scr.onkeypress(self.player1.rotate_left_start, "A")
        self.scr.onkeyrelease(self.player1.rotate_left_stop, "A")
        self.scr.onkeypress(self.player1.decel_start, "S")
        self.scr.onkeyrelease(self.player1.decel_stop, "S")
        self.scr.onkeypress(self.player1.rotate_right_start, "D")
        self.scr.onkeyrelease(self.player1.rotate_right_stop, "D")

        self.scr.onkeypress(self.player2.accelerate_start, "Up")
        self.scr.onkeyrelease(self.player2.accelerate_stop, "Up")
        self.scr.onkeypress(self.player2.rotate_left_start, "Left")
        self.scr.onkeyrelease(self.player2.rotate_left_stop, "Left")
        self.scr.onkeypress(self.player2.decel_start, "Down")
        self.scr.onkeyrelease(self.player2.decel_stop, "Down")
        self.scr.onkeypress(self.player2.rotate_right_start, "Right")
        self.scr.onkeyrelease(self.player2.rotate_right_stop, "Right")

        self.scr.onkey(self.enter, "Return")
        self.scr.onkey(self.esc, "Escape")
        self.scr.onclick(self.click, 1)

        self.scr.onkey(self.exit, "Q")
        self.scr.onkey(self.exit, "Delete")

        self.scr.onkey(self.restart, "r")
        self.scr.onkey(self.back_menu, "b")

        self.scr.onkey(self.cheat, "C")

    def enter(self) -> None:
        """
        Process the enter key press and perform the corresponding action based on the current game state.

        The enter key press can trigger different actions depending on the current game state:
        - If the game state is "game", enter does nothing.
        - If the game state is "stats", enter sets the game state to "quit".
        - If the game state is "menu", enter sets the game state to "menu game mode load".
        - If the game state starts with "menu ", the method calls the `next_menu` method.

        Returns:
            None
        """
        if self.game_state == "game":
            return
        if self.game_state == "stats":
            self.game_state = "quit"
            return
        if self.game_state == "menu":
            self.game_state = "menu game mode load"
            return
        if self.game_state.startswith("menu "):
            self.next_menu()
            return

    def esc(self) -> None:
        """
        Handle escape key press - either pause or unpause the game.

        If the game is currently in the "game" state, escape pauses the game by displaying a pause screen and changing the game state to "paused".
        If the game is currently in the "paused" state, escape clears the pause screen and changes the game state back to "game".
        If the game is currently in the "leaderboard" state, go back to the main menu
        If the game is in any other state, escape does nothing.

        Returns:
            None
        """
        if self.game_state == "game":
            self.sub.bg.pause_screen()
            self.game_state = "paused"
        elif self.game_state == "paused":
            p_trtl.clear()
            self.game_state = "game"
        elif self.game_state == "leaderboard":
            self.sub.draw.reset()
            self.game_state = "init"
        elif self.game_state.startswith("menu "):
            self.sub.draw.reset()
            self.game_state = "init"
        else:
            return

    def _click_menu(self, x: float, y: float) -> None:
        """
        Handles a click when the game is in the main menu

        Arguments:
            x (float): x coordinate of the click
            y (float): y coordinate of the click
        """
        if -250 <= x <= 250:                    # click a button
            if 0 <= y <= 100:                   # click play game
                self.game_state = "menu game mode load"
            elif -50 >= y >= -150:              # click options
                self.game_state = "options menu"
            elif -200 >= y >= -300:             # click leaderboard
                self.game_state = "leaderboard load"
            elif -350 >= y >= -450:             # click quit
                self.game_state = "quit"
        elif -375 <= y <= 100:                  # click a car
            if -900 <= x <= -350:
                self.change_car_colour(self.player1)
            elif 350 <= x <= 900:
                self.change_car_colour(self.player2)
        #! unused
        # elif (-300 >= x >= -425) and (150 <= y <= 175):
        #     self.change_name(self.player1)

    def _click_pause(self, x: float, y: float) -> None:
        """
        handles a click in the pause menu

        Arguments:
            x (float): the x coordinate of the click
            y (float): the y coordinate of the click
        """
        #! unused - no things to click on currently

    def _click_setup_game_mode(self, x: float, y: float) -> None:
        """
        handles a click in the game mode selection menu

        Arguments:
            x (float): the x coordinate of the click
            y (float): the y coordinate of the click
        """
        m_trtl.pencolor("white")
        m_trtl.pu()
        if -150 <= y <= 150:
            if -350 <= x <= -50:                # 1 player button
                self.num_of_players = 1
                self.player1.player_num = 1
                self.player2.player_num = 1
                self.player2.active = False
                m_trtl.clear()
                m_trtl.width(4)
                m_trtl.goto(-200,-150)
                m_trtl.pd()
                m_trtl.circle(150,360)
                m_trtl.pu()
            elif 50 <= x <= 350:                # 2 player button
                self.num_of_players = 2
                self.player1.player_num = 2
                self.player2.player_num = 2
                self.player2.active = True
                m_trtl.clear()
                m_trtl.width(4)
                m_trtl.goto(200,-150)
                m_trtl.pd()
                m_trtl.circle(150,360)
                m_trtl.pu()

    def _click_setup_player_name(self, x: float, y: float) -> None:
        """
        handles a click in the player name selection menu
        the player's name must be at least 1 character and less than 10 characters, and cannot be the same as the other player's name

        Arguments:
            x (float): the x coordinate of the click
            y (float): the y coordinate of the click
        """
        if self.num_of_players == 1:
            if -50 <= y <= 50:
                if -250 <= x <= 250:
                    # choose player 1 name
                    name = turtle.textinput("Player ONE", "Enter your player name")
                    self.player1.name = name if ((name is not None) and (0 < len(name) <= 10)) else self.player1.name
                    self.scr.listen()
                    self.load_player_data()
        else:
            if -50 <= y <= 50:
                if -550 <= x <= -50:
                    # choose player 1 name
                    name = turtle.textinput("Player ONE", "Enter your player name")
                    self.player1.name = name if ((name is not None) and (name != self.player2.name) and (0 < len(name) <= 10)) else self.player1.name
                    self.scr.listen()
                    self.load_player_data()
                elif 50 <= x <= 550:
                    # choose player 2 name
                    name = turtle.textinput("Player TWO", "Enter your player name")
                    self.player2.name = name if ((name is not None) and (name != self.player1.name) and (0 < len(name) <= 10)) else self.player2.name
                    self.scr.listen()
                    self.load_player_data()

    def _click_setup_sprite(self, x: float, y: float) -> None:
        """
        Handles a click in the sprite and colour selection menu

        Arguments:
            x (float): the x coordinate of the click
            y (float): the y coordinate of the click
        """
        if self.player1.player_num == 1:
            if (-300 <= y <= 500) and (-900 <= x <= -100):  # click the car
                self.cycle_car_sprite(self.player1)
            elif (-20 <= y <= 100) and (-60 <= x <= 460):   # click the colour box
                self.change_car_colour(self.player1)
            elif (-150 <= y <= -50) and (-70 <= x <= 285):  # click the buy button
                self._buy_car(self.player1)
        else:
            if -375 <= y <= 100:                            # click a car
                if -900 <= x <= -350:
                    self.cycle_car_sprite(self.player1)
                elif 350 <= x <= 900:
                    self.cycle_car_sprite(self.player2)
            if -40 <= y <= 40:                              # click a colour box
                if -310 <= x <= -90:
                    self.change_car_colour(self.player1)
                elif 90 <= x <= 310:
                    self.change_car_colour(self.player2)
            if -150 <= y <= -40:                            # click a buy button
                if -310 <= x <= -10:
                    self._buy_car(self.player1)
                elif 10 <= x <= 310:
                    self._buy_car(self.player2)

    def _click_setup(self, x: float, y: float) -> None:
        """
        handles a click in any of the setup menus

        Arguments:
            x (float): the x coordinate of the click
            y (float): the y coordinate of the click
        """
        if self.game_state == "menu game mode":     # player selection etc
            self._click_setup_game_mode(x, y)
        if self.game_state == "menu player name":   # player names
            self._click_setup_player_name(x, y)
        if self.game_state == "menu sprite select": # vehicle and colour selection
            self._click_setup_sprite(x, y)          # choose player 2 colour
        if -350 >= y >= -450 and -250 <= x <= 250:  # next button
            if all(self.can_move_next):
                self.next_menu()

    def click(self, x: float, y: float) -> None:
        """
        Called when a click occurs.
        Usually used for button functionality.

        Parameters:
        - x (float): The x-coordinate of the click.
        - y (float): The y-coordinate of the click.

        Returns:
        None
        """
        print(x, y)
        if self.game_state == "menu":
            self._click_menu(x, y)                  # main menu
        elif self.game_state == "paused":
            self._click_pause(x, y)                 # pause menu
        elif self.game_state.startswith("menu "):
            self._click_setup(x, y)                 # setup menus

    def next_menu(self) -> None:
        """
        Moves to the next player selection menu.

        This method is responsible for transitioning the game state to the next player selection menu.
        It updates the `game_state` attribute based on the current value of `game_state`.

        Possible transitions:
        - If the current `game_state` is "menu game mode", it changes `game_state` to "menu player name load".
        - If the current `game_state` is "menu player name", it changes `game_state` to "menu sprite select load".
        - If the current `game_state` is "menu sprite select", it changes `game_state` to "start".
        
        Returns:
        None
        """
        if self.game_state == "menu game mode":
            self.game_state = "menu player name load"
        elif self.game_state == "menu player name":
            self.game_state = "menu sprite select load"
        elif self.game_state == "menu sprite select":
            self.game_state = "load"

    def back_menu(self) -> None:
        """
        Moves back one player selection menu.

        This method is responsible for transitioning the game state back to the previous player selection menu.
        It updates the `game_state` attribute based on the current value of `game_state`.

        Possible transitions:
        - If the current `game_state` is "menu game mode", it changes `game_state` to "init".
        - If the current `game_state` is "menu player name", it changes `game_state` to "menu game mode load".
        - If the current `game_state` is "menu sprite select", it changes `game_state` to "menu player name".
        
        Returns:
        None
        """
        if self.game_state == "menu game mode":
            self.game_state = "init"
        elif self.game_state == "menu player name":
            self.game_state = "menu game mode load"
        elif self.game_state == "menu sprite select":
            self.game_state = "menu player name load"

    def load_player_data(self) -> None:
        """
        Loads all the coins and cars for the player
        """
        self.sub.data.check_exist(self.player1)
        self.sub.data.check_exist(self.player2)
        self.player1.score.coins = self.sub.data.db[self.player1.name]["coins"]
        self.player2.score.coins = self.sub.data.db[self.player2.name]["coins"]
        self.player1.construct()
        self.player2.construct()

    def change_car_colour(self, player: Player, color: str = "cycle") -> None:
        """
        Change the colour of a specified player to the given colour, unless it is not given, then cycle through the colour options
        
        Parameters:
        - player (Player): The player whose colour is to be changed.
        - color (str): The colour to change the player to. If not provided, the colours are cycled
        
        Returns:
        None
        """
        if color == "cycle":
            colors = ["blue", "red", "green", "yellow", "purple", "orange", "pink", "brown", "black", "white"]
            if self.colour_select_index[player.num-1] < len(colors)-1:
                self.colour_select_index[player.num-1] += 1
                color = colors[self.colour_select_index[player.num-1]]
            else:
                self.colour_select_index[player.num-1] = 0
                color = colors[self.colour_select_index[player.num-1]]
        player.attr.color = color
        player.construct()

    def change_car_sprite(self, player: Player, sprite: str = "random") -> None:
        """
        Change the sprite of the car to either a specified sprite or a random one
        #! random is now unused - selection is now handled via `cycle_car_sprite()`

        Arguments:
            player (Player): the player to change the sprite of
            sprite (str): the sprite to change to (default: "random")
        
        Returns:
            None
        """
        if sprite == "random":
            sprite = random.choice(["f1car", "ute"])
        player.attr.sprite = sprite
        player.attr.shape = f"{player.attr.sprite}{player.name}"
        player.construct()

    def cycle_car_sprite(self, player: Player) -> None:
        """
        Cycle through the available sprites for the car display in the sprite selector
        
        Parameters:
        - player (Player): The player whose sprite is to be changed
        
        Returns:
        None
        """
        # cycle through car options
        if self.car_select_index[player.num-1] < len(list(self.cars.keys()))-1:
            self.car_select_index[player.num-1] += 1
            car = list(self.cars.keys())[self.car_select_index[player.num-1]]
        else:
            self.car_select_index[player.num-1] = 0
            car = list(self.cars.keys())[self.car_select_index[player.num-1]]
        # change sprite and update button
        self.change_car_sprite(player, car)
        if car in self.sub.data.db[player.name]["cars"]:    # player has purchased the car
            self.can_move_next[player.num-1] = True
            self.sub.update.purchase_button("purchased", player)
        else:                                               # player does not have the car
            self.can_move_next[player.num-1] = False
            self.sub.update.purchase_button("buy", player, car)

    def _buy_car(self, player: Player) -> None:
        """
        Attempts the buy the currently equipped car

        Parameters:
            player (Player): the player attempting to buy the car

        Returns:
            None
        """
        if player.attr.sprite not in self.sub.data.db[player.name]["cars"]: # player does not already own the car
            cost = self.cars[player.attr.sprite]
            if player.score.coins > cost:                                   # must have enough coins to purchase the car
                player.score.coins -= cost
                self.sub.update.purchase_button("purchased", player)
                self.sub.data.db[player.name]["cars"].append(player.attr.sprite)
                self.can_move_next[player.num-1] = True

    def change_name(self, player: Player) -> None:
        """
        Changes the name of the player via a pop-up text input box
        #! unused

        Parameters:
        - player (Player): The player whose name is to be changed
        
        Returns:
            None
        """
        name = self.scr.textinput("Change Name", "Enter a new name")
        player.name = name if name is not None else player.name
        self.scr.listen()
        player.construct()
        m_trtl.clear()
        if self.num_of_players == 1:
            m_trtl.goto(-250,-50)
            self.sub.bg.rounded_rectangle(m_trtl, 100, len(self.player1.name), 10, "dark grey")
            m_trtl.goto(0,-50)
            m_trtl.write(self.player1.name, False, "center", ("comic sans", 50, "normal"))
        self.handle_keybinds()

    def setup_screen(self, height: int = 1080, width: int = 1920) -> turtle._Screen:
        """
        Creates and sets up the game screen.

        Parameters:
            height (int): The height of the game screen. Defaults to 1080.
            width (int): The width of the game screen. Defaults to 1920.

        Returns:
            turtle._Screen: The created and setup game screen.
        """
        # scr_tk = self.scr.getcanvas().winfo_toplevel()
        # scr_tk.overrideredirect(True) # windowed fullscreen
        # scrTk.attributes("-topmost", True)
        # screen._onkeypress = functools.partial(_onkeypress, screen)
        self.scr.setup(width, height)
        self.scr.reset()
        self.scr.delay(0)
        self.scr.title('"OMEGA RACE"!!!!!')
        self.setup_turtles()
        self.scr.tracer(0)
        return self.scr

    def exit(self) -> None:
        """close the game"""
        self.game_state = "quit"

    def spawn_coins(self) -> None:
        """
        Places collectable coins on the bottom straight of the track
        Assumes coins should be spawned
        
        Parameters:
            None

        Returns:
            None
        """
        for coin in self.coin_list:
            coin.show()

    def coins(self) -> None:
        """
        Attempts to spawn coins on the screen for the players to collect
        will only spawn coins if more than 500 frames have passed since the last coin was spawned
        
        Parameters:
            None

        Returns:
            None
        """
        if self.coin_frames > 750 and not any(coin.active for coin in self.coin_list):
            self.coin_frames = 0
            self.spawn_coins()
        self.coin_frames += 1
        self.update_coins()
        self.check_coin_collection()

    def update_coins(self) -> None:
        """
        Update the coins on the screen every frame to reflect them being hidden
        """
        for coin in self.coin_list:
            coin.render()

    def check_coin_collection(self) -> None:
        """
        check if any player has collided with any coins and picks them up

        Parameters:
            None

        Returns:
            None
        """
        for coin in self.coin_list:
            if coin.active:
                if self.player1.check_collision(coin):
                    self.player1.collect_coin(coin)
                    self.sub.update.coins()
                if self.player2.check_collision(coin):
                    self.player2.collect_coin(coin)
                    self.sub.update.coins()

    def setup_turtles(self) -> None:
        """
        setup all the turtles to the state needed
        """
        for t in TURTLES:
            t.ht()
            t.pu()
            t.clear()
        c_trtl.pencolor("white")
        s_trtl.pencolor("white")
        t_trtl.pencolor("white")
        ll_trtl.pencolor("white")
        lr_trtl.pencolor("white")

    def cheat(self) -> None:
        """Shhhhhhhhhhhhhhhh"""
        player_name = turtle.textinput("Cheat", "Enter your player name")
        amount = turtle.numinput("Cheat", "Enter the amount of coins to add")
        amount = int(amount) if amount is not None else 0
        self.sub.data.db[player_name]["coins"] += amount
        self.sub.data.save()
        self.scr.listen()

    def restart(self) -> None:
        """
        Restart the game, resetting all states and variables

        Parameters:
            None
        
        Returns:
            None
        """
        self.game_state = "start"
        self.player1.reset()
        self.player2.reset()
        self.game_start_time = time.now()

if __name__ == "__main__":
    raise WrongFileError("YOU RAN THE WRONG FILE AGAIN 🤦")
