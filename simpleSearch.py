import pickle
import math

# run only first time
# nltk.download('stopwords')
from nltk.corpus import stopwords

def load_inverted_index(pickle_file):
    """
        loads the inverted index from a pickle file.
        
        input:
            - pickle_file: path to the pickle file containing the inverted index

        output:
            - the inverted index dictionary
    """
    try:
        # open the file provided
        with open(pickle_file, 'rb') as f:
            inverted_index = pickle.load(f)
        return inverted_index
    except FileNotFoundError:
        # file does not exist
        print(f"\33[31m\33[1merror: file '{pickle_file}' does not exist. \33[0m")
    except Exception as e:
        # error while loading
        print(f"\33[31m\33[1man error occurred while loading the index: {e}\33[0m")
    return None

def load_word_count(word_count_file):
    """
        loads the word counts from a file into a dictionary.
        
        input:
            - word_count_file: path to the word count file

        output:
            - dictionary mapping filenames to their total word counts
    """
    # initialize dictionary
    word_count = {}
    try:
        # open the file
        with open(word_count_file, 'r') as f:
            # for each line 
            for line in f:
                # strip of whitespace (leading and trailing)
                line = line.strip()
                # if line is empty
                if not line:
                    # continue partsing thorugh file
                    continue
                # is there is no : in the line (this is th format of the word_count file)
                if ':' not in line:
                    print(f"\33[33m\33[1mWarning: Skipping malformed line: '{line}'\33[0m")
                    continue
                # split the line with : as delimiter
                filename, count = line.split(':', 1)
                # strip the filename of trailing and leading whitespaces again
                filename = filename.strip()
                try:
                    # get the count after stiping of trailing and leading whitespaces
                    count = int(count.strip())
                    # set the wordcount of the filename to the count
                    word_count[filename] = count
                except ValueError:
                    print(f"\33[33m\33[1mWarning: Invalid count for '{filename}': '{count}'\33[0m")
    except FileNotFoundError:
        print(f"\33[31m\33[1mError: The file '{word_count_file}' does not exist.\33[0m")
    except Exception as e:
        print(f"\33[31m\33[1mAn error occurred while loading word counts: {e}\33[0m")
    return word_count

def getTotalDocs(word_count_dict):
    """
        computes the total number of unique documents from the word count dictionary.
    
        input:
            - word_count_dict: dictionary mapping filenames to total word counts

        output: total number of unique documents
    """
    return len(word_count_dict)

def searchWord(inverted_index, word, N, word_count_dict, top_n = 10):
    """
        searches for a word in the inverted index and returns the top n entries sorted by tf-idf
        
        input:
            - inverted_index: the inverted index dictionary
            - word: the word to search for
            - N: total number of documents
            - word_count_dict: dictionary mapping filenames to total word counts
            - top_n: number of top results to return

        output: list of n entries with tf-idf scores
    """
    # get the results from the inverted index
    results = inverted_index.get(word.lower(), [])
    # if there are no results, print as such
    if not results:
        print(f"\33[31m\33[1mThe word '{word}' was not found in the index.\33[0m")
        return []

    # get the length of the results
    df = len(results)
    # if there are none, print as such 
    if df == 0:
        print(f"\33[31m\33[1mThe word '{word}' was not found in any document.\33[0m")
        return []

    # inverse document frequency
    idf = math.log(N / df)

    # calculate normalized tf-idf for each entry
    for entry in results:
        # get the count of the words in the file
        tf_count = entry.get('count', 0)
        # get the corresponding filename
        filename = entry.get('filename')
        # get total count of words in the file
        total_words = word_count_dict.get(filename, 1)  
        # if total words <= 0 (there are none)
        if total_words <= 0:
            total_words = 1 # avoid division by zero
        # term frequency
        tf = tf_count / total_words
        # set the tfidf value for the current entry
        entry['tfidf'] = tf * idf

    # sort results based on tf-idf score in descending order
    sorted_results = sorted(results, key = lambda x: x['tfidf'], reverse = True)
    return sorted_results[:top_n]

def display_results(word, results):
    """
        displays the search results in a readable format, including the title and TF-IDF score
        
        input:
            - word: the searched word
            - results: list of result entries
    """
    # if results are empty
    if not results:
        # print that there are none
        print(f"\33[31m\33[1mNo results found for '{word}'.\33[0m")
        return

    # print the results
    print(f"\nSearch Results for '{word}':\n{'-'*60}")
    for idx, entry in enumerate(results, 1):
        filename = entry.get('filename', 'N/A')
        title = entry.get('title', 'No Title')
        tfidf = entry.get('tfidf', 0)
        contexts = entry.get('contexts', [])
        context_sample = contexts[0] if contexts else "No context available."
        print(f"{idx}. {filename} - TF-IDF: {tfidf:.3f} (Article: {title}) \33[90m {context_sample} \33[0m")

def interactive_search(inverted_index, N, word_count_dict):
    """
        Loop for searching words in the inverted index.
        
        input:
            - inverted_index: the inverted index dictionary
            - N: total number of documents
            - word_count_dict: dictionary mapping filenames to total word counts
    """

    # constant loop
    while True:
        # get input from user
        word = input("\33[1mEnter Search Term (or type 'EXIT' to quit): \33[0m").strip()
        # if the word is EXIT (all capital) -> exit
        # this is so that searching 'exit' works
        if word == 'EXIT':
            print("\33[35m\33[1mExiting the search tool. Goodbye!\33[1m")
            break
        # if word is empty (they pressed enter)
        if not word:
            print("\33[33m\33[1mPlease enter a valid word.\33[1m")
            continue
        # accept no stopword as they were removed in the making of the inverted index
        if word.lower() in stopwords.words('english'):
            print("\33[33m\33[1mStopwords are not searchable.\33[1m")
            continue

        # search the word in the inverted index
        results = searchWord(inverted_index, word, N, word_count_dict)
        # display results
        if results:
            display_results(word, results)
            print("\n" + "="*60 + "\n")

def main():
    # inverted index file (made through inverted_index.py file)
    index_file = 'inverted_index.pkl'  
    # word count file (made through wordCount.py file)
    word_count_file = 'wordCount.txt' 
    # load inverted index
    print("Loading the inverted index...")
    inverted_index = load_inverted_index(index_file)
    if inverted_index is None:
        return
    print("Inverted index loaded successfully.\n")
    # load word count
    print("Loading word count...")
    word_count_dict = load_word_count(word_count_file)
    if word_count_dict is None:
        return
    print("Word count loaded successfully.\n")

    print("Computing total number of documents...")
    # get number of documents
    N = getTotalDocs(word_count_dict)

    # start search
    interactive_search(inverted_index, N, word_count_dict)

if __name__ == "__main__":
    main()
