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
    line_history = []
    expression_history = []
    result_history = []
    variables = {}
    
    while True:
        try:
            line = input(">>> ")
            line_history.append(line)

            for result in line_consumer.consume_line(line, expression_history, result_history, variables, True):
                pass
        except KeyboardInterrupt:
            logging.info('Quit')
            return '\n'.join(line_history)
        except:
            from traceback import print_exc
            print_exc()
    logging.info('Quit')

def main():
    parser = argparse.ArgumentParser(prog=__file__, description=__doc__)

    parser.add_argument('--debug', '-d', nargs='?', type=argparse.FileType('w'), default=None, const=sys.stderr, help='Enables debug logs.')
    parser.add_argument('--interactive', '-i', nargs='?', type=argparse.FileType('r'), default=None, const=True, help='Interactive mode. If filename is also given, start with the contents of the file loaded.')
    parser.add_argument('--output-file', '-o', type=str, default=None, help='Path to output file, or "-" for stdout.')
    # TODO: Add input from file, interactive input? (whenever a line updates, re-evaluate it)
    # Maybe also interactive output file? (whenever input at line changes, output at same line changes)
    # Maybe all of this, but in CLI?

    args = parser.parse_args()
    
    logging.basicConfig(
        stream=args.debug if args.debug is not None else sys.stderr,
        level=logging.DEBUG if args.debug is not None else logging.INFO,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    if not args.interactive:
        res = read_loop()
    else:
        input_text = ""
        if args.interactive is not None:
            input_text = args.interactive.read()
        res = textbook.start(input_text)
    if args.output_file is not None:
        if args.output_file == '-':
            print(res)
        else:
            with open(args.output_file, 'w') as f:
                f.write(res)



if __name__ == "__main__":
    main()
