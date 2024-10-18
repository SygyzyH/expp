import syntax
import statement
import tokenizer
import base
import tree

def consume_line(line: str, expression_history, result_history):
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
            # Always returns None, as an expression cannot by itself complete a statement (only a END can)
            exp = statment.consume_exp(expression_history[first_token.value - 1])
        elif first_token.name == 'RESULT_HISTORY':
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
                return base.stringify(result_history[-1])
