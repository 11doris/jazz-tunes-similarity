import functools
from typing import List, Optional
from chords.symbol.parts.noteSymbol import Note
import re

class Symbol:
    def __init__(self, root:int, components:List[int], bass:Optional[int]):
        self.root = root
        self.components = components
        self.bass = bass

    def toString(self, includeRoot=True, keyLess=False, includeBass=True) -> str:
        self.notesLeft = self.components.copy()

        # each method takes notes away the relevant note(s) from notesLeft
        sus =       self.getSus()
        augdim =    self.getAugDim()
        seventh =   self.getSeventh()
        minmaj =    self.getMinMaj()

        additions = self.getAdditions()

        note = ""
        if includeRoot: note = Note(self.root).toSymbol()
        if includeRoot and keyLess: note = str(self.root)
        bass = ""
        if includeBass:
            if self.bass is not None:
                bass = f"/{Note(self.bass).toSymbol()}"

        chord_formatted = note + minmaj + augdim + seventh + additions + sus + bass
        #print(f"\nnote: {note}\nminmaj: {minmaj}\naugdim: {augdim}\nseventh: {seventh}\nadditions: {additions}\nsus: {sus}\nbass: {bass}")

        # fix for chords
        chord_formatted = chord_formatted.replace('5sus4', 'sus4')
        chord_formatted = chord_formatted.replace('m(+b13)', 'm(+b6)')
        chord_formatted = chord_formatted.replace('7(+b5)(+b9)(+#9)(+b13)', '7alt')

        return chord_formatted


    def toLeadSheetStyle(self, includeRoot=True, keyLess=False, includeBass=True) -> str:
        self.notesLeft = self.components.copy()

        # each method takes notes away the relevant note(s) from notesLeft
        sus =       self.getSus()
        augdim =    self.getAugDim()
        seventh =   self.getSeventh()
        minmaj =    self.getMinMaj()

        additions = self.getAdditions()
        additions = "alt" if additions == "(+b5)(+b9)(+#9)(+b13)" else additions

        note = ""
        if includeRoot: note = Note(self.root).toSymbol()
        if includeRoot and keyLess: note = str(self.root)
        bass = ""
        if includeBass:
            if self.bass is not None:
                bass = f"/{Note(self.bass).toSymbol()}"

        #print()
        #print(f"{note}, {minmaj}, {augdim}, {seventh}, {additions}, {sus}, {bass}")

        root = note
        if 'b' in note:
            root1 = note.replace('b', '')
            root2 = 'flat'
        elif '#' in note:
            root1 = note.replace('#', '')
            root2 = 'sharp'
        else:
            root1 = note
            root2 = 'natural'

        aug = augdim if 'aug' in augdim else ''
        dim = augdim if ('dim' in augdim) or ('m7b5' in augdim) else ''

        add = []
        add = additions.split(')(')                     # split multiple alteratons
        add = [re.sub(r'\(|\)', '', el) for el in add]  # remove brackets
        add.append('+#5') if aug != '' else add
        add = [el for el in add if el != '']

        if len(add) == 2:
            down = minmaj + dim + seventh + sus + bass
            alt = add
        else:
            down = minmaj + dim + seventh + sus + ''.join(add) + bass
            alt = []

        #print(f"before: {down}, {alt}")

        down = "m+b6" if down == 'm+b13' else down
        down = re.sub(r'm7b5\+9', 'ø9', down)
        down = re.sub(r'dim', 'o', down)
        down = re.sub(r'M', 'Δ', down)
        down = re.sub(r'm7b5', 'ø7', down)
        #down = re.sub(r'm', '–', down) # use the longer dash
        down = re.sub(r'm', '-', down)  # use the normal dash
        down = re.sub(r'b', '♭', down)
        down = re.sub(r'#', '♯', down)
        down = re.sub(r'6\+9', '6/9', down)
        down = re.sub(r'\+9', 'add9', down)
        down = re.sub(r'\+', '', down)
        down = re.sub(r'aug', '♯5', down)
        down = re.sub(r'sus4', 'sus', down)
        down = "sus" if down == '5sus' else down

        alt = [re.sub(r'b', '♭', el) for el in alt]
        alt = [re.sub(r'#', '♯', el) for el in alt]
        alt = [re.sub(r'\+', '', el) for el in alt]

        #print(f"after:  {down}, {alt}")

        chord_parts = {
            'root1': root1,
            'root2': root2,
            'down': down,
            'alt-up': alt[0] if len(alt) == 2 else "",
            'alt-down': alt[1] if len(alt) == 2 else "",
        }
        #print(chord_parts)

        return chord_parts


    def getSus(self) -> str:
        r = lambda x: self.notesLeft.remove(x)
        if self.match([-3, -4,  5]): r(5);       return "sus4"
        return ""

    def getMinMaj(self) -> str:
        r = lambda x: self.notesLeft.remove(x)
        if self.match([ 3,  4]): r(4); return "" # add(#9) will follow since 3 is still here
        if self.match([-3,  4]): r(4); return ""
        if self.match([ 3, -4]): r(3); return "m"
        if self.match([-3, -4]):       return ""
        return ""

    def getAugDim(self) -> str:
        r = lambda x: self.notesLeft.remove(x)
        if self.match([3, -4, 6, -7, -8, -9, -10, -11]): r(3); r(6); return "dim"
        if self.match([3, -4, 6, -7, -8, -9, -10, 11]): r(3); r(6); r(11); return "dimM7"
        if self.match([ 3, -4, 6, -7, -8, 9]): r(3); r(6); r(9); return "dim7"
        if self.match([ 3, -4, 6, 10]): r(3); r(6); r(10); return "m7b5"
        if self.match([-6, -7,  8]): r(8); return "aug"
        return ""

    def getSeventh(self) -> str:
        r = lambda x: self.notesLeft.remove(x)
        if self.match([9, 10]): r(9); r(10); return "13"
        if self.match([9, 11]): r(9); r(11); return "M13"
        if self.match([5, 10]): r(5); r(10); return "11"
        if self.match([5, 11]): r(5); r(11); return "M11"
        if self.match([2, 10]): r(2); r(10); return "9"
        if self.match([2, 11]): r(2); r(11); return "M9"
        #if self.match([2, 4, 7, -9, -10]): r(2); r(4); r(7); return "2"
        if self.match([-3, -4, -5, 7, -10, -11]): r(7); return "5"

        if self.match([9]): r(9);   return "6"
        if self.match([10]): r(10); return "7"
        if self.match([11]): r(11); return "M7"
        return ""

    def getAdditions(self) -> str:
        additions = []
        if self.match([6, -7]): additions += ["b5"]
        if self.match([1]): additions += ["b9"]
        if self.match([2]): additions += ["9"]
        if self.match([3]): additions += ["#9"]
        if self.match([5]): additions += ["11"]
        if self.match([6, 7]): additions += ["#11"]
        if self.match([8]): additions += ["b13"]
        return functools.reduce(lambda prev, curr: f"{prev}(+{curr})", additions, "")

    # returns true if the positive numbers are all in notesLeft AND the negative numbers are not
    def match(self, notes:List[int]) -> bool:
        for note in notes:
            # if positive, note should be in sequence
            if note >= 0 and not note in self.notesLeft:
                return False
            # if negative, note cannot be in sequence
            if note < 0 and -note in self.notesLeft:
                return False

        return True