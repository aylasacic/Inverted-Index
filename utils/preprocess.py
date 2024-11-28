import os
import re
from tqdm import tqdm
import argparse

# create output directory if it does not exist
os.makedirs(output_dir, exist_ok=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Clean text documents by removing specific sections and formatting.")
    parser.add_argument(
        '-i', '--input_dir',
        type = str,
        default = "documents10k",
        help = 'Path to the input directory containing the documents to be cleaned. Default is "documents10k".'
    )
    parser.add_argument(
        '-o', '--output_dir',
        type = str,
        default = "cleaned_documents10k",
        help = 'Path to the output directory where cleaned documents will be saved. Default is "cleaned_documents10k".'
    )
    return parser.parse_args()

# function to clean a single file's content
def cleanText(text):
    # remove sections after specific headers
    text = re.split(r"==See also==", text, 1)[0]
    text = re.split(r"== References ==", text, 1)[0]
    text = re.split(r"== External links ==", text, 1)[0]
    
    # remove various types of headers
    text = re.sub(r"===.*?===", "", text)  
    text = re.sub(r"==.*?==", "", text)   
    
    # remove wikitables and html/xml tags
    text = re.sub(r"{\|.*?\|}", "", text, flags=re.DOTALL) 
    text = re.sub(r"<.*?>", "", text)                      
    
    # remove urls and specific patterns
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r"\bthumb\|.*?\|", "", text)
    text = re.sub(r"\b\d+px\b\s*\w*", "", text)  # removes numeric px| patterns and trailing content
    
    # replace escaped apostrophe and separate punctuation
    text = text.replace(r"\"", "\"")  
    text = re.sub(r"([.,*:;!?()|])", r" \1 ", text)  
    
    # remove newline characters
    text = text.replace("\n", " ").replace("\r", " ")
    
    # remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

def main():
    args = parse_arguments()
    input_dir = args.input_dir
    output_dir = args.output_dir

    # Check if input directory exists
    if not os.path.isdir(input_dir):
        print(f"Error: The input directory '{input_dir}' does not exist.")
        return

    # Create output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)

    # iterate through files in the input directory
    # tqdm for progress tracking to make sure everything is running
    for filename in tqdm(os.listdir(input_dir), desc="Processing files"):
        # get the file path 
        file_path = os.path.join(input_dir, filename)
        
        # open the file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # if file is empty, skip it
        if not lines:
            continue
        
        # rxtract the title line (strip trailing and leading wihtespace)
        title_line = lines[0].strip()
        
        # rnsure the title line starts with "Title: "
        if not title_line.startswith("Title: "):
            print(f"Warning: {filename} does not start with a title line.")
            # get the body text
            body_text = ''.join(lines)
            # clean it using the function above
            cleaned_body = cleanText(body_text)
            # get the final content
            final_content = cleaned_body
        else:
            # if it doesnt start as needed, process first line as title
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

    print(f"Processing complete. Cleaned files saved in {output_dir}")

if __name__ == "__main__":
    main()
