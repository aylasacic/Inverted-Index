
# Assignment 4: Inverted Index

## Author
Ajla Šačić

## Project Description
This project involves building an inverted index pipeline in several stages:
1. **Document Cleaning**:  
   - Removing subtitles (text surrounded by `=` symbols)  
   - Removing wikitables  
   - Removing references and 'see also' sections  
   - Removing any HTML and XML tags  
   - Separating punctuation connected to words  

2. **Document Merging**:  
   - Adding all files into a single file  
   - Formatting as `[filename.txt] [Title] [Content]`, all tab-separated  

3. **MapReduce for Word Counts**:  
   - Input: Combined file  
   - Output:  
     - `filename`  
     - `title`  
     - `target word`  
     - `target word frequency count`  
     - `all contexts related to the word`  

4. **Creating the Inverted Index**:  
   - Uses `pickle` to store a searchable dictionary of words.  

5. **Searching the Inverted Index**:  
   - Options for a simple or rich search UI.  

## How to Run the Search
### Simple Search (Simple UI):
```bash
python3 simpleSearch.py
```

### Rich Search (More Complex UI):
```bash
python3 richSearch.py
```

## How to Run the Project From Scratch
1. **Create a new environment**:
   ```bash
   python -m venv venv
   ```
   Activate the virtual environment:  
   - On Windows:  
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:  
     ```bash
     source venv/bin/activate
     ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the inverted index pipeline**:
   ```bash
   python3 processFiles.py --run_mapreduce --build_inverted_index
   ```

   Alternatively, execute each step separately:

   ### Step 3.1: Clean the documents
   ```bash
   python3 preprocess.py -i [--input_dir] INPUT_DIR -o [--output_dir] OUTPUT_DIR
   ```
   Output: Directory called `OUTPUT_DIR` containing cleaned files.

   ### Step 3.2: Combine the files into one
   ```bash
   python3 combine_files.py -i [--input_dir] INPUT_DIR -o [--output_file] OUTPUT_FILE
   ```
   Output: Single file `OUTPUT_FILE` containing all documents.

   ### Step 3.3: Run the MapReduce
   ```bash
   python3 mapReduceWordCount.py combined_documents.txt > word_counts.txt
   ```
   Output: `word_counts.txt` with word counts per file, including contexts.

   ### Step 3.4: Create the Inverted Index
   ```bash
   python3 invertedIndex.py --input_file word_counts.txt --output_file inverted_index.pkl
   ```

   ### Step 3.5: Get the total word count for each file
   ```bash
   python3 countWords.py -i [--input_dir] INPUT_DIR -o [--output_file] OUTPUT_FILE
   ```

4. **Run the Search**:
   - Simple UI:  
     ```bash
     python3 simpleSearch.py
     ```
   - Rich UI:  
     ```bash
     python3 richSearch.py
     ```
