from color import Color, red, green, blue
from typing import Any, Optional
from dataclasses import dataclass
from enum import Enum


class ColorIterator:
    @staticmethod
    def color_iterator():
        return iter([red, green, blue])

    @staticmethod
    def ordered_colors(main_color: Color):
        colors = list(ColorIterator.color_iterator())
        colors.remove(main_color)
        colors.insert(0, main_color)
        return iter(colors)


# @dataclass(unsafe_hash=True)  # TODO: investigate if unsafe hashing can cause problems
@dataclass()  # TODO: investigate if unsafe hashing can cause problems
class RgbContainer(ColorIterator):
    red: Optional[Any] = None
    green: Optional[Any] = None
    blue: Optional[Any] = None

    # this lets us access the correct color elements with either self.green or self[green]
    def __getitem__(self, item):
        if item == red:
            return self.red
        elif item == green:
            return self.green
        elif item == blue:
            return self.blue
        raise KeyError(f'{item} is not {red}, {green} or {blue}.')

    def __setitem__(self, key, value):
        if key not in self.color_iterator():
            raise KeyError(f'{key} is not {red}, {green} or {blue}.')
        if key == red:
            self.red = value
        elif key == green:
            self.green = value
        elif key == blue:
            self.blue = value

    def __contains__(self, item):
        if item in self.__iter__():
            return True
        return False

    def __iter__(self):
        elements = []
        for color in self.color_iterator():
            elements.append(self[color])
        return iter(elements)

    def __hash__(self):
        return (id(self.red), id(self.green), id(self.blue)).__hash__()


class PathEnum(Enum):
    left = 0
    right = 1


class PathContainer():
    right: RgbContainer = None
    left: RgbContainer = None

    def __init__(self, right=None, left=None):
        self.right = right or RgbContainer()
        self.left = left or RgbContainer()

    def __iter__(self):
        return iter(self.elements())

    def __getitem__(self, item):
        return self.getPath(item)

    def __setitem__(self, key: PathEnum, value:RgbContainer):
        if key is PathEnum.left:
            self.left = value
        else:
            self.right = value

    def getPath(self, enum: PathEnum):
        if enum is PathEnum.left:
            return self.left
        return self.right

    def size(self):
        return 2*3

    @staticmethod
    def __get_color_enum__(num):
        counter = 0
        for i in RgbContainer.color_iterator():
            if(counter == num):
                break
            counter+=1
        return i

    def elements(self):
        return [self.left, self.right]

    @staticmethod
    def color(index):
        num_rgb = 3  # TODO compute properly number of members of RGB
        color_ind = index % num_rgb
        color = PathContainer.__get_color_enum__(color_ind)
        return color

    def get_elem_color(self, index):
        num_rgb = 3 #TODO compute properly number of members of RGB
        elem  = int(index/num_rgb)
        color_ind = index%num_rgb
        color = self.__get_color_enum__(color_ind)
        return elem, color

    def get(self, index):
        elem, color = self.get_elem_color(index)
        return self.elements()[elem][color]

    def set(self, index, new_element):
        elem, color = self.get_elem_color(index)
        self.elements()[elem][color] = new_element


