from tqdm.auto import tqdm
import hashlib
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken
import json
from pprint import pprint
# tiktoken.encoding_for_model('gpt-3.5-turbo')
# Tokenizer used for gpt-3.5-turbo
tokenizer = tiktoken.get_encoding('cl100k_base')

# create the length function
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

    # print(courses[0])
    # chunks = text_splitter.split_text(courses[0]["page_content"])
    # print(len(chunks))
    # print("Chunk 0", chunks[0])
    # print("Chunk 1", chunks[1])
    # print(tiktoken_len(chunks[0]), tiktoken_len(chunks[1]))
    # return


    m = hashlib.md5()  # this will convert URL into unique ID

    documents = []

    for course in tqdm(courses):
        url = course["metadata"]['source']
        m.update(url.encode('utf-8'))
        uid = m.hexdigest()[:12]
        chunks = text_splitter.split_text(course["page_content"])
        for i, chunk in enumerate(chunks):
            documents.append({
                'id': f'{uid}-{i}',
                'text': chunk,
                'source': url
            })

    len(documents)
    pprint(documents)


def retreive_courses():
    with open("course_contents.json", "r") as file:
        courses = json.load(file)
        return courses
    

if __name__ == '__main__':
    main()
