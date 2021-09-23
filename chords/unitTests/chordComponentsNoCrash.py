import random
from chords.chord import Chord
from chords.randomChord import randomChord

# check if random components don't crash
random.seed(420)
for i in range(100000):
    rc = randomChord(random)
    print(rc.toSymbol())
    assert isinstance(rc, Chord)
    assert isinstance(rc.toString(), str)
    assert isinstance(rc.toSymbol(), str)

