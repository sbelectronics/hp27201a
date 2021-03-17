# HP27201A speech output module, command line interface
# Scott Baker, http://www.smbaker.com/
#
# Supports the following commands
#    clear <bank> - clear the speech memory
#    download <word> - download a single word from vocabulary to speech moodule
#    id - print identity string
#    pitch [H|M|L] - set pitch to high, medium, or low
#    reset - reset the module
#    status [S] - query status. Use "S" for short status, or leave blank for full status
#    speak <word> - speak a word
#    speakall - speak all words in vocabulary
#    list - list all words in vocabulary
#    transparent - switch to transparent mode (bypass the speech module)
#    upload - upload words from the speech module's memory to the host computer
#
# This program expects a speech vocabulary to be stored in the file named by the
# --vocab argument (defaults to test.vocab). The module only has about 12K of RAM
# so you must choose the words you want to put in the module.

from __future__ import print_function
import argparse
import sys
import time

from globals import ERROR, WARNING, INFO, DEBUG
from hp27201a import hp27201a
from interface import ScreenInterface, SerialInterface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--afterstatus', '-a', default=False, action='store_true')
    parser.add_argument('--watchstatus', '-w', default=False, action='store_true')
    parser.add_argument('--closedcaption', '-c', default=False, action='store_true', help='print words as we queue them')
    parser.add_argument("--baud", type=int, default=9600, help="baud rate to use on serial device")
    parser.add_argument("--serial", type=str, default=None, help="send output to serial device")
    parser.add_argument("--vocab", type=str, default="test.vocab", help="vocabulary file name")
    parser.add_argument('--verbose', '-v', action='count', default=INFO)
    parser.add_argument('--maxq', '-m', type=int, default=None, help="maximum items to have in speech queue before speaking")
    parser.add_argument("command", help="command to execute")
    parser.add_argument("args", nargs="*", help="arguments to command")
    args = parser.parse_args(sys.argv[1:])

    if args.serial:
        interface = SerialInterface(port=args.serial, baud=args.baud, verbosity=args.verbose)
    else:
        interface = ScreenInterface()

    speech = hp27201a(args.vocab, interface, verbosity=args.verbose)

    if args.command == "clear":
        if args.args:
            for arg in args.args:
                speech.clear(int(arg))
        else:
            speech.clear()
    elif args.command == "download":
        for arg in args.args:
            speech.downloadSingle(arg)
    elif args.command == "id":
        print(speech.identify())
    elif args.command == "init":
        speech.downloadAll(printWords=args.closedcaption)
    elif args.command == "pitch":
        if len(args.args) !=1 :
            print("Incorrect argument to pitch", file=sys.stderr)
            sys.exit(-1)
        speech.pitch(args.args[0])
    elif args.command == "reset":
        speech.reset()
    elif args.command == "status":
        argu = [x.upper() for x in args.args]
        if ("SHORT" in argu) or ("S" in argu):
            print(speech.status(short=True))
        else:
            print(speech.status(short=False))
    elif args.command == "speak":
        for word in args.args:
            if args.maxq is not None:
                while ((9-speech.getSpeechQueueLength()) > args.maxq):
                    time.sleep(0.01)
            if args.closedcaption:
                print(word, end=' ')
                sys.stdout.flush()
            speech.speak(word)
        if args.closedcaption:
            print()
    elif args.command == "speakall":
        speech.speakAll()
    elif args.command == "list":
        for word in speech.getWords():
            print(word)
    elif args.command == "transparent":
        speech.transparent()
    elif args.command == "upload":
        if len(args.args) !=1 :
            print("Incorrect argument to pitch", file=sys.stderr)
            sys.exit(-1)        
        print(speech.upload(int(args.args[0])))
    else:
        print("unknown command %s" % args.command, file=sys.stderr)

    if args.afterstatus:
        print(speech.status(short=False))

    if args.watchstatus:
        lastStatus = ""
        while True:
            status = speech.status()
            if status!=lastStatus:
                print(status)
                lastStatus = status
    
if __name__ == "__main__":
    main()
