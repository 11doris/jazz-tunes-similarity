from chords.ChordSequence import ChordSequence


def _get_test_sequence():
    return [['a'],
            ['a', 'b'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c', 'd']]


def test_fill_up_bars_with_max_chords():
    cs = ChordSequence(config="../config.json")

    ## 4 Beats per Measure

    # Test with 4 chords, 4 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq, 4)
    assert seq[0] == ['a', 'a', 'a', 'a']
    assert seq[1] == ['a', 'a', 'b', 'b']
    assert seq[2] == ['a', 'a', 'b', 'c']
    assert seq[3] == ['a', 'b', 'c', 'd']

    # Test with 3 chords, 4 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:3], 4)
    assert seq[0] == ['a', 'a', 'a', 'a']
    assert seq[1] == ['a', 'a', 'b', 'b']
    assert seq[2] == ['a', 'a', 'b', 'c']

    # Test with 2 chords, 4 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:2], 4)
    assert seq[0] == ['a', 'a']
    assert seq[1] == ['a', 'b']

    # Test with 1 chord, 4 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:1], 4)
    assert seq[0] == ['a']

    ## 3 Beats per Measure

    # Test with 3 chords, 3 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:3], 3)
    assert seq[0] == ['a', 'a', 'a']
    assert seq[1] == ['a', 'a', 'b']
    assert seq[2] == ['a', 'b', 'c']

    # Test with 2 chords, 3 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:2], 3)
    assert seq[0] == ['a', 'a', 'a']
    assert seq[1] == ['a', 'a', 'b']

    # Test with 1 chord, 3 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:1], 3)
    assert seq[0] == ['a']

    ## 2 Beats per Measure

    # Test with 2 chords, 2 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:2], 2)
    assert seq[0] == ['a', 'a']
    assert seq[1] == ['a', 'b']

    # Test with 1 chord, 2 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:1], 2)
    assert seq[0] == ['a']

    ## 5 Beats per Measure

    # Test with 2 chords, 5 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:2], 5)
    assert seq[0] == ['a', 'a']
    assert seq[1] == ['a', 'b']

    # Test with 1 chord, 2 beats per measure
    seq = _get_test_sequence()
    seq = cs.fill_up_bar(seq[0:1], 5)
    assert seq[0] == ['a']