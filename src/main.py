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
    
    while True:
        try:
            line = input(">>> ")

            directive = syntax.KNOWN_DIRECTIVES['assign']
            assigments = {'_': result_history[-1] if len(result_history) > 0 else None}
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
                # FIXME: Bad code repetition
                if first_token.name == 'EXP_HISTORY':
                    # Always returns None, as an expression cannot by itself complete a statement (only a END can)
                    exp = statment.consume_exp(expression_history[first_token.value - 1])
                elif first_token.name == 'RESULT_HISTORY':
                    exp = statment.consume_exp(result_history[first_token.value - 1])
                else:
                    exp = statment.consume_token(first_token)
                if exp is not None:
                    break
        
            for token in token_generator:
                if token.name == 'EXP_HISTORY':
                    # Always returns None, as an expression cannot by itself complete a statement (only a END can)
                    exp = statment.consume_exp(expression_history[token.value - 1])
                elif token.name == 'RESULT_HISTORY':
                    exp = statment.consume_exp(result_history[token.value - 1])
                else:
                    exp = statment.consume_token(token)
                if exp is not None:
                    expression_history.append(exp)
                    print(f"{len(expression_history)}: {base.stringify(exp)}")
                    if exp.value.name == 'NAME' and exp.value.value != '_':
                        parameters.append(exp.value.value)
                        print(f"param {len(parameters)}: {base.stringify(exp)}")
                    elif exp.value.name == 'EQUAL' and exp.lhs.value.name == 'NAME':
                        assigments[exp.lhs.value.value] = exp.rhs
                        print(f"assign {len(assigments) - 1}: {base.stringify(exp)}")
                    else:
                        result = directive(exp, *parameters, **assigments)
                        if isinstance(result, tree.BiTree):
                            result_history.append(result)
                        else:
                            new_node = syntax.default_token('NUMBER')
                            new_node.value = result
                            result_history.append(tree.BiTree(None, None, new_node))
                        print(f"result {len(result_history)}: {base.stringify(result_history[-1])}")
            
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
