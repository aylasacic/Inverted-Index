import os
import argparse
from tqdm import tqdm

def parse_arguments():
    parser = argparse.ArgumentParser(
        description = "Combine multiple text files into a single tab-delimited file with filename, title, and content."
    )
    parser.add_argument(
        '-i', '--input_dir',
        type = str,
        required = True,
        help = 'Path to the input directory containing the text files to combine.'
    )
    parser.add_argument(
        '-o', '--output_file',
        type = str,
        default = "combined_documents.txt",
        help = 'Path to the output combined .txt file. Defaults to "combined_documents.txt".'
    )
    return parser.parse_args()

def combineFiles(input_dir, combined_file_path):
    """
        combines all files in the input directory into a single tab-delimited text file
        each line contains 'filename', 'title', and 'content' separated by tabs

        parameters:
            - input_dir (str): directory containing the input text files.
            - combined_file_path (str): Path to the output combined .txt file.
    """
    try:
        with open(combined_file_path, 'w', encoding='utf-8') as outfile:
            # write header line (optional)
            outfile.write("Filename\tTitle\tContent\n")
            
            # get list of files
            files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
            
            if not files:
                print(f"No files found in the input directory '{input_dir}'.")
                return

            # iterate through each file with progress tracking
            for filename in tqdm(files, desc="Combining files"):
                file_path = os.path.join(input_dir, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        # if file is empty, skip it
                        if not lines:
                            print(f"Skipping '{filename}': File is empty.")
                            continue

                        # initialize title and content
                        title_text = "[Missing Title]"
                        content = []

                        # process lines to extract title and content
                        for line in lines:
                            # remove trailing and leading whitespaces
                            line = line.strip()
                            
                            # check for title line
                            if line.startswith("Title: "):
                                title_text = line[len("Title: "):].strip()
                            elif not line.startswith("Filename: "):
                                # append to content if it's not a filename or title line
                                content.append(line)

                        # join content lines with spaces
                        content_text = ' '.join(content)

                        # replace any tabs in the fields to avoid misalignment
                        filename_clean = filename.replace('\t', ' ')
                        title_clean = title_text.replace('\t', ' ')
                        content_clean = content_text.replace('\t', ' ')

                        # create a tab-delimited line
                        line_out = f"{filename_clean}\t{title_clean}\t{content_clean}\n"

                        # write the line to the output file
                        outfile.write(line_out)

                except Exception as e:
                    print(f"Error processing file '{filename}': {e}")

        print(f"\nAll files have been successfully combined into '{combined_file_path}' in tab-delimited format.")

    except Exception as e:
        print(f"Failed to write to '{combined_file_path}': {e}")

def main():
    args = parse_arguments()
    input_dir = args.input_dir
    output_combined_file = args.output_file

    # check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist.")
        return

    combineFiles(input_dir, output_combined_file)

if __name__ == "__main__":
    main()
