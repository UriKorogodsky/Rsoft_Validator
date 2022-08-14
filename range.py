from consts import *
from color import *


class Range:
    def __init__(self, variable_range):
        self.range = variable_range
        self.min = np.min(variable_range)
        self.max = np.max(variable_range)
        self.mean = np.mean([self.min, self.max])
        self.scale = self.max - self.mean

    def denormalize_param(self, value):
        if type(value) is bool:
            return value
        value *= self.scale
        return value + self.mean

    def normalize_param(self, value):
        if type(value) is bool:
            return value
        value -= self.mean
        return value / self.scale

