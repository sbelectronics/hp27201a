# Vocabulary builder
# Scott Baker, http://www.smbaker.com/

# Given a list of words at stdin, lookup those words in
# vocab.py and generate a list of vocabulary on stdout.

from __future__ import print_function
from vocab import VOCAB
import sys

# Assumption
#   global overhead
#     2 bytes - highest phrase #
#     2 bytes - memory remaining
#   per-phrase overhead
#     2 bytes - length
#     2 bytes - checksum
GROUP_OVERHEAD = 4
WORD_OVERHEAD = 4

# each RAM is 2K
MAX_GROUP_SIZE = 2048 - GROUP_OVERHEAD

# number of RAMs
MAX_GROUPS = 6

groupFree = []
groupIndices = []

def alloc_group(l):
    global groupFree
    global groupIndices

    for i in range(0, MAX_GROUPS):
        if groupFree[i] >= l:
            groupFree[i] -= l
            index = groupIndices[i]
            groupIndices[i] += 1
            return (i, index)

    return (None, None)

def main():
    global groups

    vocab = []

    for i in range(0, MAX_GROUPS):
        groupFree.append(MAX_GROUP_SIZE)
        groupIndices.append(1)

    for line in sys.stdin.readlines():
        line = line.strip()
        if not line:
            continue
        
        word = line.upper()
        if word not in VOCAB:
            print("Unknown word: %s" % word, file=sys.stderr, )
            sys.exit(-1)

        contents = VOCAB[word]

        if (len(contents) %2 ) != 0:
            print("length is not a multiple of 2 on word %s" % word)
            sys.exit(-1)

        l = len(contents)/2

        (group, index) = alloc_group(l+WORD_OVERHEAD)
        if group is None:
            print("out of space on word %s" % word, file=sys.stderr)
            sys.exit(-1)

        vocab.append( [group, index, word, contents] )

    for item in sorted(vocab):
        print("%d %d %s %s" % (item[0]+1, item[1], item[2], item[3]))

if __name__ == "__main__":
    main()

