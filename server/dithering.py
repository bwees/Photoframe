from PIL import Image, ImageDraw
from math import sqrt
from time import time
import sys
from os import mkdir
from dataclasses import dataclass

class Color:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __hash__(self):
        return hash((self.r, self.g, self.b))
    
    def __eq__(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b
    

def color_addition(first_color: Color, second_color: Color):
    return Color(first_color.r + second_color.r, first_color.g + second_color.g, first_color.b + second_color.b)

def color_multiplication(value: float, color: Color):
    return Color(round(value * color.r), round(value * color.g), round(value * color.b))

def pixel_to_color(pixel):
    return Color(pixel[0], pixel[1], pixel[2])


def process(image: Image, pallete: list[Color]):
    """put all pixel data inside a 2d array for faster operations"""

    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            color = Color(pixel[0], pixel[1], pixel[2])
            new_color = nearest_color(color, pallete)
            distance_error = Color(color.r - new_color.r,
                                   color.g - new_color.g, color.b - new_color.b)

            draw = ImageDraw.Draw(image)
            draw.point((x, y), (new_color.r, new_color.g, new_color.b))

            if (x+1 < image.width and y+1 < image.height):
                """ugly Floyd–Steinberg dithering

                https://en.wikipedia.org/wiki/Floyd%E2%80%93Steinberg_dithering

                todo: find a way to do each step on one line
                """
                temp_color = color_addition(
                    pixel_to_color(image.getpixel((x+1, y))),
                    color_multiplication(7/16, distance_error))

                draw.point((x+1, y), (temp_color.r,
                           temp_color.g, temp_color.b))

                temp_color = color_addition(
                    pixel_to_color(image.getpixel((x-1, y+1))),
                    color_multiplication(3/16, distance_error))

                draw.point((x-1, y+1), (temp_color.r,
                           temp_color.g, temp_color.b))

                temp_color = color_addition(
                    pixel_to_color(image.getpixel((x, y+1))),
                    color_multiplication(5/16, distance_error))

                draw.point((x, y+1), (temp_color.r,
                           temp_color.g, temp_color.b))

                temp_color = color_addition(
                    pixel_to_color(image.getpixel((x+1, y+1))),
                    color_multiplication(1/16, distance_error))

                draw.point((x+1, y+1), (temp_color.r,
                           temp_color.g, temp_color.b))

    return image


def nearest_color(old_color: Color, pallete: list[Color]):
    """change the current color to the nearest color available"""

    new_color = pallete[0]
    min_distance = distance(old_color, pallete[0])

    for color in pallete:
        new_distance = distance(color, old_color)

        if (new_distance < min_distance):
            new_color = color
            min_distance = new_distance

    return new_color


def distance(first_color: Color, second_color: Color):
    """return the distance between 2 colors"""
    return sqrt((first_color.r - second_color.r) ** 2 + (first_color.g - second_color.g) ** 2 + (first_color.b - second_color.b) ** 2)