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
    "=": "EQUAL",
    "!": "BANG",
}


def eprint(*args, **kwargs):
    """
    https://stackoverflow.com/a/14981125/2278742
    """
    print(*args, file=sys.stderr, **kwargs)


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
        for line_number, line in enumerate(file_contents):
            for char in line:
                if not char in token_type_dict:
                    eprint(f"[line {line_number+1}] Error: Unexpected character: {char}")
                    exit_code = 65
            skip_next_char = False
            for idx, char in enumerate(line):
                if skip_next_char:
                    skip_next_char = False
                    continue
                if char in token_type_dict:
                    token = token_type_dict[char]
                    try:
                        if char == "=" and line[idx + 1] == "=":
                            token = "EQUAL_EQUAL"
                            char = "=="
                            skip_next_char = True
                        elif char == "!" and line[idx + 1] == "=":
                            token = "BANG_EQUAL"
                            char = "!="
                            skip_next_char = True
                    except:
                        pass
                    print(f"{token} {char} null")
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
