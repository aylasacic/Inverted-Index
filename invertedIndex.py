'''
Author:
Date:
Description:

How to run: python3 inverted_index.py --input-file word_counts.txt --output-file inverted_index.pkl
Format of word_counts.txt: 
'''

import pickle
from collections import defaultdict
import argparse
import os
import csv

import nltk

# rnsure nltk stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords

def buildInvertedIndex(file_path):
    """
        builds an inverted index from the given word_counts.txt file.
        
        input:
            - file_path: Path to the word_counts.txt file

        output: inverted index as a defaultdict
    """
    inverted_index = defaultdict(list)
    line_number = 0  # for debugging 

    # see if file exists
    if not os.path.exists(file_path):
        print(f"Input file not found: {file_path}")
        return inverted_index

    try:
        # open file
        with open(file_path, 'r', encoding = 'utf-8') as file:
            # read the file (tab delimiter)
            reader = csv.reader(file, delimiter = '\t', quotechar = '"')
            for row in reader:
                line_number += 1
                # skip row if no lines
                if not row:
                    continue  

                # see if there are five tab seperated things in the line
                if len(row) < 5:
                    # skip row if such
                    print(f"malformed line {line_number}: {row}")
                    continue

                # unpack row into filename, title, word, frequecny and contexts
                filename, title, word, frequency_str, joined_contexts = row

                # exclude stop words
                if word.lower() in stopwords.words('english'):
                    continue

                # convert frequency to integer
                try:
                    frequency = int(frequency_str)
                except ValueError:
                    print(f"invalid frequency")
                    continue

                # Split contexts by ' | ' and clean them
                contexts = [ctx.strip() for ctx in joined_contexts.split('|') if ctx.strip()]

                # make entry
                entry = {
                    'filename': filename,
                    'title': title,
                    'count': frequency,
                    'contexts': contexts
                }

                # add entry to a lowercase word in the inverted index
                inverted_index[word.lower()].append(entry)

    except Exception as e:
        print(f"An error occurred while building the index: {e}")

    return inverted_index

def saveIndex(index, filename):
    """
        saves the inverted index to a file using pickle.
    
        input:
            - index: The inverted index to save
            - filename: The filename to save the index to
        ouput: index saved to file
    """
    try:
        # open provided filename
        with open(filename, 'wb') as f:
            # save it using pickle
            pickle.dump(index, f)
        print(f"inverted index saved to {filename}")
    except Exception as e:
        print(f"failed to save index: {e}")

def main():
    # argparser for easier argparsing than using sys
    parser = argparse.ArgumentParser(description = "build an inverted index from word_counts.txt.")
    parser.add_argument(
        '-i','--input_file', 
        type = str, 
        default = 'word_counts.txt',
        help = 'Path to the input word counts file (default: word_counts.txt)')
    parser.add_argument(
        '-o', '--output_file', 
        type = str, 
        default = 'inverted_index.pkl',
        help = 'Filename to save the inverted index (default: inverted_index.pkl)')

    args = parser.parse_args()

    # ensure nltk stopwords are downloaded
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')

    # build the index
    print("Building the inverted index...")
    index = buildInvertedIndex(args.input_file)
    # get unique words (for debugging)
    print(f"Total unique words (excluding stop words): {len(index)}")
    # save idnex
    saveIndex(index, args.output_file)

if __name__ == "__main__":
    main()
