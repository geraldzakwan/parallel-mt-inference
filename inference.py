import os
import time
import string
import argparse

import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor

from config import *

DEBUG = False

parser = argparse.ArgumentParser()
parser.add_argument("--source_lang", type=str, help="source language code")
parser.add_argument("--target_lang", type=str, help="target language code")
parser.add_argument("--num_chunks", type=int, help="number of chunks")
parser.add_argument("--multiple_of", type=int, help="num sentences should be divisible by")
parser.add_argument("--run_id", type=int, help="id to differ from other runs")
parser.add_argument("--url", type=str, help="service endpoint")

def preprocess_doc_to_sents(doc):
    doc = doc.translate(str.maketrans("", "", "\n"))

    return doc.split(".")

def generate_chunks(doc, num_chunks):
    chunk_size = len(doc) // num_chunks

    sentence_chunks = []
    appended_sentence = ""

    for i, sentence in enumerate(doc):
        appended_sentence = appended_sentence + sentence + ". "

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

async def run_experiment(source_doc_chunks, source_lang, target_lang, url):
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    send_request,
                    *(url, source_chunk, source_lang, target_lang, i)
                )
                for i, source_chunk in enumerate(source_doc_chunks)
            ]

            for resp in await asyncio.gather(*tasks):
                data = resp.json()["data"]

                chunk_num = data["chunk_num"]
                text = data["text"][0]

                if DEBUG:
                    print("RESPONSE CHUNK NUM")
                    print(chunk_num)
                    print("-"*50)
                    print(text)
                    print("-"*50)

                with open("data/results/{}-{}/{}/translation_{}.txt".format(source_lang, target_lang, len(source_doc_chunks), chunk_num), "w") as outfile:
                    outfile.write(text)

if __name__ == "__main__":
    args = parser.parse_args()

    corpus_dir = "data/parallel-corpus/{}/".format(
        args.source_lang + "-" + args.target_lang
    )

    with open(os.path.join(corpus_dir, "source.txt"), "r") as infile:
        source_doc = preprocess_doc_to_sents(infile.read())

    with open(os.path.join(corpus_dir, "target.txt"), "r") as infile:
        target_doc = preprocess_doc_to_sents(infile.read())

    clipped_length = len(source_doc)

    if len(source_doc) > len(target_doc):
        clipped_length = len(target_doc)

    if clipped_length % args.multiple_of > 0:
        clipped_length = (clipped_length // args.multiple_of) * args.multiple_of

    source_doc = source_doc[:clipped_length]
    target_doc = target_doc[:clipped_length]

    print("Using {} pairs of sentences".format(len(source_doc)))

    source_doc_chunks = generate_chunks(source_doc, args.num_chunks)
    target_doc_chunks = generate_chunks(target_doc, args.num_chunks)

    if DEBUG:
        print("SOURCE DOC CHUNKS")
        print(source_doc_chunks)
        print("-"*50)

        print("TARGET DOC CHUNKS")
        print(target_doc_chunks)
        print("-"*50)

    results_dir = "data/results/{}-{}/{}/{}".format(args.source_lang, args.target_lang, args.num_chunks, args.run_id)

    try:
        os.mkdir(results_dir)
    except:
        if DEBUG:
            print("results directory has been created")

    for i, target_doc in enumerate(target_doc_chunks):
        with open(os.path.join(results_dir, "reference_{}.txt".format(i)), "w") as outfile:
            outfile.write(target_doc)

    loop = asyncio.get_event_loop()

    future = asyncio.ensure_future(run_experiment(
        source_doc_chunks,
        args.source_lang,
        args.target_lang,
        args.url,
    ))

    start = time.time()

    loop.run_until_complete(future)

    elapsed_time = time.time() - start

    with open("data/results/{}-{}/{}/elapsed_time.txt".format(args.source_lang, args.target_lang, len(target_doc_chunks)), "w") as outfile:
        outfile.write(str(elapsed_time) + "\n")
