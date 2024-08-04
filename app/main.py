import sys
from pathlib import Path

import pytest

token_type_dict = {
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
}


def main():
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
        for line_number, line in enumerate(file_contents):
            for char in line:
                if not char in token_type_dict:
                    print(f"[line {line_number+1}] Error: Unexpected character: {char}")
            for char in line:
                if char in token_type_dict:
                    print(f"{token_type_dict[char]} {char} null")
        print("EOF  null")
    else:
        print("EOF  null")


test_data = {
    "(()": "LEFT_PAREN ( null\nLEFT_PAREN ( null\nRIGHT_PAREN ) null\nEOF  null\n",
    "{{}}": "LEFT_BRACE { null\nLEFT_BRACE { null\nRIGHT_BRACE } null\nRIGHT_BRACE } null\nEOF  null\n",
    "({*.,+*})": "LEFT_PAREN ( null\nLEFT_BRACE { null\nSTAR * null\nDOT . null\nCOMMA , null\nPLUS + null\nSTAR * null\nRIGHT_BRACE } null\nRIGHT_PAREN ) null\nEOF  null\n",
    ",.$(#": "[line 1] Error: Unexpected character: $\n[line 1] Error: Unexpected character: #\nCOMMA , null\nDOT . null\nLEFT_PAREN ( null\nEOF  null\n",
}


@pytest.mark.parametrize("lox_input", test_data.items())
def test_scanning_parentheses(capsys, lox_input):
    code, tokens = lox_input
    test_input_file_path = Path("test.lox")
    with open(test_input_file_path, "w") as f:
        f.write(code)
    sys.argv = [__file__, "tokenize", str(test_input_file_path.absolute())]
    main()

    captured = capsys.readouterr()
    assert captured.out == tokens


if __name__ == "__main__":
    main()
