import os
import re
import argparse
from tqdm import tqdm
import string
import subprocess

def parse_arguments():
    parser = argparse.ArgumentParser(description = "Process text documents: preprocess, combine, count words, and optionally run MapReduce.")
    parser.add_argument(
        '-i', '--input_dir',
        type = str,
        default = "documents10k",
        help = 'Path to the input directory containing the documents to be processed. Default is "documents10k".'
    )
    parser.add_argument(
        '-c', '--cleaned_dir',
        type = str,
        default = "cleaned_documents10k",
        help = 'Path to the output directory where cleaned documents will be saved. Default is "cleaned_documents10k".'
    )
    parser.add_argument(
        '-o', '--combined_file',
        type = str,
        default = "combined_documents.txt",
        help = 'Path to the output combined .txt file. Defaults to "combined_documents.txt".'
    )
    parser.add_argument(
        '-w', '--wordcount_file',
        type = str,
        default = "wordCount.txt",
        help = 'Path to the output file where word counts will be written. Defaults to "wordCount.txt".'
    )
    parser.add_argument(
        '--run_mapreduce',
        action = 'store_true',
        help = 'Flag to run the MapReduce job after processing.'
    )
    parser.add_argument(
        '--context_size',
        type = int,
        default = 3,
        help = 'Number of words to include before and after the target word as context in MapReduce job.'
    )
    parser.add_argument(
        '--mapreduce_output',
        type = str,
        default = "word_counts.txt",
        help = 'Output file for MapReduce results. Defaults to "word_counts.txt".'
    )
    parser.add_argument(
        '--build_inverted_index',
        action = 'store_true',
        help = 'Flag to build the inverted index after MapReduce.'
    )
    parser.add_argument(
        '--inverted_index_file',
        type = str,
        default = 'inverted_index.pkl',
        help = 'Filename to save the inverted index (default: inverted_index.pkl)'
    )
    return parser.parse_args()
    return parser.parse_args()

def run_inverted_index(input_file, output_file):
    """
        runs the invertedIndex.py script using subprocess

        parameters:
            - input_file (str): the path to the input file
            - output_file (str): he path to the output file
    """
    cmd = [
        'python3', 'invertedIndex.py',
        '--input_file', input_file,
        '--output_file', output_file
    ]

    try:
        subprocess.run(cmd, check = True)
        print(f"Inverted index built and saved to '{output_file}'.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while building the inverted index: {e}")

# function to clean a single file's content
def cleanText(text):
    # remove sections after specific headers
    text = re.split(r"==See also==", text, 1)[0]
    text = re.split(r"== References ==", text, 1)[0]
    text = re.split(r"== External links ==", text, 1)[0]
    
    # Remove various types of headers
    text = re.sub(r"===.*?===", "", text)  # removes headers like ===Header===
    text = re.sub(r"==.*?==", "", text)    # removes headers like ==Header==
    
    # remove wikitables and HTML/XML tags
    text = re.sub(r"{\|.*?\|}", "", text, flags=re.DOTALL)  
    text = re.sub(r"<.*?>", "", text)                       
    
    # remove urls and specific patterns
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r"\bthumb\|.*?\|", "", text)
    text = re.sub(r"\b\d+px\b\s*\w*", "", text)  # removes numeric px| patterns and trailing content
    
    # replace escaped apostrophe and separate punctuation
    text = text.replace(r"\"", "\"")  # fix apostrophes
    text = re.sub(r"([.,*:;!?()|])", r" \1 ", text)  # separate punctuation from words
    
    # remove newline characters
    text = text.replace("\n", " ").replace("\r", " ")
    
    # remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def preprocess_files(input_dir, output_dir):
    # create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist.")
        return

    # iterate through files in the input directory
    for filename in tqdm(os.listdir(input_dir), desc="Preprocessing files"):
        file_path = os.path.join(input_dir, filename)
        
        # open the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # if file is empty, skip it
        if not lines:
            continue
        
        # extract the title line (strip trailing and leading whitespace)
        title_line = lines[0].strip()
        
        # ensure the title line starts with "Title: "
        if not title_line.startswith("Title: "):
            print(f"Warning: {filename} does not start with a title line.")
            # get the body text
            body_text = ''.join(lines)
            # clean it using the function above
            cleaned_body = cleanText(body_text)
            # get the final content
            final_content = cleaned_body
        else:
            # extract the title text
            title_text = title_line 
            
            # combine the remaining lines into body text
            body_text = ''.join(lines[1:])  # Exclude the title line
            cleaned_body = cleanText(body_text)
            
            # combine the title and cleaned body with a newline
            final_content = f"{title_text}\n{cleaned_body}"
        
        # save the cleaned content to a new file
        output_path = os.path.join(output_dir, filename)
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                file.write(final_content)
        except Exception as e:
            print(f"Error writing to '{output_path}': {e}")
            continue

    print(f"Preprocessing complete. Cleaned files saved in {output_dir}")

