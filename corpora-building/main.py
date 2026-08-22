from os.path import exists
from pathlib import Path
import os
from args_parser import parse_arguments
from constants import Action

import questionary


OPEN_TAG = '['
CLOSE_TAG = ']'

def extract_character_dialogue(input_file: Path, character_tag : str) -> str:
    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]



    return "test\n"



def extract_character_tags_from_file(input_file: Path) -> set[str]:

    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]

    character_tag = ""
    character_name = ""

    character_tags : set[str] = set()

    for line in lines:
        tag_opened = False
        tag_closed = False

        character_tag = ""
        character_name = ""


        for char in line:
            if char == OPEN_TAG:
                if not tag_opened:
                    tag_opened = True
                else:
                    raise Exception(f"ERROR. Wrong format. Two open tags found on line: {line}")


            elif char == CLOSE_TAG:

                if tag_opened:
                    tag_closed = True
                else:
                    raise Exception(f"ERROR. Wrong format. Close tag with no open tag on line: {line}")


            else:
                if tag_opened and not tag_closed:
                    character_name += char

                elif tag_opened and tag_closed:
                    character_tag = OPEN_TAG + character_name + CLOSE_TAG
                    character_tags.add(character_tag)
                    break

        if tag_opened and not tag_closed:
            raise Exception(f"ERROR. Wrong format. The open tag was never closed: {line}")




    return character_tags




def find_all_character_tags(files_to_process: list[Path]) -> set[str]:

    all_character_tags = set()

    for file in files_to_process:
        # Intersect the newly found tags with other tags 
        all_character_tags |= extract_character_tags_from_file(file)

    return all_character_tags






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

def tag_to_name(tag: str) -> str:
    name = tag.lstrip(OPEN_TAG).rstrip(CLOSE_TAG).lower()
    return name[:1].upper() + name[1:]


def main():
    # Parse the CLI arguments 
    args = parse_arguments()


    files_to_process = identify_files_to_process(args.input_file, args.source_dir)

    all_character_tags : set[str] = find_all_character_tags(files_to_process)
    print(all_character_tags)

    # prompt the user to pick the character from names
    character_tag_choice = questionary.select(
            "Which character that you would like to work with?",
            choices=[ questionary.Choice(f"{tag_to_name(tag)}", value=tag) for tag in all_character_tags]
    ).ask()

    # promt the user to pick the action
    action_choice = questionary.select(
            "Pick the action that you would like to perform",
            choices=[
                questionary.Choice(
                    f"Extract all dialogue produced by {tag_to_name(character_tag_choice)}",
                    value=Action.EXTRACT_CHARACTER
                ),
                questionary.Choice(
                    f"Extract all dialogue produced by everyone other than {tag_to_name(character_tag_choice)}",
                    value=Action.EXTRACT_OTHERS
                ),
            ]
    ).ask()

    if action_choice == Action.EXTRACT_CHARACTER:

        all_dialogue_by_chosen_character = ""

        for file in files_to_process:
            all_dialogue_by_chosen_character += extract_character_dialogue(file, character_tag_choice)

        with open(args.output_file, "w") as f:
            f.write(all_dialogue_by_chosen_character)


        

    elif action_choice == Action.EXTRACT_OTHERS:
        ...




if __name__ == "__main__":
    main()







