# Param 1: source_lang
# Param 2: target_lang
# Param 3: num_chunks
# Param 4: eval_metric

echo Running evaluation script
python3 evaluation.py --source_lang "$1" --target_lang "$2" --num_chunks "$3" --eval_metric "$4"
