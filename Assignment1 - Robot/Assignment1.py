"""
29/03/2021
COSC343 Assignment 1
Group 1
Alec Fraser, Reuben Sweetman, Zack Molloy, Nick Sheetz
"""

#!/usr/bin/env python3
from ev3dev2.motor import OUTPUT_B, OUTPUT_C, MoveTank, SpeedPercent
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor, TouchSensor
from time import *


class Robot:
    """Class to set up and control ev3 Lego robot"""
    def __init__(self):
        self.drive = MoveTank(OUTPUT_B, OUTPUT_C)
        self.sound = Sound()
        self.touch = TouchSensor()
        self.touch.mode = 'TOUCH'
        self.cl = ColorSensor()
        self.cl.mode = 'COL-REFLECT'
        self.sensor = UltrasonicSensor()
        self.sensor.MODE_US_SI_CM

    def move_forward(self, rotations):
        """Moves the robot forward a given distance at a set speed.
        Args:
            rotations (int): How much the motors rotate forward.
        """
        self.sound.beep()
        self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), rotations)
        sleep(1)

    def move_back(self, rotations):
        """Moves the robot backwards a given distance at a set speed.
        Args:
            rotations (int): How much the motors rotate backwards.
        """
        self.sound.beep()
        self.drive.on_for_rotations(SpeedPercent(-10), SpeedPercent(-10), rotations)
        sleep(1)

    def rotate(self, deg):
        """Rotates the robot to reflect the input degree.
        Args:
            deg (int): Degrees to rotate the robot.
        """
        self.sound.beep()
        self.drive.on_for_degrees(SpeedPercent(10), SpeedPercent(-10), deg)
        sleep(1)

    def move_tiles(self, tiles):
        """Moves the robot forward a given number of black titles in a straight line.
        Args:
            tiles (int): Number of black tiles to move forward over.

        Return:
            int: black_count which is the tile number that the robot is currently on.
        """
        black_count = 1  # Starts at one for initial black tile.
        distance = 1.15
        self.sound.speak(str(black_count))
        self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 1)

        # Moves set distance and checks tile colour.
        while black_count < tiles:
            current_colour = self.cl.value()
            if self.is_black(current_colour):  # Increments black tile count.
                black_count += 1
                if black_count == tiles:  # Breaks once count has been reached.
                    self.sound.speak(str(black_count))
                    return black_count
                self.sound.speak(str(black_count))

                self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
                sleep(0.5)

            # When robot has gone off course, use correction method.
            if self.is_black(current_colour) is False and self.is_white(current_colour) is False:
                self.corrections(distance)
                current_colour = self.cl.value()
                if self.is_black(current_colour):
                    black_count -= 1

    def corrections(self, distance):
        """Corrects the robots path when it deviates from the straight line.
        Args:
            distance (int): Distance for the robot to move for correction.
        """
        # Checks to the left if there is black / grey ground (-1 to 0).
        self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 180)
        sleep(0.5)
        left_colour = self.cl.value()

        sleep(0.5)
        # Go back original spot from left movement.
        self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(-15), 180)
        sleep(0.5)
        # Checks to the right hand side ground colour (-1 to 0).
        self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 180)
        sleep(0.5)
        right_colour = self.cl.value()

        sleep(0.5)
        # Go back original spot from right movement.
        self.drive.on_for_degrees(SpeedPercent(-15), SpeedPercent(0), 180)

        # Move back and correct angle if tile to the right is black
        if self.is_black(right_colour):

            self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 20)

            self.drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), distance)
            sleep(0.5)
            self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 40)
            sleep(0.5)

        # Move back and correct angle if tile to the left is black
        elif self.is_black(left_colour):

            self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 20)

            self.drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), distance)
            sleep(0.5)
            self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 40)
            sleep(0.5)

    def moveRows(self, rows, n):
        """Moves the robot down a given number of rows to the tower search area.
        Args:
            rows (int): Number of rows to move.
            n (int): The black tile number the robot is starting on.

        Returns:
            int: The black tile number that robot is currently on.
        """
        count = 0
        distance = 2.31
        # Move one row at a time until desired row is reached.
        while count < rows:
            self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
            current_colour = self.cl.value()
            sleep(0.5)
            # Runs correction method if robot has gone out of alignment.
            if self.is_white(current_colour):
                self.corrections(distance)
            else:
                n += 15  # Keeping track of which black tile the robot is currently on.
                self.sound.speak(str(n))
                count += 1
        return n

    def sonar(self, rows, n):
        """Robot traverses search area using sonar to check each row for the tower.
        Args:
            rows (int): Number of rows in search area.
            n (int): The black tile number that robot is currently on.
        """
        count = 0
        distance = 2.31

        # Checks the give number of rows
        while count < rows:
            self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
            current_colour = self.cl.value()
            sleep(0.5)
            # If tile is white, use correction method.
            if self.is_white(current_colour):
                self.corrections(distance)
            else:
                n+=15  # To count black tiles.
                self.sound.speak(str(n))
                # Drives backwards then turns 90 degrees left (middle of big tiles).
                self.drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), distance-1.2)
                self.drive.on_for_degrees(SpeedPercent(-10), SpeedPercent(10), 168)
                sleep(0.5)
                # Looks down the length of the row. If sonar detects anything within value 900, robot goes down that row
                if self.sensor.value() < 900:
                    self.go_down_lane(count)
                    return
                # Turns and moves onto next row.
                self.drive.on_for_degrees(SpeedPercent(10), SpeedPercent(-10), 168)
                self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance-1.2)
                # Checks current tile, if white run corrections method.
                if self.is_white(current_colour):
                    self.corrections(distance-1.2)
                self.sound.speak(str(n))
                count += 1  # Increment row number

    def go_down_lane(self, count):
        """Robot looks down row/lane and slowly moves forward until tower position is certain using sonar.
        Args:
            count (int): Row number to calculate tower position.
        """
        distance = 1.4
        n = 1

        # Senor value greater than 400 move closer.
        while self.sensor.value() > 400:
            self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
            n+=1  # Increment tower tile number.
        # If row 1, n value = tower location.
        if count == 1:  # If tower is in row 2, add 3 to n.
            n = n+3
        elif count == 2:  # If tower is in row 3, add 6 to n.
            n = n+6
        elif count == 3:  # If tower is in row 4, add 9 to n.
            n=n+9
        self.result(n)

    def result(self, n):
        """Method to sound out that the tower has been located and on which square.
        Args:
            n (int): Value of tower location.
        """
        self.sound.speak("located tower")
        self.sound.speak("tower in square"+str(n))

    def is_black(self, value):
        """Checks if the current tile the robot is on is black.
        Args:
            value (int): Value from robots sensor.
        Returns:
            bool: True if value is in range of a black tile.
        """
        if value <= 13:
            return True
        return False

    def is_white(self, value):
        """Checks if the current tile the robot is on is white.
        Args:
            value (int): Value from robots sensor.
        Returns:
            bool: True if value is in range of a white tile.
        """
        if value >= 48:
            return True
        return False


def main():
    # Initialize robot.
    r = Robot()
    # Movement to set robot on first black tile, facing 90 degrees right.
    r.move_forward(0.8)
    r.rotate(168)
    # Move robot 10 black tiles.
    n = r.move_tiles(10)
    # 90 degree right rotation and small adjustments to set robot in optimal position.
    r.move_forward(0.1)
    r.rotate(165)
    r.move_back(0.25)
    # Moves robot down rows to search area.
    n = r.moveRows(3, n)
    # Search rows for tower using sonar feature
    r.sonar(4, n)
    r.sound.beep()


main()
