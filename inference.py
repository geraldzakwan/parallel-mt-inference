import os
import string
import argparse

import requests
# import urllib
# from urllib.request import urlretrieve

import  nltk.translate.bleu_score as bleu

from config import *

parser = argparse.ArgumentParser()
parser.add_argument("--source_lang", type=str, help="source language code")
parser.add_argument("--target_lang", type=str, help="target language code")
parser.add_argument("--num_chunks", type=int, help="number of chunks")
parser.add_argument("--url", type=str, help="service endpoint")

def preprocess_sentence(sentence):
    sentence = sentence.strip("\n")
    # sentence = sentence.translate(str.maketrans("", "", string.punctuation))

    return sentence

def compute_average_blue_score(reference_translation, candidate_translations):
    cumulative_blue_score = 0

    for candidate_translation in candidate_translations:
        cumulative_bleu_score += bleu.sentence_bleu(
            reference_translation, candidate_translation)

    return cumulative_bleu_score / len(candidate_translations)

def generate_chunks(doc, num_chunks):
    sentence_chunks = []
    appended_sentence = ""

    for i, sentence in enumerate(doc):
        appended_sentence = appended_sentence + " " + sentence

        if (i + 1) % num_chunks == 0:
            sentence_chunks.append(appended_sentence)
            appended_sentence = ""

    return sentence_chunks

def send_request(url, text, source_lang, target_lang, id):
    payload = {
        "text": text,
        "source": source_lang,
        "target": target_lang,
        "id": id,
    }

    print(payload)

    resp = requests.post(url, json=payload)

    return resp

def run_experiment(source_doc, target_doc, source_lang, target_lang, num_chunks, url):
    source_doc_chunks = generate_chunks(source_doc, num_chunks)
    target_doc_chunks = generate_chunks(target_doc, num_chunks)

    for i in range(0, len(source_doc_chunks)):
        source_chunk = source_doc_chunks[i]
        target_chunk = target_doc_chunks[i]

        print(source_chunk)
        print(target_chunk)

        resp = send_request(url, source_chunk, source_lang, target_lang, i)

        print(resp.json())

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
            source_sentences = []

            for line in infile:
                source_sentences.append(preprocess_sentence(line))

            source_docs.append(source_sentences)

    for target_file in target_files:
        with open(os.path.join(target_corpus_dir, target_file), "r") as infile:
            target_sentences = []

            for line in infile:
                target_sentences.append(preprocess_sentence(line))

            target_docs.append(target_sentences)

    for i in range(0, len(source_docs)):
        run_experiment(source_docs[i],
            target_docs[i],
            args.source_lang,
            args.target_lang,
            args.num_chunks,
            args.url,
        )
