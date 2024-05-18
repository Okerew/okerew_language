import re
import sys
TOKEN_TYPES = [
    ('KEYWORD', r'(input|print|exec|func|for|while|if|else|exit|elif|leave)'),
    ('OPERATOR', r'(\+|\-|\*|\/|\%|\*\*|\/\/|\&|\||\^|<<|>>|==|!=|>|<|>=|<=)'),
    ('ASSIGNMENT', r'='),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER', r'\d+(\.\d*)?'),
    ('STRING', r'\'[^\']*\''),
    ('NEWLINE', r'\n'),
    ('WHITESPACE', r'\s+'),
    ('COMMENT', r'\?.*'),
]

PATTERN = '|'.join(f'(?P<{type}>{pattern})' for type, pattern in TOKEN_TYPES)

def lexer(code):
    tokens = []
    for match in re.finditer(PATTERN, code):
        for name, value in match.groupdict().items():
            if value is not None:
                if name != 'COMMENT':
                    tokens.append((name, value))
                break
    return tokens

def load_code_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


class OkerewInterpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}

    def interpret(self, tokens):
        current_token = None
        token_index = 0
        while token_index < len(tokens):
            current_token = tokens[token_index]

            if current_token[0] == 'WHITESPACE' or current_token[0] == 'NEWLINE':
                token_index += 1
                continue

            if current_token[0] == 'KEYWORD' and current_token[1] == 'input':
                variable_name = self.get_next_token_value(tokens, token_index + 1)
                user_input = input(f"Enter value for {variable_name[1]}: ")
                try:
                    self.variables[variable_name[1]] = int(user_input)
                except ValueError:
                    self.variables[variable_name[1]] = user_input
                token_index += 2

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'print':
                next_token = self.get_next_token_value(tokens, token_index + 1)
                if next_token and next_token[0] == 'STRING':
                    print(next_token[1][1:-1])
                else:
                    expression_value = self.evaluate_expression(tokens, token_index + 1)
                    print(expression_value)
                token_index += 2

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'exit':
                break

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'else':
                def execute_else_block():
                    print("Executing else block")

                execute_else_block()
                token_index = self.find_matching_keyword(tokens, token_index, 'if', 'else')

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'for':
                def execute_for_block():
                    for i in range(1, 6):
                        print("Current number:", i)

                execute_for_block()
                token_index = self.find_matching_keyword(tokens, token_index, 'for', 'else')

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'while':
                condition = self.get_next_token_value(tokens, token_index + 1)
                if condition:
                    condition_value = self.evaluate_expression(tokens, token_index + 1)
                    while condition_value:
                        pass
                        condition_value = self.evaluate_expression(tokens, token_index + 1)
                    token_index = self.find_matching_keyword(tokens, token_index, 'while', 'else')

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'if':
                condition = self.get_next_token_value(tokens, token_index + 1)
                if condition:
                    condition_value = self.evaluate_expression(tokens, token_index + 1)
                    if condition_value:
                        pass
                    else:
                        token_index = self.find_matching_keyword(tokens, token_index, 'elif', 'else')

            elif current_token[0] == 'KEYWORD' and current_token[1] == 'func':
                token_index = self.define_function(tokens, token_index)

            elif current_token[0] == 'IDENTIFIER':
                variable_name = current_token[1]
                if self.get_next_token_value(tokens, token_index + 1) == '=':
                    expression_value = self.evaluate_expression(tokens, token_index + 2)
                    self.variables[variable_name] = expression_value
                    token_index += 3
                elif variable_name in self.functions:
                    function_body = self.functions[variable_name]
                    self.interpret(function_body)

            token_index += 1

    def define_function(self, tokens, start_index):
        index = start_index + 1
        # Skip any whitespace after the 'func' keyword
        while index < len(tokens) and tokens[index][0] == 'WHITESPACE':
            index += 1

        if index < len(tokens) and tokens[index][0] == 'IDENTIFIER':
            function_name = tokens[index][1]
            index += 1

            while index < len(tokens) and tokens[index][0] == 'WHITESPACE':
                index += 1

            function_body = []
            while index < len(tokens):
                if tokens[index][0] == 'KEYWORD' and tokens[index][1] == ('leave'):
                    index += 1
                    break
                function_body.append(tokens[index])
                index += 1

            self.functions[function_name] = function_body
            return index
        else:
            raise SyntaxError("Function name must be an identifier")


    def find_matching_keyword(self, tokens, start_index, keyword1, keyword2):
        count = 0
        for index in range(start_index, len(tokens)):
            current_token = tokens[index]
            if current_token[0] == 'KEYWORD' and current_token[1] == keyword1:
                count += 1
            elif current_token[0] == 'KEYWORD' and current_token[1] == keyword2:
                if count == 0:
                    return index
                else:
                    count -= 1

        return len(tokens) - 1

    def expect_and_skip(self, tokens, index, expected_type, expected_value):
        if index < len(tokens):
            next_token = tokens[index]
            if next_token[0] == expected_type and next_token[1] == expected_value:
                return index + 1
        raise SyntaxError(f"Expected '{expected_value}' but found {next_token[1]} at index {index}")

    def evaluate_expression(self, tokens, start_index):
        expression_tokens = tokens[start_index:]
        expression = ''
        for token in expression_tokens:
            if token[0] in ('NUMBER', 'IDENTIFIER', 'OPERATOR', 'STRING'):
                expression += token[1]
            elif token[0] == 'NEWLINE':
                break

        if not expression:
            return None

        try:
            result = eval(expression, {}, self.variables)
            return result
        except Exception as e:
            print(f"Error evaluating expression: {e}")
            return None
        
    def get_next_token_value(self, tokens, index):
        if index < len(tokens):
            return tokens[index]
        else:
            return None


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python interpreter.py <file.okerew>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not file_path.endswith('.okerew'):
        print("Error: The file must have a .okerew extension.")
        sys.exit(1)

    code = load_code_from_file(file_path)
    tokens = lexer(code)

    interpreter = OkerewInterpreter()
    interpreter.interpret(tokens)
