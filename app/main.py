import sys
from pathlib import Path

token_type_dict = {"(": "LEFT_PAREN", ")": "RIGHT_PAREN"}


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
        file_contents = file.read()

    if file_contents:
        for char in file_contents:
            if char in token_type_dict:
                print(f"{token_type_dict[char]} {char} null")
        print("EOF  null")
    else:
        print("EOF  null")


def test_main(capsys):
    test_input_file_path = Path("test.txt")
    with open(test_input_file_path, "w") as f:
        f.write("(()")
    sys.argv = [__file__, "tokenize", str(test_input_file_path.absolute())]
    main()

    captured = capsys.readouterr()
    assert (
        captured.out == "LEFT_PAREN null\nLEFT_PAREN null\nRIGHT_PAREN null\nEOF  null\n"
    )


if __name__ == "__main__":
    main()
