# Param 1: source_lang
# Param 2: target_lang

echo Running summarization script
python3 summarize.py --source_lang "$1" --target_lang "$2"
