import os
import string
import argparse

DEBUG = False

parser = argparse.ArgumentParser()
parser.add_argument("--source_lang", type=str, help="source language code")
parser.add_argument("--target_lang", type=str, help="target language code")

if __name__ == "__main__":
    args = parser.parse_args()

    results_dir = "data/results/{}-{}".format(args.source_lang, args.target_lang)

    num_chunks_list = os.listdir(results_dir)
    num_chunks_list.remove(".DS_Store")
    num_chunks_list = sorted([int(n_c) for n_c in num_chunks_list])

    for num_chunks in num_chunks_list:
        curr_num_chunk_dir = os.path.join(results_dir, str(num_chunks))

        avg_elapsed_time = 0

        for run_id in os.listdir(curr_num_chunk_dir):
            curr_result_dir = os.path.join(curr_num_chunk_dir, run_id)

            with open(os.path.join(curr_result_dir, "elapsed_time.txt"), "r") as infile:
                avg_elapsed_time += float(infile.read().strip("\n"))

        avg_elapsed_time = avg_elapsed_time / len(os.listdir(results_dir))

        with open(os.path.join(curr_num_chunk_dir, "bleu_score.txt"), "r") as infile:
            bleu_score = float(infile.read().strip("\n"))

        print("Summary")
        print("-"*50)
        print("source_lang: {}".format(args.source_lang))
        print("target_lang: {}".format(args.target_lang))
        print("num_chunks: {}".format(num_chunks))
        print("-"*50)
        print("Average elapsed time over {} runs: {:.2f} seconds".format(len(os.listdir(results_dir)), avg_elapsed_time))
        print("-"*50)
        print("BLEU score: {:.4f}".format(bleu_score))
        print("-"*50)
