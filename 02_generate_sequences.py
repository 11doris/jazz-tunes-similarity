from chords.ChordSequence import ChordSequence

cs = ChordSequence()
dd = cs.read_data()

print(dd)

for key, value in dd.items():
    print(f"{key}, {dd[key]['title']}")
    print(f"    {value}")

