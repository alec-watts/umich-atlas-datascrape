import os
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter, Retry
from tqdm.auto import tqdm
import json
import argparse

load_dotenv()

bearer_token = os.getenv('BEARER_TOKEN')
headers = {
    'Authorization': f'Bearer {bearer_token}'
}
endpoint_url = 'https://umich-chatgpt-plugin.onrender.com'

def upload():
    batch_size = 100
    print('Uploading documents...')
    documents = load_documents()
    s = requests.Session()

    retries = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[ 500, 502, 503, 504 ]
    )

    s.mount('https://', HTTPAdapter(max_retries=retries))

    for i in tqdm(range(0, len(documents), batch_size)):
        i_end = min(i + batch_size, len(documents))
        print(i_end)
        # make post request that allows up to 5 retries
        response = s.post(
            f'{endpoint_url}/upsert',
            headers=headers,
            json={
                'documents': documents[i:i_end]
            }
        )
        # print(response)


def load_documents():
    documents = []
    with open('train.jsonl', 'r') as file:
        for line in file:
            documents.append(json.loads(line))
        return documents
    

def test_queries():
    print('Testing queries...')
    queries = [
        {'query': 'I need a class with an A average that fullfills my upper level computer science requirements'},
        {'query': 'I want a 4 credit computer science class on mondays and wednesday around 2pm'},
        {'query': 'Give me a course with a low workload'}
    ]

    response = requests.post(
        f'{endpoint_url}/query',
        headers=headers,
        json={
            'queries': queries
        }
    )

    for query_result in response.json()['results']:
        query = query_result['query']
        answers = []
        scores = []
        for result in query_result['results']:
            answers.append(result['text'])
            scores.append(round(result['score'], 2))
        print('-'*70+'\n' + query + '\n\n' + '\n'.join([f'{s}: {a}' for a, s in zip(answers, scores)]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--upload', action='store_true')
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()

    if args.upload:
        upload()
    if args.test:
        test_queries()

