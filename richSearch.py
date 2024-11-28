import pickle
import math
from rich import print  
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich import box
import pyfiglet
import time

# run only first time
import nltk

# ensure NLTK stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

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
        print(f"[bold red]Error: The file '{pickle_file}' does not exist.[/bold red]")
    except Exception as e:
        # error while loading
        print(f"[bold red]An error occurred while loading the index: {e}[/bold red]")
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
                    print(f"[bold yellow]Warning: Skipping malformed line: '{line}'[/bold yellow]")
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
                    print(f"[bold yellow]Warning: Invalid count for '{filename}': '{count}'[/bold yellow]")
    except FileNotFoundError:
        print(f"[bold red]Error: The file '{word_count_file}' does not exist.[/bold red]")
    except Exception as e:
        print(f"[bold red]An error occurred while loading word counts: {e}[/bold red]")
    return word_count

def getTotalDocs(word_count_dict):
    """
        computes the total number of unique documents from the word count dictionary.
    
        input:
            - word_count_dict: dictionary mapping filenames to total word counts

        output: total number of unique documents
    """
    return len(word_count_dict)

def search_word(inverted_index, word, N, word_count_dict, n=10):
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
        print(f"[bold red]The word '{word}' was not found in the index.[/bold red]")
        return []

    # get the length of the results
    df = len(results)
    # if there are none, print as such
    if df == 0:
        print(f"[bold red]The word '{word}' was not found in any document.[/bold red]")
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
            total_words = 1  # avoid division by zero
        # term frequency
        tf = tf_count / total_words
        # set the tfidf value for the current entry
        entry['tfidf'] = tf * idf

    # sort results based on TF-IDF score in descending order
    sorted_results = sorted(results, key=lambda x: x['tfidf'], reverse=True)
    return sorted_results[:n]

def highlight_word(text, word, max_length = 100):
    """
        highlights all occurrences of the search word in the given text and truncates it if necessary
        
        input:
            - text: the context text
            - word: the word to highlight
            - max_length: maximum length of the context to display

        output: a Rich Text object with highlighted words
    """
    # if text larger than maximum allowed text, truncate it
    if len(text) > max_length:
        text = text[:max_length] + "..."

    # initialize rich text object
    rich_text = Text(text)
    # set all words to lower (already done but just to make sure)
    word_lower = word.lower()

    start = 0

    # loop over the text and higlitht the word what is needed
    while True:
        index = text.lower().find(word_lower, start)
        if index == -1:
            break
        # highlight the word
        rich_text.stylize("bold red", index, index + len(word))
        start = index + len(word)

    return rich_text

def display_results(word, results):
    """
        displays the search results in a readable format, including the title and TF-IDF score
        
        input:
            - word: the searched word
            - results: list of result entries
    """
    # if results are empty
    if not results:
        print(f"[bold red]No results found for '{word}'.[/bold red]")
        return

    # initialize console object
    console = Console()

    # create a table
    table = Table(title = f"Search Results for '{word}'", box = box.MINIMAL_DOUBLE_HEAD)

    # define columns
    table.add_column("No.", no_wrap = True, justify = 'right', style = "bold white")
    table.add_column("Filename")
    table.add_column("Article Title", style = "bold")
    table.add_column("TF-IDF Score", justify = "center")
    table.add_column("Context")

    # get the entries for the column values
    for idx, entry in enumerate(results, 1):
        filename = entry.get('filename', 'N/A')
        title = entry.get('title', 'No Title')
        tfidf = f"{entry.get('tfidf', 0):.3f}"  # Increased precision
        contexts = entry.get('contexts', [])
        context_sample = contexts[0] if contexts else "No context available."

        # highlight the searched word in the context
        highlighted_context = highlight_word(context_sample, word)

        # add row to the table
        table.add_row(
            str(idx),
            filename,
            title,
            tfidf,
            highlighted_context
        )

    # print it out in the console
    console.print(table)

def display_banner(console):
    """
        displays the stylized MapIndex banner.
        
        input: 
            - console: Rich console instance
    """
    # generate ASCII Art using pyfiglet with a desired font
    ascii_banner = pyfiglet.figlet_format("MapIndex", font = "big")

    # create styled text for title and subtitle
    title = "[bold green]Welcome to MapIndex Terminal[/bold green]"

    # combine title and ASCII banner
    combined_text = f"{title}\n\n{ascii_banner}"

    # create a Rich Panel with the combined text
    panel = Panel(
        combined_text,
        style = "bold magenta",
        border_style = "blue",
        padding = (1, 2),
        expand = False
    )

    # align the panel to the center of the terminal
    centered_panel = Align.center(panel)

    # print the centered panel to the console
    console.print(centered_panel)

def interactive_search(inverted_index, N, word_count_dict):
    """
        Loop for searching words in the inverted index.
        
        input:
            - inverted_index: the inverted index dictionary
            - N: total number of documents
            - word_count_dict: dictionary mapping filenames to total word counts
    """

    # initialize the Rich console
    console = Console()

    # constant loop
    while True:
        # get input from user
        word = console.input("[bold blue]Enter Search Term (or type 'EXIT' to quit): [/bold blue]").strip()
        # if the word is EXIT (all capital) -> exit
        # this is so that searching 'exit' works
        if word == 'EXIT':
            print("[bold red]Exiting the search tool. Goodbye![/bold red]")
            break
        # if word is empty (they pressed enter), continue but warn
        if not word:
            print("[bold yellow]Please enter a valid word.[/bold yellow]")
            continue
        # accept no stopword as they were removed in the making of the inverted index
        if word.lower() in stopwords.words('english'):
            print("[bold yellow]Stopwords are not searchable.[/bold yellow]")
            continue

        # search the word in the inverted index
        results = search_word(inverted_index, word, N, word_count_dict)
        # display results
        if results:
            display_results(word, results)

def main():
    # inverted index file (made through inverted_index.py file)
    index_file = 'inverted_index.pkl'  
    # word count file (made through wordCount.py file)
    word_count_file = 'wordCount.txt'  
    # initialize a Rich console
    console = Console()

    # display loading animation for the inverted index
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Loading Inverted Index..."),
        transient=True,
    ) as progress:
        progress.add_task("loading")
        inverted_index = load_inverted_index(index_file)
        time.sleep(1)  # simulate loading time (for short files)

    if inverted_index is None:
        console.print("[bold red]Failed to load the inverted index. Exiting...[/bold red]")
        return

    # display success message
    print("[bold green]Inverted index loaded successfully![/bold green]\n")

    # display loading animation for the word counts
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Loading Word Counts..."),
        transient=True,
    ) as progress:
        progress.add_task("loading_word_count")
        word_count_dict = load_word_count(word_count_file)
        time.sleep(1)  # simulate loading time (for short files)

    # if the dict is empty, exit
    if not word_count_dict:
        console.print("[bold red]Failed to load word counts or word counts are empty. Exiting...[/bold red]")
        return

    # compute total number of documents
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold green]Computing total number of documents..."),
        transient=True,
    ) as progress:
        progress.add_task("computing")
        N = getTotalDocs(word_count_dict)
        time.sleep(1)  # Simulate computation time

    print(f"[bold blue]Total Documents: {N}[/bold blue]\n")
    # display the MapIndex banner
    display_banner(console)

    # start the interactive search
    interactive_search(inverted_index, N, word_count_dict)

if __name__ == "__main__":
    main()
