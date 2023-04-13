from tqdm.auto import tqdm
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import json
from pprint import pprint
import urllib.parse


tokenizer = tiktoken.encoding_for_model('gpt-3.5-turbo')
# tokenizer = tiktoken.get_encoding('cl100k_base')
def tiktoken_len(text):
    tokens = tokenizer.encode(
        text,
        disallowed_special=()
    )
    return len(tokens)


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,  # number of tokens overlap between chunks
    length_function=tiktoken_len,
    separators=['\n\n', '\n', ' ', '']
)


def main():
    # Get the courses from the file
    courses = retreive_courses()
    m = hashlib.md5()
    documents = []

    for course in tqdm(courses):
        # Convert URL into unique ID
        url = course['metadata']['source']
        print(url)
        m.update(url.encode('utf-8'))
        uid = m.hexdigest()[:12]

        # Build chunks w/ prefix
        chunks = text_splitter.split_text(course['page_content'])
        course_name = urllib.parse.unquote(url.split('/')[-2])
        prefix = 'Description of course ' + course_name + ': \n'      
        for i in range(len(chunks)):
            chunks[i] = prefix + chunks[i]
        
        # Format chunks
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': f'{uid}-{i}',
                'text': chunk,
                'metadata': { 'url': url }
            })

    # len(documents)
    # pprint(documents)
    save_documents(documents)


def retreive_courses():
    with open('course_contents.json', 'r') as file:
        courses = json.load(file)
        return courses


def save_documents(documents):
    # Compatible with Hugging Face's datasets
    with open('train.jsonl', 'w') as f:
        for doc in documents:
            f.write(json.dumps(doc) + '\n')


if __name__ == '__main__':
    main()
