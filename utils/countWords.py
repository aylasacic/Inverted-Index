import os
import string
import argparse
from tqdm import tqdm

def parse_arguments():
    """
    parse command-line arguments for input directory and output file
    """
    parser = argparse.ArgumentParser(
        description="Count the number of words in each document within the input folder, skipping the first line and excluding punctuation."
    )
    parser.add_argument(
        '-i', '--input_dir',
        type=str,
        required=True,
        help='Path to the input directory containing the text files.'
    )
    parser.add_argument(
        '-o', '--output_file',
        type=str,
        default='wordCount.txt',
        help='Path to the output file where word counts will be written. Defaults to "wordCount.txt".'
    )
    return parser.parse_args()

def countWords(input_folder, output_file):
    """
    counts the number of words in each document within the input_folder
    skips the first line and excludes punctuation
    writes the results to output_file.

    parameters:
        - input_folder (str): location of the input files
        - output_file (str): path to the output file
    """
    # prepare a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # write header line (optional)
            # outfile.write("Filename\tWordCount\n")

            # get list of files
            files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

            if not files:
                print(f"No files found in the input directory '{input_folder}'.")
                return

            # iterate over all files with progress tracking
            for filename in tqdm(files, desc="Counting words"):
                file_path = os.path.join(input_folder, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        if not lines:
                            # if the file is empty -> word count is 0
                            word_count = 0
                        else:
                            # skip the first line -> title
                            content = ''.join(lines[1:])
                            
                            # remove punctuation
                            content = content.translate(translator)
                            
                            # split the content into words (remove trailing and leading whitespaces)
                            words = content.split()
                            
                            # count the number of words
                            word_count = len(words)
                    
                    # write the filename and word count to the output file
                    outfile.write(f"{filename}:{word_count}\n")
                
                except Exception as e:
                    # handle exceptions and continue
                    print(f"Error processing '{filename}': {e}")

        print(f"\nWord counts have been written to '{output_file}'.")
    
    except Exception as e:
        print(f"Failed to write to '{output_file}': {e}")

def main():
    args = parse_arguments()
    input_folder = args.input_dir
    output_file = args.output_file

    # check if input directory exists
    if not os.path.isdir(input_folder):
        print(f"Error: The input directory '{input_folder}' does not exist.")
        return

    countWords(input_folder, output_file)

if __name__ == "__main__":
    main()