import random

from .constants import SHAPES

class SevenBag:
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.sequence = []

    def _extend(self):
        bag = list(SHAPES.keys())
        self.rng.shuffle(bag)
        self.sequence.extend(bag)

    def get(self, index: int) -> str:
        while index >= len(self.sequence):
            self._extend()
        return self.sequence[index]