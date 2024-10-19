import line_consumer
import textbook

import argparse

import logging
import sys

__doc__ = \
"""\
Use this parser to calculate expressions including magnitudes, complex numbers, and parameters.

Howto:
- Choose a directive 
    - eval: evaluate an expression (without knowing argument values)
    - assign: (DEFAULT) assign all known variables and evaluate
    - derive: derive expression with respect to argument
    - solve: find roots of expression with all known variables
- Write expressions
- Access previously typed expressions with $<expression number> and results with $$<result number>
"""


def read_loop():
    print(__doc__)
    # Default directive
    expression_history = []
    result_history = []
    variables = {}
    
    while True:
        try:
            line = input(">>> ")

            for result in line_consumer.consume_line(line, expression_history, result_history, variables, True):
                pass
        except KeyboardInterrupt:
            logging.info('Quit')
            raise
        except:
            from traceback import print_exc
            print_exc()
    logging.info('Quit')

def main():
    parser = argparse.ArgumentParser(prog=__file__, description=__doc__)

    parser.add_argument('--debug', '-d', action=argparse.BooleanOptionalAction)
    parser.add_argument('--interactive', '-i', action=argparse.BooleanOptionalAction)
    # TODO: Add input from file, interactive input? (whenever a line updates, re-evaluate it)
    # Maybe also interactive output file? (whenever input at line changes, output at same line changes)
    # Maybe all of this, but in CLI?

    args = parser.parse_args()
    
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    if not args.interactive:
        read_loop()
    else:
        textbook.start()


if __name__ == "__main__":
    main()
