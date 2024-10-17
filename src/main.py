import syntax
import statement
import tokenizer
import base
import tree

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
    # Default directive
    directive = syntax.KNOWN_DIRECTIVES['eval']
    expression_history = []
    last_result = None
    
    while True:
        try:
            line = input(">>> ")

            assigments = {'_': last_result}
            parameters = []
        
            statment = statement.StatmentConstructor()
            token_generator = tokenizer.tokenize(line)
        
            try:
                first_token = next(token_generator)
            except StopIteration:
                continue
        
            exp = None
            if first_token.name == 'DIRECTIVE':
                directive = syntax.KNOWN_DIRECTIVES[first_token.value[1:]]
            else:
                # NOTE: The first token is not thrown away, it stays in the statement class state.
                # The only way we complete an expression here is if the tokenizer returne 'END' as the first token,
                # which can only happen if the statement is empty. In which case, we quit
                exp = statment.consume_token(first_token)
                if exp is not None:
                    break
        
            for token in token_generator:
                if token.name == 'HISTORY':
                    # Always returns None, as an expression cannot by itself complete a statement (only a END can)
                    exp = statment.consume_exp(expression_history[token.value - 1])
                else:
                    exp = statment.consume_token(token)
                if exp is not None:
                    expression_history.append(exp)
                    print(f"{len(expression_history)}: {base.stringify(exp)}")
                    if exp.value.name == 'NAME' and exp.value.value != '_':
                        parameters.append(exp.value.value)
                        print(f"param {len(parameters)}: {base.stringify(exp)}")
                    elif exp.value.name == 'EQUAL' and exp.lhs.value.name == 'NAME':
                        assigments[exp.lhs.value.value] = base.assign(exp.rhs, **assigments)
                        print(f"assign {len(assigments) - 1}: {base.stringify(exp)}")
                    else:
                        result = directive(exp, *parameters, **assigments)
                        print("result: ", end='')
                        if isinstance(result, tree.BiTree):
                            print(base.stringify(result))
                        else:
                            print(result)
                        last_result = result
                        # Default directive after first succesfull command
                        directive = syntax.KNOWN_DIRECTIVES['assign']
            
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
    # TODO: Add input from file, interactive input from file? (whenever a line updates, re-evaluate it)
    # Maybe also interactive output file? (whenever input at line changes, output at same line changes)
    # Maybe all of this, but in CLI?

    args = parser.parse_args()
    
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(levelname)s:%(funcName)s:%(lineno)s] %(message)s"
    )

    read_loop()


if __name__ == "__main__":
    main()
