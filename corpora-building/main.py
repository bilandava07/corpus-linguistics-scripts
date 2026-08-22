from os.path import exists
from pathlib import Path
import os
from args_parser import parse_arguments

def extract_character_tags_from_file(input_file: Path) -> set[str]:

    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]

    character_tag = ""
    character_name = ""

    open_tag = '['
    close_tag = ']'

    character_tags : set[str] = set()

    for line in lines:
        tag_opened = False
        tag_closed = False

        character_tag = ""
        character_name = ""


        for char in line:
            if char == open_tag:
                tag_opened = True

            elif char == close_tag:
                tag_closed = True

            else:
                if tag_opened and not tag_closed:
                    character_name += char

                elif tag_opened and tag_closed:
                    character_tag = open_tag + character_name + close_tag
                    character_tags.add(character_tag)
                    break

    return character_tags




def find_all_character_tags(files_to_process: list[Path]) -> set[str]:

    all_character_tags = set()

    for file in files_to_process:
        # Intersect the newly found tags with other tags 
        all_character_tags |= extract_character_tags_from_file(file)

    return all_character_tags





def extract_character_lines(input_file: Path, output_file: Path, char_marker: str):
    # Read in the file
    # Look for char_marker e.g. [GORDON]:

  pass

def identify_files_to_process(input_file: str | None, source_dir : str | None) -> list[Path]:
    files_to_process : list[Path] = []

    if input_file:
        # path to a single input file specified 

        input_file_path : Path = Path(input_file)

        # check if the file exists
        if not input_file_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {input_file_path}")


        # only process .txt files
        if input_file_path.suffix == ".txt":
            files_to_process.append(input_file_path)
        else:
            print(f"{input_file_path} is NOT a .txt file! Skippping...")


    elif source_dir:
        # path to a source directory with input files specified

        source_dir : Path = Path(source_dir)

        # Iterate through path objects inside the directory
        for input_path in source_dir.iterdir():

            # only process files not dir
            if not input_path.is_file():
                print(f"{input_path} is a directory! Skippping...")
                continue

            # only process .txt files
            if input_path.suffix != ".txt":
                print(f"{input_path} is NOT a .txt file! Skippping...")
                continue

            files_to_process.append(input_path)

    return files_to_process



def main():
    # Parse the CLI arguments 
    args = parse_arguments()

    files_to_process = identify_files_to_process(args.input_file, args.source_dir)

    all_character_tags : set[str] = find_all_character_tags(files_to_process)

    print(all_character_tags)






if __name__ == "__main__":
    main()










        







  


    



