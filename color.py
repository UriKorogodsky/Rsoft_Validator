class Color:
    def __init__(self, name, wavelength):
        self.name = name
        self.wavelength = wavelength

    def __repr__(self):
        return f'<Color: name={self.name}, wavelength={self.wavelength}, id={id(self)}>'

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.name == other.name and self.wavelength == other.wavelength:
            return True
        return False

    def __hash__(self):
        return hash((self.name, self.wavelength))

    @staticmethod
    def red():
        return Color('red', 0.637e-3)

    @staticmethod
    def green():
        return Color('green', 0.52e-3)

    @staticmethod
    def blue():
        return Color('blue', 0.45e-3)


red = Color.red()
green = Color.green()
blue = Color.blue()
