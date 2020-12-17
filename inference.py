import os
import string
import argparse

import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from timeit import default_timer

import  nltk.translate.bleu_score as bleu

from config import *

parser = argparse.ArgumentParser()
parser.add_argument("--source_lang", type=str, help="source language code")
parser.add_argument("--target_lang", type=str, help="target language code")
parser.add_argument("--num_chunks", type=int, help="number of chunks")
parser.add_argument("--url", type=str, help="service endpoint")

START_TIME = default_timer()
DEBUG = True

def preprocess_doc_to_sents(doc):
    doc = doc.translate(str.maketrans("", "", "\n"))

    return doc.split(".")

def compute_average_blue_score(reference_translation, candidate_translations):
    cumulative_blue_score = 0

    for candidate_translation in candidate_translations:
        cumulative_bleu_score += bleu.sentence_bleu(
            reference_translation, candidate_translation)

    return cumulative_bleu_score / len(candidate_translations)

def generate_chunks(doc, num_chunks):
    chunk_size = len(doc) // num_chunks

    sentence_chunks = []
    appended_sentence = ""

    for i, sentence in enumerate(doc):
        appended_sentence = appended_sentence + " " + sentence

        if (i + 1) % chunk_size == 0:
            sentence_chunks.append(appended_sentence)
            appended_sentence = ""

    return sentence_chunks

def send_request(url, text, source_lang, target_lang, chunk_num):
    payload = {
        "text": text,
        "source": source_lang,
        "target": target_lang,
        "chunk_num": chunk_num,
    }

    if DEBUG:
        print("REQUEST")
        print(payload)
        print("-"*50)

    resp = requests.post(url, json=payload)

    return resp

def run_experiment(source_doc, target_doc, source_lang, target_lang, num_chunks, url):
    source_doc_chunks = generate_chunks(source_doc, num_chunks)
    target_doc_chunks = generate_chunks(target_doc, num_chunks)

    for i in range(0, len(source_doc_chunks)):
        source_chunk = source_doc_chunks[i]
        target_chunk = target_doc_chunks[i]

        if DEBUG:
            print("CHUNK NUMBER")
            print(i)
            print("-"*50)
            print("SOURCE CHUNK")
            print(source_chunk)
            print("-"*50)
            print("TARGET CHUNK")
            print(target_chunk)
            print("-"*50)

        resp = send_request(url, source_chunk, source_lang, target_lang, i)

        if DEBUG:
            print("RESPONSE")
            print(resp.json())
            print("-"*50)

# def fetch(session, csv):
#     base_url = "https://people.sc.fsu.edu/~jburkardt/data/csv/"
#     with session.get(base_url + csv) as response:
#         data = response.text
#         if response.status_code != 200:
#             print("FAILURE::{0}".format(url))
#
#         elapsed = default_timer() - START_TIME
#         time_completed_at = "{:5.2f}s".format(elapsed)
#         print("{0:<30} {1:>20}".format(csv, time_completed_at))
#
#         return data
#
# async def get_data_asynchronous():
#     csvs_to_fetch = [
#         "ford_escort.csv",
#         "cities.csv",
#         "hw_25000.csv",
#         "mlb_teams_2012.csv",
#         "nile.csv",
#         "homes.csv",
#         "hooke.csv",
#         "lead_shot.csv",
#         "news_decline.csv",
#         "snakes_count_10000.csv",
#         "trees.csv",
#         "zillow.csv"
#     ]
#     print("{0:<30} {1:>20}".format("File", "Completed at"))
#     with ThreadPoolExecutor(max_workers=10) as executor:
#         with requests.Session() as session:
#             # Set any session parameters here before calling `fetch`
#             loop = asyncio.get_event_loop()
#             START_TIME = default_timer()
#             tasks = [
#                 loop.run_in_executor(
#                     executor,
#                     fetch,
#                     *(session, csv) # Allows us to pass in multiple arguments to `fetch`
#                 )
#                 for csv in csvs_to_fetch
#             ]
#             for response in await asyncio.gather(*tasks):
#                 pass

if __name__ == "__main__":
    args = parser.parse_args()

    corpus_dir = "data/parallel-corpus/{}/corpus/".format(
        args.source_lang + "-" + args.target_lang
    )

    source_corpus_dir = corpus_dir + args.source_lang
    target_corpus_dir = corpus_dir + args.target_lang

    source_files = os.listdir(source_corpus_dir)
    target_files = os.listdir(target_corpus_dir)

    source_docs = []
    target_docs = []

    for source_file in source_files:
        with open(os.path.join(source_corpus_dir, source_file), "r") as infile:
            source_docs.append(preprocess_doc_to_sents(infile.read()))

    for target_file in target_files:
        with open(os.path.join(target_corpus_dir, target_file), "r") as infile:
            target_docs.append(preprocess_doc_to_sents(infile.read()))

    for i in range(0, len(source_docs)):
        run_experiment(
            source_docs[i],
            target_docs[i],
            args.source_lang,
            args.target_lang,
            args.num_chunks,
            args.url,
        )

    # loop = asyncio.get_event_loop()
    # future = asyncio.ensure_future(get_data_asynchronous())
    # loop.run_until_complete(future)
