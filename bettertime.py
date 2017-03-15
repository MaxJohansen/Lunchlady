from datetime import time


class HumanTime(time):
    """ Defines methods to see if a time occurs before another time. """
    def after(self, other):
        return other < self

    def before(self, other):
        return self < other

    def __str__(self):
        return super().__str__()[:-2]