class ScaleType(Enum):
    IONIAN = (0, 2, 4, 5, 7, 9, 11)
    DORIAN = (0, 2, 3, 5, 7, 9, 10)
    MAJOR = IONIAN

class Scale:
    tonic: int
    scale: ScaleType

    def num_degrees():
        pass

