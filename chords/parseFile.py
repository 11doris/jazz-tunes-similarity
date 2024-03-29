import xml.etree.ElementTree as ET
from dataset.xmlChildren import getChild, getChildren
from dataset.chordFromXML import ChordXML


def get_chords(measure, key, beat_time):
    # each measure (beat) has multiple harmonies (chords)
    harmonies = getChildren(measure, "harmony")
    notes = getChildren(measure, 'note')

    # parse the harmony tag with Chord().toJson and put it into the json file
    chords = []
    for harmony in harmonies:
        chord = ChordXML(harmony, key)  # chord.key is the default key of the tune, 0 = C!
        keynumber = chord.key
        chords += [chord.toJson()]
    # chords = [Chord(harmony, key).toJson() for harmony in harmonies]

    # parse the length of the chord to determine on which beat it is played
    beats = []

    if beat_time['beats'] == 4 and beat_time['beat_time'] == 4:
        for note in notes:
            d = int(getChild(note, 'duration').text)
            assert (d % 768 == 0)

            current_beat = 1 if len(beats) == 0 else next_beat
            next_beat = int(current_beat + d/768)

            beats += [current_beat]

    elif beat_time['beats'] == 3 and beat_time['beat_time'] == 4:
        # the distribution of chords to beats in a 3/4 time signature is buggy in musicXML since the 3 beats are distributed to 4 beats.
        # pragmatic approach: if 2 chords in a bar, first one takes 2 bars, second one 1 bar.
        if len(notes) == 1:
            beats = [1]
        elif len(notes) == 2:
            beats = [1, 2]
        elif len(notes) == 3:
            beats = [1, 2, 3]
        else:
            raise NotImplementedError('unsupported time signature for 3/4.')

    elif beat_time['beats'] == 5 and beat_time['beat_time'] == 4:
        # the distribution of chords to beats in a 5/4 time signature is buggy in musicXML.
        # pragmatic approach: if 2 chords in a bar, first one takes 2 bars, second one 1 bar.
        if len(notes) == 1:
            beats = [1]
        elif len(notes) == 2:
            beats = [1, 3]
        elif len(notes) == 3:
            beats = [1, 3, 4]
        elif len(notes) == 4:
            beats = [1, 2, 3, 4]
        else:
            raise NotImplementedError(f'unsupported number of chords {len(notes)} per bar for 5/4.')

    elif beat_time['beats'] == 6 and beat_time['beat_time'] in [4, 8]:
        # the distribution of chords to beats in a 5/4 time signature is buggy in musicXML.
        # pragmatic approach: if 2 chords in a bar, first one takes 2 bars, second one 1 bar.
        if len(notes) == 1:
            beats = [1]
        elif len(notes) == 2:
            beats = [1, 3]
        elif len(notes) == 3:
            beats = [1, 3, 4]
        else:
            raise NotImplementedError(f'unsupported number of chords {len(notes)} per bar for 5/4.')

    else:
        raise NotImplementedError('unsupported beat.')

    if (len(beats) != len(chords)):
        print("bla")

    out = {}
    for i in range(len(beats)):
        out[beats[i]] = chords[i]

    return out, keynumber


def parseFile(file):
    # get the first child element with tag part, this is the song
    root = ET.parse(file).getroot()
    part1 = getChild(root, "part")

    identification = getChild(root, "identification")
    creator = getChildren(identification, "creator")
    composer = ""
    style = ""
    for el in creator:
        if el.attrib['type'] == 'composer':
            composer = el.text
        elif el.attrib['type'] == 'lyricist':
            style = el.text

    # get the song key xml information; the actual key is parsed with get_chords() further down
    attribute = getChild(part1[0], "attributes")
    key = getChild(attribute, "key")
    keynumber = None
    mode = getChild(key, "mode").text

    # get the beat measure information
    beats = getChild(attribute, 'time')
    beat_time = {'beats': int(getChild(beats, "beats").text),
                 'beat_time': int(getChild(beats, "beat-type").text)}

    out = {}
    beats = {}
    sections = {}
    sections_xml = {}
    repeat_from = None
    ending1 = None
    measure_num_real = 0
    find_section = None
    max_num_chords_per_bar = 0

    # loop over all bars
    for measure in part1:
        measure_num_real += 1
        measure_num_xml = int(measure.attrib["number"])
        out[measure_num_real] = {}
        # print(f'Measure XML file: {measure_num_xml}, Real Measure: {measure_num_real}----- ')

        # make sure that the first bar is labeled with section 'A'
        if measure_num_real == 1:
            sections[measure_num_real] = 'A'
            sections_xml[measure_num_xml] = 'A'

        out[measure_num_real], keynumber = get_chords(measure=measure, key=key, beat_time=beat_time)

        # update the variable to contain the maximum number of chords per bar for this tune
        if len(out[measure_num_real]) > max_num_chords_per_bar:
            max_num_chords_per_bar = len(out[measure_num_real])

        for elem in list(measure):

            # find section indicators A, B, C etc ('Rehearsal' xml tag)
            find_direction = elem.find('direction-type')
            if find_direction is not None:
                find_section = find_direction.find('rehearsal')
                if find_section is not None:
                    # print(f"Bar {measure_num_real}, Section {find_section.text}")
                    sections[measure_num_real] = find_section.text
                    sections_xml[measure_num_xml] = find_section.text

            # handle repetitions
            # print(f'    {elem}')
            # search for first or second endings
            find_ending = elem.find('ending')
            if find_ending is not None:
                if find_ending.attrib['type'] == 'start':
                    ending1 = measure_num_xml

            find_repeat = elem.find('repeat')
            if find_repeat is not None:
                if find_repeat.attrib['direction'] == 'forward':
                    repeat_from = measure_num_xml
                elif find_repeat.attrib['direction'] == 'backward':
                    if ending1 is None:
                        repeat_end = measure_num_xml + 1
                    else:
                        repeat_end = ending1
                    # print(f'looping over the bars {repeat_from} to {repeat_end}')

                    # by convention, if repeat forward sign is missing, repeat from start
                    if repeat_from is None:
                        repeat_from = 1

                    for i in range(repeat_from, repeat_end):
                        measure_num_real += 1
                        out[measure_num_real] = out[i]
                        if i in sections_xml.keys():
                            # print(f"Bar real {measure_num_real}, xml {measure_num_xml}, Section {sections_xml[i]}")
                            sections[measure_num_real] = sections_xml[i]

                    find_section = None
                    repeat_from = None
                    ending1 = None

    _meta_info = {'default_key': {'key': keynumber,
                                  'mode': mode
                                  },
                  'composer': composer,
                  'style': style,
                  'sections': sections,
                  'num_bars': measure_num_real,
                  'time_signature': beat_time,
                  'max_num_chords_per_bar': max_num_chords_per_bar,
                  }

    return out, _meta_info
