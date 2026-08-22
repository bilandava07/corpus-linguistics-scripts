from os.path import exists
from pathlib import Path
import os
from args_parser import parse_arguments
from constants import Action

import questionary


OPEN_TAG = '['
CLOSE_TAG = ']'
SEPARATOR = ':'

def find_character_tag(input_line: str) -> str | None:
    ''' Finds and returns a valid character tag in the string '''

    tag_opened = False
    tag_closed = False

    character_tag = ""
    character_name = ""

    for char in input_line:
        if char == OPEN_TAG:
            if not tag_opened:
                tag_opened = True
            else:
                raise Exception(f"ERROR. Wrong format. Two open tags found on line: {input_line}")


        elif char == CLOSE_TAG:

            if tag_opened:
                tag_closed = True
            else:
                raise Exception(f"ERROR. Wrong format. Close tag with no open tag on line: {input_line}")


        else:
            if tag_opened and not tag_closed:
                character_name += char

            elif tag_opened and tag_closed:
                character_tag = OPEN_TAG + character_name + CLOSE_TAG + SEPARATOR
                return character_tag

    if tag_opened and not tag_closed:
        raise Exception(f"ERROR. Wrong format. The open tag was never closed: {input_line}")

    return None





def extract_character_dialogue(input_file: Path, target_character_tag : str, preserve_tags : bool) -> str:
    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]

    all_dialogue_by_target_character = ""

    recording_a_characters_utterance = False

    for line in lines:
        if recording_a_characters_utterance:
            # stop recording if encountered an empty line or a new tag 
            if not line:
                all_dialogue_by_target_character += "\n\n"
                recording_a_characters_utterance = False

            elif OPEN_TAG in line or CLOSE_TAG in line:
                if not target_character_tag == find_character_tag(line):
                    all_dialogue_by_target_character += "\n\n"
                    recording_a_characters_utterance = False

            else:
                all_dialogue_by_target_character += line + " "

        if not recording_a_characters_utterance:
            if target_character_tag == find_character_tag(line):
                recording_a_characters_utterance = True

                if not preserve_tags:
                    line = line[len(target_character_tag):]


                all_dialogue_by_target_character += line + " "

    return all_dialogue_by_target_character


def extract_character_tags_from_file(input_file: Path) -> set[str]:

    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]

    character_tag = ""
    character_name = ""

    character_tags : set[str] = set()

    for line in lines:
        character_tag = find_character_tag(line)

        if character_tag:
            character_tags.add(character_tag)

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

        target_dir : Path = Path(source_dir)

        # Iterate through path objects inside the directory
        for input_path in sorted(target_dir.iterdir()):

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

def determine_output_dir(input_file: str | None, source_dir : str | None) -> Path:
    base_output_dir = "./corpora/"

    if input_file:
        return Path(base_output_dir)

    elif source_dir:
        return Path(base_output_dir + source_dir)

    return Path(base_output_dir)


def tag_to_name(tag: str) -> str:
    print(tag)
    tag_no_separator = tag.rstrip(SEPARATOR)
    name = tag_no_separator.lstrip(OPEN_TAG).rstrip(CLOSE_TAG).lower()
    return name[:1].upper() + name[1:]


def main():
    # Parse the CLI arguments 
    args = parse_arguments()

    preserve_tags = args.preserve_tags


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


    data_to_write = ""
    output_file_name = ""

    if action_choice == Action.EXTRACT_CHARACTER:

        all_dialogue_by_target_character = ""

        for file in files_to_process:
            all_dialogue_by_target_character += extract_character_dialogue(file, character_tag_choice, preserve_tags)

        data_to_write = all_dialogue_by_target_character
        output_file_name = f"{tag_to_name(character_tag_choice).lower()}_only.txt"

       

    elif action_choice == Action.EXTRACT_OTHERS:
        target_characters_tags = all_character_tags - {character_tag_choice}

        all_dialogued_by_everyone_but_chosen_character = ""

        # Not the most efficient way, since the text is being read N times where N the amount of target character tags
        # still instantaneous on modern CPUs, while the logic is simple and reused
        for file in files_to_process:
            for target_tag in target_characters_tags:
                all_dialogued_by_everyone_but_chosen_character += extract_character_dialogue(file, target_tag, preserve_tags)

        data_to_write = all_dialogued_by_everyone_but_chosen_character
        output_file_name = f"all_except_{tag_to_name(character_tag_choice).lower()}.txt"




    base_output_dir = determine_output_dir(args.input_file, args.source_dir)
    base_output_dir.mkdir(parents=True, exist_ok=True)

    full_output_path = base_output_dir / Path(output_file_name)

    with open(full_output_path, "w") as f:
        f.write(data_to_write)









if __name__ == "__main__":
    main()







