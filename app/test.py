import sys
from pathlib import Path

import pytest
from main import main

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
        'LEFT_BRACE { null\nIDENTIFIER str1 null\nEQUAL = null\nSTRING "Test" Test\nLESS < null\nGREATER > null\nIDENTIFIER str2 null\nEQUAL = null\nSTRING "Case" Case\nIDENTIFIER num1 null\nEQUAL = null\nNUMBER 100 100.0\nIDENTIFIER num2 null\nEQUAL = null\nNUMBER 200.00 200.0\nIDENTIFIER result null\nEQUAL = null\nLEFT_PAREN ( null\nIDENTIFIER str1 null\nEQUAL_EQUAL == null\nSTRING "Test" Test\nCOMMA , null\nIDENTIFIER str2 null\nBANG_EQUAL != null\nSTRING "Fail" Fail\nRIGHT_PAREN ) null\nLEFT_PAREN ( null\nIDENTIFIER num1 null\nPLUS + null\nIDENTIFIER num2 null\nRIGHT_PAREN ) null\nGREATER_EQUAL >= null\nNUMBER 300 300.0\nLEFT_PAREN ( null\nIDENTIFIER a null\nMINUS - null\nIDENTIFIER b null\nRIGHT_PAREN ) null\nLESS < null\nNUMBER 10 10.0\nRIGHT_BRACE } null\nEOF  null\n',
        "[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n[line 6] Error: Unexpected character: &\n",
    ],
    "_123_hello world_ 6az f00 foo": [
        0,
        "IDENTIFIER _123_hello null\nIDENTIFIER world_ null\nNUMBER 6 6.0\nIDENTIFIER az null\nIDENTIFIER f00 null\nIDENTIFIER foo null\nEOF  null\n",
        "",
    ],
    "and": [
        0,
        "AND and null\nEOF  null\n",
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
