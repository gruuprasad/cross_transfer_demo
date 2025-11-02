from enum import Enum

class TrackType(Enum):
    NORMAL = 0
    CROSS = 1

class TrackState(Enum):
    STRAIGHT = 0
    CROSS = 1

class TrackInfo:
    # default direction is towards positive axis
    def __init__(self, prim, direction=[1, 1, 0,]):
        self.prim = prim
        self.direction = direction

    def __repr__(self):
        return f"TrackInfo(prim={self.prim}, direction={self.direction})"
