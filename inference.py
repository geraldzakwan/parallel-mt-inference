import os
import string
import argparse

import urllib
from urllib.request import urlretrieve

from config import *

parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, help="source language code")
parser.add_argument("--target", type=str, help="target language code")

def preprocess_sentence(sentence):
    sentence = sentence.strip("\n")
    sentence = sentence.translate(str.maketrans("", "", string.punctuation))

    return sentence

if __name__ == "__main__":
    args = parser.parse_args()

    corpus_dir = "data/parallel-corpus/{}/corpus/".format(
        args.source + "-" + args.target
    )

    source_corpus_dir = corpus_dir + args.source
    target_corpus_dir = corpus_dir + args.target

    source_files = os.listdir(source_corpus_dir)
    target_files = os.listdir(target_corpus_dir)

    source_sentences = []
    target_sentences = []

    for source_file in source_files:
        with open(os.path.join(source_corpus_dir, source_file), "r") as infile:
            for line in infile:
                source_sentences.append(preprocess_sentence(line))

    for target_file in target_files:
        with open(os.path.join(target_corpus_dir, target_file), "r") as infile:
            for line in infile:
                target_sentences.append(preprocess_sentence(line))

    print(len(target_sentences))
    print(len(source_sentences))
