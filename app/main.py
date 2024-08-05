import re
import sys
from pathlib import Path

import pytest

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
                        print(f"IDENTIFIER {identifier_string} null")
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
                        print(f"DOT . null")
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
                            print(f"IDENTIFIER {identifier_string} null")
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
                print(f"DOT . null")
            in_number_literal = False
        if in_identifier_string:
            print(f"IDENTIFIER {identifier_string} null")
            in_identifier_string = False
            identifier_string = ""
        print("EOF  null")
    else:
        print("EOF  null")

    exit(exit_code)


# expected values:
# exit code, stdout, stderr
test_data = {
    "(()": [
        0,
        "LEFT_PAREN ( null\nLEFT_PAREN ( null\nRIGHT_PAREN ) null\nEOF  null\n",
        "",
    ],
    "{{}}": [
        0,
        "LEFT_BRACE { null\nLEFT_BRACE { null\nRIGHT_BRACE } null\nRIGHT_BRACE } null\nEOF  null\n",
        "",
    ],
    "({*.,+*})": [
        0,
        "LEFT_PAREN ( null\nLEFT_BRACE { null\nSTAR * null\nDOT . null\nCOMMA , null\nPLUS + null\nSTAR * null\nRIGHT_BRACE } null\nRIGHT_PAREN ) null\nEOF  null\n",
        "",
    ],
    ",.$(#": [
        65,
        "COMMA , null\nDOT . null\nLEFT_PAREN ( null\nEOF  null\n",
        "[line 1] Error: Unexpected character: $\n[line 1] Error: Unexpected character: #\n",
    ],
    "={===}": [
        0,
        "EQUAL = null\nLEFT_BRACE { null\nEQUAL_EQUAL == null\nEQUAL = null\nRIGHT_BRACE } null\nEOF  null\n",
        "",
    ],
    "!!===": [0, "BANG ! null\nBANG_EQUAL != null\nEQUAL_EQUAL == null\nEOF  null\n", ""],
    "<<=>>=": [
        0,
        "LESS < null\nLESS_EQUAL <= null\nGREATER > null\nGREATER_EQUAL >= null\nEOF  null\n",
        "",
    ],
    "// Comment": [
        0,
        "EOF  null\n",
        "",
    ],
    "/": [
        0,
        "SLASH / null\nEOF  null\n",
        "",
    ],
    "(\t\n )": [
        0,
        "LEFT_PAREN ( null\nRIGHT_PAREN ) null\nEOF  null\n",
        "",
    ],
    '"foo baz"': [
        0,
        'STRING "foo baz" foo baz\nEOF  null\n',
        "",
    ],
    '"bar': [
        65,
        "EOF  null\n",
        "[line 1] Error: Unterminated string.\n",
    ],
    '"foo <	>bar 123 // hello world!"': [
        0,
        'STRING "foo <	>bar 123 // hello world!" foo <	>bar 123 // hello world!\nEOF  null\n',
        "",
    ],
    '("hello"+"baz") != "other_string"': [
        0,
        'LEFT_PAREN ( null\nSTRING "hello" hello\nPLUS + null\nSTRING "baz" baz\nRIGHT_PAREN ) null\nBANG_EQUAL != null\nSTRING "other_string" other_string\nEOF  null\n',
        "",
    ],
    "1234.1234": [
        0,
        "NUMBER 1234.1234 1234.1234\nEOF  null\n",
        "",
    ],
    "1234.1234.1234.": [
        0,
        "NUMBER 1234.1234 1234.1234\nDOT . null\nNUMBER 1234 1234.0\nDOT . null\nEOF  null\n",
        "",
    ],
    '"Hello" = "Hello" && 42 == 42': [
        65,
        'STRING "Hello" Hello\nEQUAL = null\nSTRING "Hello" Hello\nNUMBER 42 42.0\nEQUAL_EQUAL == null\nNUMBER 42 42.0\nEOF  null\n',
        "[line 1] Error: Unexpected character: &\n[line 1] Error: Unexpected character: &\n",
    ],
    '(5+3) > 7 ; "Success" != "Failure" & 10 >= 5': [
        65,
        'LEFT_PAREN ( null\nNUMBER 5 5.0\nPLUS + null\nNUMBER 3 3.0\nRIGHT_PAREN ) null\nGREATER > null\nNUMBER 7 7.0\nSEMICOLON ; null\nSTRING "Success" Success\nBANG_EQUAL != null\nSTRING "Failure" Failure\nNUMBER 10 10.0\nGREATER_EQUAL >= null\nNUMBER 5 5.0\nEOF  null\n',
        "[line 1] Error: Unexpected character: &\n",
    ],
    "foo bar _hello": [
        0,
        "IDENTIFIER foo null\nIDENTIFIER bar null\nIDENTIFIER _hello null\nEOF  null\n",
        "",
    ],
    '{\n// This is a complex test case\nstr1 = "Test"< >str2 = "Case"\nnum1 = 100\nnum2 = 200.00\nresult = (str1 == "Test" , str2 != "Fail") && (num1 + num2) >= 300 && (a - b) < 10\n}\n': [
        65,
        'LEFT_BRACE { null\nIDENTIFIER str1 null\nEQUAL = null\nSTRING "Test" Test\nLESS < null\nGREATER > null\nIDENTIFIER str2 null\nEQUAL = null\nSTRING "Case" Case\nIDENTIFIER num1 null\nEQUAL = null\nNUMBER 100 100.0\nIDENTIFIER num2 null\nEQUAL = null\nNUMBER 200.00 200.0\nIDENTIFIER result null\nEQUAL = null\nLEFT_PAREN ( null\nIDENTIFIER str1 null\nEQUAL_EQUAL == null\nSTRING "Test" Test\nCOMMA , null\nIDENTIFIER str2 null\nBANG_EQUAL != null\nSTRING "Fail" Fail\nRIGHT_PAREN ) null\nLEFT_PAREN ( null\nIDENTIFIER num1 null\nPLUS + null\nRIGHT_PAREN ) null\nIDENTIFIER num2 null\nGREATER_EQUAL >= null\nNUMBER 300 300.0\nLEFT_PAREN ( null\nIDENTIFIER a null\nMINUS - null\nRIGHT_PAREN ) null\nIDENTIFIER b null\nLESS < null\nNUMBER 10 10.0\nRIGHT_BRACE } null\nEOF  null\n',
        "[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n",
    ],
    "_123_hello world_ 6az f00 foo": [
        0,
        "IDENTIFIER _123_hello null\nIDENTIFIER world_ null\nNUMBER 6 6.0\nIDENTIFIER az null\nIDENTIFIER f00 null\nIDENTIFIER foo null\nEOF  null\n",
        "",
    ],
}


@pytest.mark.parametrize("lox_input", test_data.items())
def test_scanning_parentheses(capsys, lox_input):
    code, expected_values = lox_input
    exit_code = expected_values[0]
    stdout = expected_values[1]
    stderr = expected_values[2]
    test_input_file_path = Path("test.lox")
    with open(test_input_file_path, "w") as f:
        f.write(code)
    sys.argv = [__file__, "tokenize", str(test_input_file_path.absolute())]
    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exit_code == exc_info.value.code

    captured = capsys.readouterr()

    assert stdout == captured.out
    assert stderr == captured.err


if __name__ == "__main__":
    main()
