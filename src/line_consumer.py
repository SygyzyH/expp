import syntax
import syntax_error
import statement
import tokenizer
import base
import tree

import logging
import inspect

def consume_line(line: str, expression_history, result_history, live_print: bool):
    directive = syntax.KNOWN_DIRECTIVES['assign']
    assigments = {'_': result_history[-1] if len(result_history) > 0 else None}
    parameters = []
        
    statment = statement.StatmentConstructor()
    token_generator = tokenizer.tokenize(line)
        
    first_token = next(token_generator)
        
    exp = None
    if first_token.name == 'DIRECTIVE':
        directive = syntax.KNOWN_DIRECTIVES[first_token.value[1:]]
    else:
        # NOTE: The first token is not thrown away, it stays in the statement class state.
        # The only way we complete an expression here is if the tokenizer returne 'END' as the first token,
        # which can only happen if the statement is empty. In which case, we quit
        # FIXME: Bad code repetition
        if first_token.name == 'EXP_HISTORY':
            assert first_token.value > 0, syntax_error.SyntaxError(first_token.line, first_token.column, f'History is index 1 based. 0 is not valid')
            assert first_token.value - 1 < len(expression_history), syntax_error.SyntaxError(first_token.line, first_token.column, f'Invalid result history idx {first_token.value}, max is {len(expression_history)}')
            # Always returns None, as an expression cannot by itself complete a statement (only a END can)
            exp = statment.consume_exp(expression_history[first_token.value - 1])
        elif first_token.name == 'RESULT_HISTORY':
            assert first_token.value > 0, syntax_error.SyntaxError(first_token.line, first_token.column, f'History is index 1 based. 0 is not valid')
            assert first_token.value - 1 < len(result_history), syntax_error.SyntaxError(first_token.line, first_token.column, f'Invalid result history idx {first_token.value}, max is {len(result_history)}')
            exp = statment.consume_exp(result_history[first_token.value - 1])
        else:
            exp = statment.consume_token(first_token)
        if exp is not None:
            return
        
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
            if live_print:
                print(f"{len(expression_history)}: {base.stringify(exp)}")
            # Number of parameters directive has, that are positional and have no default, excluding the input expression.
            required_parameters = len(list(
                filter(
                    lambda param: param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and param.default == inspect.Parameter.empty,
                    inspect.signature(directive).parameters.values()
                )
            )) - 1
            if len(parameters) < required_parameters and exp.value.name == 'NAME' and exp.value.value != '_':
                parameters.append(exp.value.value)
            elif exp.value.name == 'EQUAL' and exp.lhs.value.name == 'NAME':
                assigments[exp.lhs.value.value] = exp.rhs
            else:
                logging.debug(f'running {directive.__name__} on {exp}')
                try:
                    result = directive(exp, *parameters, **assigments)
                except Exception as e:
                    raise syntax_error.SyntaxError(token.line, token.column, f'Directive "{directive.__name__}" failed: {e.__class__.__name__}: {str(e)}')
                if isinstance(result, tree.BiTree):
                    result_history.append(result)
                else:
                    new_node = syntax.default_token('NUMBER')
                    new_node.value = result
                    result_history.append(tree.BiTree(None, None, new_node))
                if live_print:
                    print(f"result {len(result_history)}: {base.stringify(result_history[-1])}")
                return base.stringify(result_history[-1])
    raise syntax_error.SyntaxError(0, 0, 'Failed to construct enough expressions to perform directive')
