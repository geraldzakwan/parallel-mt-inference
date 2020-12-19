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
parser.add_argument("--run_id", type=int, help="id to differ from other runs with the same parameters")

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

    results_dir = "data/results/{}-{}/{}/{}".format(args.source_lang, args.target_lang, args.num_chunks, args.run_id)

    source_doc = ""
    target_doc = ""

    for i in range(0, args.num_chunks):
        with open(os.path.join(results_dir, "translation_{}.txt".format(i)), "r") as infile:
            source_doc = source_doc + " " + infile.read()

        with open(os.path.join(results_dir, "reference_{}.txt".format(i)), "r") as infile:
            target_doc = target_doc + " " + infile.read()

    bleu_score = compute_average_blue_score(target_doc, [source_doc])

    with open(os.path.join(results_dir, "bleu_score.txt"), "w") as outfile:
        outfile.write(str(bleu_score) + "\n")
