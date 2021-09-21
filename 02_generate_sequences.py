from chords.ChordSequence import ChordSequence

cs = ChordSequence()
dd = cs.generate_sequences()

for key, value in dd.items():
    print(f"{key}, {key}")
    print(f"    {value['out']}")

