#!/usr/bin/env python3
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, MoveTank, SpeedPercent
from ev3dev2.sound import Sound
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor
from time import *


class Robot:
    def __init__(self):
        self.drive = MoveTank(OUTPUT_B, OUTPUT_C)
        self.sound = Sound()
        self.cl = ColorSensor()
        self.cl.mode = 'COL-REFLECT'
        self.sensor = UltrasonicSensor()


    def move_forward(self, rotations):
        self.sound.beep()
        self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), rotations)
        sleep(1)

    def rotate(self, deg):
        self.sound.beep()
        self.drive.on_for_degrees(SpeedPercent(10), SpeedPercent(-10), deg)
        sleep(1)

    def move_tiles(self, tiles):
        black_check = False
        black_count = 1
        distance = 1.15
        prev_colour = self.cl.value()
        self.sound.speak(str(black_count))
        self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 1)

        while black_count < tiles:
            current_colour = self.cl.value()
            if self.is_black(current_colour):
                black_count += 1
                if black_count == tiles:
                    self.sound.speak(str(black_count))
                    return
                self.sound.speak(str(black_count))
                black_check = True
                self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
                sleep(0.5)
            # if self.is_white(current_colour):
            #      prev_colour = current_colour
            #      black_check = False
            #      self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), 0.50)

            if self.is_black(current_colour) is False and self.is_white(current_colour) is False:
                self.sound.speak("current colour" + str(current_colour))
                self.sound.speak("correction")
                self.corrections(distance)
                current_colour = self.cl.value()
                if self.is_black(current_colour):
                    black_count -= 1
                    black_check = False

        #changed from -10 to 0 when rotating
    def corrections(self, distance):
        self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 180)  # check to the left if there is black / grey (-1 to 0)
        sleep(0.5)
        left_colour = self.cl.value()
        self.sound.speak("left colour" + str(left_colour))
        sleep(0.5)
        self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(-15), 180)  # go back original spot from left
        sleep(0.5)
        self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 180)  # checks the right hand side (-1 to 0)
        sleep(0.5)
        right_colour = self.cl.value()
        self.sound.speak("right colour" + str(right_colour))
        sleep(0.5)
        self.drive.on_for_degrees(SpeedPercent(-15), SpeedPercent(0), 180) # go back original spot from right

        if self.is_black(right_colour):
            self.sound.speak("black tile is right")
            self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 20)
            self.sound.speak("back up now")
            self.drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), distance)
            sleep(0.5)
            self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 40)
            sleep(0.5)
        elif self.is_black(left_colour):
            self.sound.speak("black tile is left")
            self.drive.on_for_degrees(SpeedPercent(15), SpeedPercent(0), 20)
            self.sound.speak("back up now")
            self.drive.on_for_rotations(SpeedPercent(-15), SpeedPercent(-15), distance)
            sleep(0.5)
            self.drive.on_for_degrees(SpeedPercent(0), SpeedPercent(15), 40)
            sleep(0.5)

    def moveRows(self, rows):
        n = 10
        count = 0
        distance = 2.25
        while count < rows:
            self.drive.on_for_rotations(SpeedPercent(15), SpeedPercent(15), distance)
            current_colour = self.cl.value()
            sleep(0.5)
            if self.is_white(current_colour):
                self.sound.speak("on white tile correction")
                self.corrections(distance)
            else:
                n += 15
                self.sound.speak(str(n))
                count += 1

    # def sonar(self):
    #     self.drive.on_for_degrees(SpeedPercent(-15), SpeedPercent(15), 90)

    def is_black(self, value):
        if value <= 13:
            return True
        return False

    def is_white(self, value):
        if value >= 48:
            return True
        return False


def main():
    r = Robot()
    r.move_forward(0.8)
    r.rotate(168)
    r.move_tiles(10)
    r.move_forward(0.1)
    r.rotate(165)
    r.moveRows(3)
    r.sound.beep()


main()
