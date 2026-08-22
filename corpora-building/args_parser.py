import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            " Description follows.." 
        ),
        epilog=(
            #TODO:  
            "Example:\n"
            "follows..."
            ""
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    input_arguments = parser.add_mutually_exclusive_group(required=True)

    input_arguments.add_argument(
        "-if",
        "--input-file",
        metavar="<input_file_path>",
        help="Path to the input .txt file containing the transcript to processed"
    )

    input_arguments.add_argument(
        "-sd",
        "--source-dir",
        metavar="<source_directory>",
        help="Path to the directory, containing the .txt transcript files to process"
    )


    parser.add_argument(
        "-pt",
        "--preserve-tags",
        action="store_true",
        default=False,
        help="Set to True to preserve the character tags in the output file"
    )


    arguments_parsed = parser.parse_args()
    return arguments_parsed


