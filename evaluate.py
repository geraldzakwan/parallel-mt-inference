import os
import string
import argparse

import nltk.translate.bleu_score as bleu

DEBUG = False
SUPPORTED_EVALUATION_METRIC = ["bleu"]

parser = argparse.ArgumentParser()
parser.add_argument("--eval_metric", type=str, help="evaluation metric")
parser.add_argument("--source_lang", type=str, help="source language code")
parser.add_argument("--target_lang", type=str, help="target language code")
parser.add_argument("--num_chunks", type=int, help="number of chunks")

def get_supported_eval_metric():
    supp_metric = "["

    for metric in SUPPORTED_EVALUATION_METRIC:
        supp_metric = supp_metric + metric + ", "

    return supp_metric[0:len(supp_metric)-2] + "]"

def compute_average_blue_score(reference_translation, candidate_translations):
    cumulative_bleu_score = 0

    for candidate_translation in candidate_translations:
        cumulative_bleu_score += bleu.sentence_bleu(
            reference_translation, candidate_translation)

    return cumulative_bleu_score / len(candidate_translations)

if __name__ == "__main__":
    args = parser.parse_args()

    if not args.eval_metric.lower() in SUPPORTED_EVALUATION_METRIC:
        raise Exception("Evaluation metric is not supported, choose one from: {}".format(get_supported_eval_metric()))

    result_dir = "data/result/{}-{}/{}".format(args.source_lang, args.target_lang, args.num_chunks)

    total_bleu_score = 0

    for i in range(0, args.num_chunks):
        with open(os.path.join(result_dir, "translation_{}.txt".format(i)), "r") as infile:
            source_doc_chunk = infile.read()

        with open(os.path.join(result_dir, "reference_{}.txt".format(i)), "r") as infile:
            target_doc_chunk = infile.read()

        total_bleu_score += compute_average_blue_score(target_doc_chunk, [source_doc_chunk])

    avg_blue_score = total_bleu_score / args.num_chunks

    with open(os.path.join(result_dir, "bleu_score.txt"), "w") as outfile:
        outfile.write(str(avg_blue_score) + "\n")
