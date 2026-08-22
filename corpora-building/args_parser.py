import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            " Description follows.." 
        ),
        epilog=(
            "Example:\n"
            "  sor_automation -i schools.csv -n 100 -s -d -c\n\n"
            "At least one report type (-s, -d, or -c) must be selected."
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

    output_arguments = parser.add_mutually_exclusive_group(required=True)

    output_arguments.add_argument(
        "-if",
        "--output-file",
        metavar="<output_file_path>",
        help="Path to the output .txt file"
    )

    output_arguments.add_argument(
        "-sd",
        "--output-dir",
        metavar="<output_directory>",
        help="Path to the directory where the output files will be saved to"
    )


    arguments_parsed = parser.parse_args()
    return arguments_parsed


