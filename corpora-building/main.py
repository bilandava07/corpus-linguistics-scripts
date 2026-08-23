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


def format_dialogue_lines(input_file: Path, character_tags: set[str]) -> str:
    # read in the file content 
    content = input_file.read_text(encoding="utf-8")

    # split into lines and get rid of spaces at the beginning and at the end
    lines = [line.strip() for line in content.splitlines()]

    formatted_output = ""

    recording_a_characters_utterance = False

    for line in lines:
        if recording_a_characters_utterance:
            if not line:
                formatted_output += "\n\n"
                recording_a_characters_utterance = False

            elif OPEN_TAG in line or CLOSE_TAG in line:
                raise Exception(
                f"Formatting error! \n\n {line}\n\n" +
                "No blank line between two characters' utterances! "
                )

            else:
                formatted_output += line + " "

        else: # not recording an utterance
            if find_character_tag(line):
                recording_a_characters_utterance = True
                formatted_output += "\n" + line + " "

            else:
                if not line:
                    formatted_output += "\n"

                elif OPEN_TAG in line or CLOSE_TAG in line:
                    raise Exception(
                    f"Formatting error! \n\n {line}\n\n" +
                    "No blank line between two characters' utterances! "
                    )

                else:
                    formatted_output += "\n" + "[OTHERS]:" + line + "\n"

    return formatted_output


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
    base_output_dir = Path("./corpora/")

    if input_file:
        return base_output_dir

    elif source_dir:
        season_dir = Path(source_dir).name
        return base_output_dir / season_dir

    return base_output_dir


def tag_to_name(tag: str) -> str:
    tag_no_separator = tag.rstrip(SEPARATOR)
    name = tag_no_separator.lstrip(OPEN_TAG).rstrip(CLOSE_TAG).lower()
    return name[:1].upper() + name[1:]


def write_file_to_disk(content: str, output_path: Path):
    with open(output_path, "w") as f:
        f.write(content)

    print(f"Wrote output file to:  {output_path}")



def main():

    # Parse the CLI arguments 
    args = parse_arguments()

    preserve_tags = args.preserve_tags


    input_files = identify_files_to_process(args.input_file, args.source_dir)

    # Format all dialogue before processing
    base_formatted_output_dir = Path("./formatted")
    base_formatted_output_dir.mkdir(parents=True, exist_ok=True)
    formatted_files_to_process : list[Path] = []

    all_character_tags_in_input_files : set[str] = find_all_character_tags(input_files)
    print("Character tags identified in the input files: ")
    print(all_character_tags_in_input_files)
    print()

    for file in input_files:
        formatted_output = format_dialogue_lines(file, all_character_tags_in_input_files)

        output_file = base_formatted_output_dir / file
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            f.write(formatted_output)

        formatted_files_to_process.append(output_file)

    all_character_tags = find_all_character_tags(formatted_files_to_process)
    print("Character tags after formatting the files: ")
    print(all_character_tags)
    print()


    # Prompt the user to pick the character from names
    chosen_character_tag = questionary.select(
            "Pick the target character",
            choices=[ questionary.Choice(f"{tag_to_name(tag)}", value=tag) for tag in sorted(all_character_tags)]
    ).ask()

    # Prompt the user to pick the action
    action_choice = questionary.select(
            "Pick the action that you would like to perform for the target character",
            choices=[
                questionary.Choice(
                    f"Extract all dialogue produced by {tag_to_name(chosen_character_tag)}",
                    value=Action.EXTRACT_CHARACTER
                ),
                questionary.Choice(
                    f"Extract all dialogue produced by everyone other than {tag_to_name(chosen_character_tag)}",
                    value=Action.EXTRACT_OTHERS
                ),
            ]
    ).ask()


    chosen_character_name = tag_to_name(chosen_character_tag).lower()

    if action_choice == Action.EXTRACT_CHARACTER:

        # Initialize the output directory
        base_formatted_output_dir = determine_output_dir(args.input_file, args.source_dir) / Path(f"{chosen_character_name}_only{'_tags_preserved' if preserve_tags else ''}")
        base_formatted_output_dir.mkdir(parents=True, exist_ok=True)

        for file in formatted_files_to_process:
            dialogue_by_target_character = ""

            dialogue_by_target_character += extract_character_dialogue(file, chosen_character_tag, preserve_tags)

            output_file = Path(
                f"{file.stem}_{chosen_character_name}_only"
                f"{'_tags_preserved' if preserve_tags else ''}.txt"
            )

            write_file_to_disk(
                content=dialogue_by_target_character,
                output_path=base_formatted_output_dir / output_file
            )


    elif action_choice == Action.EXTRACT_OTHERS:

        # Initialize the output directory
        base_formatted_output_dir = determine_output_dir(args.input_file, args.source_dir) / Path(f"all_except_{chosen_character_name}{'_tags_preserved' if preserve_tags else ''}")
        base_formatted_output_dir.mkdir(parents=True, exist_ok=True)

        target_characters_tags = all_character_tags - {chosen_character_tag}


        # Not the most efficient way, since the text is being reread N times where N is the amount of target character tags
        # still instantaneous on modern CPUs, while the logic is simple and reusable
        for file in formatted_files_to_process:

            all_dialogue_except_chosen_character = ""

            for target_tag in target_characters_tags:
                all_dialogue_except_chosen_character += extract_character_dialogue(file, target_tag, preserve_tags)

            output_file = Path(
                f"{file.stem}_except_{chosen_character_name}"
                f"{'_tags_preserved' if preserve_tags else ''}.txt"
            )

            write_file_to_disk(
                content=all_dialogue_except_chosen_character,
                output_path=base_formatted_output_dir / output_file
            )



if __name__ == "__main__":
    main()







