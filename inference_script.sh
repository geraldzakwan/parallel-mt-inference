# Param 1: source_lang
# Param 2: target_lang
# Param 3: num_chunks
# Param 4: multiple_of
# Param 5: url
# Param 6: eval_metric
# Param 7: repetition

echo Deleting previously created result directory if any
rm -rf data/results/"$1"-"$2"/"$3"

echo Creating new result directory
mkdir data/results/"$1"-"$2"/"$3"

for (( i=1; i<=$7; i++ )); do
  echo Repetition: "$i"

  echo Creating directory to store the result from current repetition
  mkdir data/results/"$1"-"$2"/"$3"/"$i"

  echo Running inference script
  python3 inference.py --source_lang "$1" --target_lang "$2" --num_chunks "$3" --run_id "$i" --multiple_of "$4" --url "$5"
done;