def combine_files(input_dir, combined_file_path):
    """
        combines all files in the input directory into a single tab-delimited text file
        each line contains 'filename', 'title', and 'content' separated by tabs

        parameters:
            - input_dir (str): directory containing the input text files.
            - combined_file_path (str): Path to the output combined .txt file.
    """
    try:
        with open(combined_file_path, 'w', encoding='utf-8') as outfile:
            # outfile.write("Filename\tTitle\tContent\n")
            
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

                        # create a tab delimited line
                        line_out = f"{filename_clean}\t{title_clean}\t{content_clean}\n"

                        # rrite the line to the output file
                        outfile.write(line_out)

                except Exception as e:
                    print(f"Error processing file '{filename}': {e}")

        print(f"All files have been successfully combined into '{combined_file_path}' in tab-delimited format.")

    except Exception as e:
        print(f"Failed to write to '{combined_file_path}': {e}")

def count_words(input_folder, output_file):
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

            # iterate over all files (track progress using tqdm)
            for filename in tqdm(files, desc="Counting words"):
                file_path = os.path.join(input_folder, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        lines = infile.readlines()
                        
                        if not lines:
                            # if the file is empty -> word count is 0
                            word_count = 0
                        else:
                            # skip the first line (assumed to be the title)
                            content = ''.join(lines[1:])
                            
                            # remove punctuation
                            content = content.translate(translator)
                            
                            # split the content into words
                            words = content.split()
                            
                            # count the number of words
                            word_count = len(words)
                    
                    # write the filename and word count to the output file
                    outfile.write(f"{filename}:{word_count}\n")
                
                except Exception as e:
                    # handle exceptions byt just prinitng out the file that failed
                    print(f"Error processing '{filename}': {e}")

        print(f"Word counts have been written to '{output_file}'.")

    except Exception as e:
        print(f"Failed to write to '{output_file}': {e}")

def run_mapreduce(combined_file, output_file, context_size):
    """
        runs the MapReduce job using mapReduceWordCount.py
    """
    # cuild the command to run the MapReduce job
    cmd = [
        'python3', 'mapReduceWordCount.py',
        combined_file,
        '--context-size', str(context_size)
    ]

    # open the output file to write the MapReduce results
    with open(output_file, 'w', encoding = 'utf-8') as outfile:
        # run the command and redirect stdout to the output file
        subprocess.run(cmd, stdout = outfile)

    print(f"MapReduce job complete. Results saved in '{output_file}'.")

def main():
    args = parse_arguments()
    input_dir = args.input_dir
    cleaned_dir = args.cleaned_dir
    combined_file = args.combined_file
    wordcount_file = args.wordcount_file
    run_mr = args.run_mapreduce
    context_size = args.context_size
    mapreduce_output = args.mapreduce_output
    build_index = args.build_inverted_index
    inverted_index_file = args.inverted_index_file


    # preprocess files
    preprocess_files(input_dir, cleaned_dir)

    # combine files
    combine_files(cleaned_dir, combined_file)

    # count words
    count_words(cleaned_dir, wordcount_file)

    # run MapReduce job if requested
    if run_mr:
        run_mapreduce(combined_file, mapreduce_output, context_size)

    if build_index:
        run_inverted_index(mapreduce_output, inverted_index_file)

if __name__ == "__main__":
    main()
