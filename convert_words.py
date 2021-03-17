words={}

def emit(word, contents):
    if word is None:
        return
    if not contents:
        return
    words[word] = contents

def load_words(fn):
    word = None
    contents = ""
    for line in open(fn).readlines():
        if line.startswith(" "):
            line = line.strip()
            emit(word, contents)
            word = line.strip().split()[-1]
            contents=""
        else:
            contents = contents + line.strip()

def get_id(word):
    return "VOCAB_" + word.replace("-", "_").replace(".","_").replace("!","_").replace("'", "_").upper()

def save_words(fn):
    outf = open(fn, "w")
    for word in sorted(words.keys()):
        contents = words[word]
        outf.write('%s = "%s"\n' % (get_id(word), contents))

    outf.write("\n")

    outf.write("VOCAB={\n")

    lines = []
    for word in sorted(words.keys()):
        lines.append('  "%s": %s' % (word, get_id(word)))

    outf.write(",\n".join(lines) + "\n")
    outf.write("}\n")

def main():
    load_words("vocab-src/27203-16007_Rev-2330.src")
    load_words("vocab-src/27203-16009_Rev-2320.src")
    save_words("vocab.py")

if __name__ == "__main__":
    main()
