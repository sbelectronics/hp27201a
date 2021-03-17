# HP27201A speech output module, driver
# Scott Baker, http://www.smbaker.com/

from __future__ import print_function
import sys
import time

from globals import ERROR, WARNING, INFO, DEBUG

XON = chr(0x11)

class word:
    def __init__(self, group, index, name, contents):
        self.group = group
        self.index = index
        self.name = name
        self.contents = contents


class hp27201a:
    def __init__(self, vocabFilename, interface, verbosity=INFO):
        self.interface = interface
        self.vocabFilename = vocabFilename
        self.words = {}
        self.groups = {}
        self.verbosity = verbosity

        if self.vocabFilename:
            self.loadVocab(vocabFilename)

    def CLE(self, group=None):
        if group:
            return "\x1B&ySCLE %d;\x1B&yU" % group
        else:
            return "\x1B&ySCLE A;\x1B&yU"

    def DOW(self, group, number, kind, contents):
        return "\x1B&ySDOW %d.%d %d %s %s;\x1B&yU\x11" % (group, number, len(contents)/2, "V", contents)

    def ID(self):
        return "\x1B&yI\x11"

    def RES(self):
        return "\x1B&ySRES;\x1B&yU"

    def PIT(self, level):
        if level.upper() in ["H", "HIGH"]:
            return "\x1B&ySPIT H;\x1B&yU"
        elif level.upper() in ["M", "MEDIUM", "MED"]:
            return "\x1B&ySPIT M;\x1B&yU"                
        else:
            return "\x1B&ySPIT L;\x1B&yU"            

    def SPE(self, group, number):
        return "\x1B&ySSPE %d.%d;\x1B&yU" % (group, number)

    def STA(self, short):
        if short:
            # short status, only buffer remaining
            return "\x1B&ySSTA S;\x1B&yU\x11"
        else:
            # long status, 7 characters of info
            #   1st byte
            #      "C" after a download of "bugle call" // maybe a buffer overrun?
            #      "4" after a download where I set the group wrong
            #      "0" after a previous STA
            return "\x1B&ySSTA A;\x1B&yU\x11"

    def TRA(self):
        return "\x1B&ySTRA;\x1B&yU"

    def UPL(self, group):
        # Always returns 2K of data

        # I think the speech data grows from the end of the buffer backward, and 
        # the index grows from the front forward. Sample data looks like this:
        #   0600  - 3 index of next sample
        #   A701  - 01A7 is the bytes free
        #   BA05  - 05BA is the length of the first sample (bugle)
        #   FF87  - checksum?
        #   4C00  - 004C is the length of the second sample (0)
        #   4582  - checksum?
        #   5200  - 0052 is the length of the third sample
        #   F981  - checksum?
        #   4D00  - 004D is the length of the third sample
        # Blank RAM is
        #   0000 FF07
        # conclusion -- 4 bytes per sample of overhead, plus 4 bytes of global overhead

        return "\x1B&ySUPL %d;\x1B&yU\x11" % group

    def getWords(self):
        return sorted(self.words.keys())

    def loadVocab(self, fn):
        count = 0
        for line in open(fn).readlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts)!=4:
                continue

            count += 1
            group = int(parts[0])
            index = int(parts[1])
            name = parts[2]
            w = word(group, index,  name, parts[3])

            self.words[name] = w
            if group not in self.groups:
                self.groups[group] = []

            self.groups[group].append(word)

        if self.verbosity >= INFO:
            print("Loaded %d vocabularity items from %s" % (count, fn))

    def getSpeechQueueLength(self):
        status = self.status(short=True)
        return int(status)

    def clear(self, group=None):
        command = self.CLE(group)
        self.interface.execute(command)

    def identify(self):
        command = self.ID()
        self.interface.execute(command)
        return self.interface.getResponse()

    def downloadAll(self, printWords=False):
        command = self.CLE(group=None)
        self.interface.execute(command)

        for word in self.words.values():
            if printWords:
                print(word.name, end=' ')
                sys.stdout.flush()
            command = self.DOW(word.group, word.index, "V", word.contents)
            self.interface.execute(command)

        if printWords:
            print()

    def downloadSingle(self, word):
        word = word.upper()
        if word not in self.words:
            raise Exception("Word `%s` not in vocabulary" % word)

        word = self.words[word]

        command = self.DOW(word.group, word.index, "V", word.contents)
        self.interface.execute(command)

    def reset(self):
        command = self.RES()
        self.interface.execute(command)

    def pitch(self, level):
        command = self.PIT(level)
        self.interface.execute(command)

    def speak(self, word):
        word = word.upper()
        if word not in self.words:
            raise Exception("Word `%s` not in vocabulary" % word)

        word = self.words[word]

        command = self.SPE(word.group, word.index)
        self.interface.execute(command)

    def speakAll(self):
        for name in sorted(self.words.keys()):
            word = self.words[name]
            print(word.name)
            command = self.SPE(word.group, word.index)
            self.interface.execute(command)

            while self.getSpeechQueueLength()<9:
                time.sleep(0.01)

    def status(self, short=False):
        command = self.STA(short)
        self.interface.execute(command)
        return self.interface.getResponse()

    def transparent(self):
        command = self.TRA()
        self.interface.execute(command)

    def upload(self, group=None):
        command = self.UPL(group)
        self.interface.execute(command)
        return self.interface.getResponse()

