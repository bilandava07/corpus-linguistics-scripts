from os.path import exists
from pathlib import Path
import os
from args_parser import parse_arguments


def find_all_character_markers(input_file: Path):
    pass



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




if __name__ == "__main__":
    main()










        







  


    



