import syntax
import syntax_error
import statement
import tokenizer
import base
import tree

import logging
import inspect

DEFAULT_DIRECTIVE = base.assign

def consume_line(line: str, expression_history, result_history, variables: dict, live_print: bool):
    directive_stack = []
    parameters = []
    variables['_'] = result_history[-1] if len(result_history) > 0 else None
    variables['__'] = expression_history[-1] if len(expression_history) > 0 else None
        
    statment = statement.StatmentConstructor()
    token_generator = tokenizer.tokenize(line)
        
    for token in token_generator:
        # If is a directive, add it to the directives we need to complete
        if token.name == 'DIRECTIVE':
            directive_stack.append(syntax.KNOWN_DIRECTIVES[token.value[1:]])
            continue

        # Consume the token
        if token.name == 'EXP_HISTORY':
            # Always returns None, as an expression cannot by itself complete a statement (only a END can)
            exp = statment.consume_exp(expression_history[token.value - 1])
        elif token.name == 'RESULT_HISTORY':
            exp = statment.consume_exp(result_history[token.value - 1])
        else:
            exp = statment.consume_token(token)
        
        if exp is not None:
            if len(directive_stack) > 0:
                directive = directive_stack[-1]
            else:
                directive = DEFAULT_DIRECTIVE
                
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
                continue
            
            # Finished an expression and all the required parameters. We can now attempt to complete one directive
            if len(directive_stack) > 0:
                directive_stack.pop()

            if directive == syntax.KNOWN_DIRECTIVES['set']:
                assert exp.value.name == 'EQUAL' and exp.lhs.value.name == 'NAME', syntax_error.SyntaxError(token.line, token.column, f'Directive "set" requires left-hand-side to be a name, and operator to be equality.')
                variables[exp.lhs.value.value] = exp.rhs
                continue
            
            logging.debug(f'running {directive.__name__} on {exp}')
            try:
                result = directive(exp, *parameters, **variables)
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

            yield base.stringify(result_history[-1])
    assert len(directive_stack) == 0, syntax_error.SyntaxError(token.line, token.column, f'Directive[s]: {", ".join([_.__name__ for _ in directive_stack])} cannot be completed')
