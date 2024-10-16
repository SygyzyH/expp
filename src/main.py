import tokenizer
import base

import argparse

import logging
import sys

__doc__ = \
"""\
Use this parser to calculate expressions including magnitudes, complex numbers, and parameters.

Howto:
TODO
"""


def read_loop():
    print(__doc__)
    iters = 3
    while iters > 0:
        iters -= 1
        line = input(">>> ")
        
        statment = base.StatmentConstructor()
        for token in tokenizer.tokenize(line):
            exp = statment.consume_token(token)
            if exp is not None:
                print(exp)

def main():
    parser = argparse.ArgumentParser(prog=__file__, description=__doc__)

    parser.add_argument('--debug', '-d', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    read_loop()


if __name__ == "__main__":
    main()
