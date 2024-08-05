import re
import sys


one_char_token_type_dict = {
    "(": "LEFT_PAREN",
    ")": "RIGHT_PAREN",
    "{": "LEFT_BRACE",
    "}": "RIGHT_BRACE",
    ",": "COMMA",
    ".": "DOT",
    "-": "MINUS",
    "+": "PLUS",
    ";": "SEMICOLON",
    "*": "STAR",
    "=": "EQUAL",
    "!": "BANG",
    "<": "LESS",
    ">": "GREATER",
    "/": "SLASH",
}

two_char_token_type_dict = {
    "==": "EQUAL_EQUAL",
    "!=": "BANG_EQUAL",
    "<=": "LESS_EQUAL",
    ">=": "GREATER_EQUAL",
}

reserved_words = [
    "and",
    "class",
    "else",
    "false",
    "for",
    "fun",
    "if",
    "nil",
    "or",
    "print",
    "return",
    "super",
    "this",
    "true",
    "var",
    "while",
]


def eprint(*args, **kwargs):
    """
    https://stackoverflow.com/a/14981125/2278742
    """
    print(*args, file=sys.stderr, **kwargs)


def format_number_literal(number_literal: str) -> str:
    return str(float(number_literal))


def add_token(line, idx, in_string_literal, skip_next_n_chars) -> tuple[int, int]:
    char = line[idx]
    token = one_char_token_type_dict[char]
    try:
        # wrap in try except so we don't have to check if we're out of bounds of the string
        potential_two_char_token = char + line[idx + 1]
        if potential_two_char_token in two_char_token_type_dict.keys():
            char = potential_two_char_token
            token = two_char_token_type_dict[potential_two_char_token]
            skip_next_n_chars = 1
        elif potential_two_char_token == "//":
            if not in_string_literal:
                # // doesn't start a comment if it's part of a string literal
                return 1, skip_next_n_chars
    except:
        pass
    print(f"{token} {char} null")
    return 0, skip_next_n_chars


def add_identifier(identifier: str) -> None:
    if identifier in reserved_words:
        print(f"{identifier.upper()} {identifier} null")
    else:
        print(f"IDENTIFIER {identifier} null")


def main():
    exit_code = 0

    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command != "tokenize":
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)

    with open(filename) as file:
        file_contents = file.readlines()

    if file_contents:
        in_string_literal = False
        in_number_literal = False
        in_identifier_string = False
        period_in_number_literal = False
        string_literal = ""
        number_literal = ""
        identifier_string = ""
        for line_number, line in enumerate(file_contents):
            skip_next_n_chars = 0
            for idx, char in enumerate(line):
                if skip_next_n_chars:
                    skip_next_n_chars -= 1
                    continue

                # char is not (part of) a token
                if char in one_char_token_type_dict.keys():
                    if in_identifier_string:
                        add_identifier(identifier_string)
                        in_identifier_string = False
                        identifier_string = ""

                if (
                    char in one_char_token_type_dict
                    and not in_string_literal
                    and not in_number_literal
                ):
                    comment, skip_next_n_chars = add_token(
                        line, idx, in_string_literal, skip_next_n_chars
                    )
                    if comment:
                        break
                else:
                    if char == '"':
                        if in_string_literal:
                            print(f'STRING "{string_literal}" {string_literal}')
                            string_literal = ""
                        in_string_literal = not in_string_literal
                    elif in_string_literal:
                        string_literal += char
                    elif char in "0123456789" and not in_identifier_string:
                        in_number_literal = True
                        number_literal += char
                    elif in_number_literal and char == "." and period_in_number_literal == False:
                        in_number_literal = True
                        period_in_number_literal = True
                        number_literal += char
                    elif in_number_literal and char == "." and period_in_number_literal == True:
                        print(f"NUMBER {number_literal} {number_literal}")
                        print("DOT . null")
                        in_number_literal = False
                        period_in_number_literal = False
                        number_literal = ""
                    elif in_number_literal and char not in "0123456789.":
                        print(f"NUMBER {number_literal} {format_number_literal(number_literal)}")
                        in_number_literal = False
                        period_in_number_literal = False
                        number_literal = ""

                        # handle the char following the number
                        if (
                            char in one_char_token_type_dict
                            and not in_string_literal
                            and not in_number_literal
                        ):
                            add_token(line, idx, in_string_literal, 0)

                    if char.isspace():
                        if in_identifier_string:
                            add_identifier(identifier_string)
                            in_identifier_string = False
                            identifier_string = ""
                        # skip over it
                        pass
                    elif (
                        not in_number_literal
                        and not in_string_literal
                        and char not in one_char_token_type_dict.keys()
                        and char != '"'
                    ):
                        # https://craftinginterpreters.com/scanning.html#regular-languages-and-expressions
                        if not in_identifier_string and re.match(r"[a-zA-Z_]", char):
                            in_identifier_string = True
                            identifier_string += char
                        elif in_identifier_string and re.match(r"[a-zA-Z_0-9]", char):
                            identifier_string += char
                        else:
                            eprint(f"[line {line_number+1}] Error: Unexpected character: {char}")
                            exit_code = 65
        if in_string_literal:
            eprint(f"[line {line_number+1}] Error: Unterminated string.")
            exit_code = 65
        if in_number_literal:
            # number literal that's not followed by another character before the EOF
            add_dot = False
            if number_literal[-1] == ".":
                number_literal_a = number_literal[0:-1]
                add_dot = True
            else:
                number_literal_a = number_literal
            print(f"NUMBER {number_literal_a} {format_number_literal(number_literal)}")
            if add_dot:
                print("DOT . null")
            in_number_literal = False
        if in_identifier_string:
            add_identifier(identifier_string)
            in_identifier_string = False
            identifier_string = ""
        print("EOF  null")
    else:
        print("EOF  null")

    exit(exit_code)


if __name__ == "__main__":
    main()
