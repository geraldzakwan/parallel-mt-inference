# Machine Translation Service
A Flask-based API containing the Helsinki NLP models from HuggingFace.

Reference: `[Huggingface Transformers library](https://huggingface.co/Helsinki-NLP)`

## How to Use the API

### Download the Machine Translation (MT) Model

First, make a directory called `data` in `root` and download a specific MT model using the command below.
The example provided is for `English (en)` to `French (fr)` MT model.

```
mkdir data
python3 download_models.py --source en --target fr
```

If you want to store it anywhere else, specify the `MODEL_PATH` in `config.py` accordingly.

### Install Requirements

Use `Python>=3.6` and run the command below.

```
pip install -r requirements.txt
```

Note that I use `PyTorch CPU` in the requirement file.
Change it accordingly if you want to use `PyTorch GPU`.

### Run the Web App

You can either run the app directly using `Python3`:

```
python app.py
```

or you can run it using `Docker` by building the image and running a container:

```
docker build -t mt-service .
docker run -p 5000:5000 -v /path/to/models:/app/data -it mt-service
```

### Accessing the App

The web app should be hosted at `http://localhost:5000`

You can hit the API using the following `curl` command:

```
curl --location --request POST 'http://localhost:5000/translate' \
  --header 'Content-Type: application/json' \
  --data-raw '{
   "source": "en",
   "target": "fr",
   "text": "Hello, my name is Geraldi Dzakwan. I am a final year master's student at Columbia University. My interests are football, tech (particularly Machine Learning) and comedy."
   "chunk_num": 0,
}'
```

You can ignore the `chunk_num` for now, just set it to `0`.

You could then expect the following response:

```
{
    "data": {
        "chunk_num": 0,
        "text": [
            "Bonjour, je m'appelle Geraldi Dzakwan. Je suis une étudiante de dernière année à la maîtrise à l'Université Columbia. Mes intérêts sont le football, la technologie (en particulier Machine Learning) et la comédie."
        ]
    }
}
```

## How to Run Parallel Inference Experiment

### Set Up Directory Structure

First, make a directory called `results` in `root`.

If you want to conduct an experiment using `en-fr` MT model, then
create another directory called `en-fr` inside `results` directory.

### Set Up Your Dataset

If you use `en-fr` MT model, put your dataset inside the `data/parallel-corpus/en-fr` directory.
You should have two documents: `source.txt` in English and `target.txt` in French.
Your directory should look like below.

```
results
  en-fr
    source.txt
    target.txt
```

I put sample documents (source.txt and target.txt) for `en-fr`, please refer to them for document format.

### Run the Web App

This time around, we will use `gunicorn` so that we can spawn multiple Flask app instances.

Run the command below instead in the `root` directory.

```
gunicorn app:app --workers 4 --bind localhost:5000 --timeout 3600
```

Big number of `workers` may cause the program to crash since the MT model is quite big.

Set `timeout` for a quite long duration, i.e. 1 hour (3600 seconds).

### Run Parallel Inference

Run the command below.

```
python3 inference.py --source_lang en --target_lang fr --num_chunks 2 --run_id 1 --multiple_of 32 --url http://localhost:5000/translate
```

Specify your source and target language in the param `source_lang` and `target_lang` respectively.

Specify `num_chunks`, i.e. the number of document splits.
For example, `--num_chunks 2` will split your document into two smaller
documents with the same number of sentences each.

Specify `url`, i.e. the service endpoint where you hosted your web app.
If you run it locally, you don't need to change it.

You can ignore the `run_id` for now, just set it to `1`.

You can ignore the `multiple_of` as well for now, just set it to `32`.

You will have outputs like below.

```
results
  en-fr (source_lang - target_lang)
    2 (num_chunks)
      1 (run_id)
        elapsed_time.txt (How long the inference takes)
        reference_0.txt (Chunk 0 of your target document)
        reference_1.txt (Chunk 1 of your target document)
        translation_0.txt (Chunk 0 of your translated source document)
        translation_1.txt (Chunk 1 of your translated source document)
```

You can compare the inference time by looking at the `elapsed_time.txt` file in each corresponding directory.

### Run Parallel Inference Many Times

To get more accurate `elapsed_time` data, we can run the inference many times.

To do this, use the `inference_script.sh`.

First, run `chmod +x inference_script.sh` to give permission to the script.

Then, run the command below.

```
./inference_script.sh en fr 2 32 http://localhost:5000/translate 10
```

Where:

1. Param 1 is the `source_lang`, e.g. `en`
2. Param 2 is the `target_lang`, e.g. `fr`
3. Param 3 is the `num_chunks`, e.g. `2`
4. Param 4 is the `multiple_of`, e.g. `32`
5. Param 5 is the `url`, e.g. `http://localhost:5000/translate`
6. Param 6 is the `repetition`, e.g. `10`

`multiple_of` is used to make sure that the number of sentences is divisible by `multiple_of`.

Because in my experiment, I use `1, 2, 4, 8, 16 and 32` `num_chunks`, then I need to make sure
that the number of sentences are divisible by `32`, by reducing them to the nearest multiplier of `32`.

This way, we can allocate each chunk with the same number of sentences.

### Run Evaluation

Finally, you should evaluate the translation result to see if the number of chunks affect translation quality.
Currently, this project only supports `BLEU` metric.

Run the command below.

```
python3 evaluate.py --source_lang en --target_lang fr --num_chunks 2 --eval_metric bleu
```

Set `eval_metric` to `bleu` and the rest of the parameters are the same as previous, except you remove the `url`.

Or alternatively, you could also use the `evaluation_script.sh`.

First, run `chmod +x evaluation_script.sh` to give permission to the script.

Then, run the command below.

```
./evaluation_script.sh en fr 2 bleu
```

Where:

1. Param 1 is the `source_lang`, e.g. `en`
2. Param 2 is the `target_lang`, e.g. `fr`
3. Param 3 is the `num_chunks`, e.g. `2`
4. Param 4 is the `eval_metric`, e.g. `bleu`

Now, your directory will have one more file, `bleu_score.txt`.

```
results
  en-fr (source_lang - target_lang)
    2 (num_chunks)
      bleu_score.txt (The BLEU score for this inference scenario)
      1 (run_id)
        elapsed_time.txt (How long the inference takes)
        reference_0.txt (Chunk 0 of your target document)
        reference_1.txt (Chunk 1 of your target document)
        translation_0.txt (Chunk 0 of your translated source document)
        translation_1.txt (Chunk 1 of your translated source document)
```

You can compare the `bleu` score for each inference scenario, i.e. differing `num_chunks`, by looking at `bleu_score.txt`.

Note that we have only one `bleu_score` even though we run multiple times.
This is because the `bleu_score` will be the same and will only differ if we change the `num_chunks`.

### Summarize Experiment

Rather than going to each output file to compute average elapsed time and the `BLEU` score,
I provide a script to handle that.

Run the command below.

```
python3 summarize.py --source_lang en --target_lang fr
```

Or alternatively, you could also use the `summarize_script.sh`.

First, run `chmod +x summarize_script.sh` to give permission to the script.

Then, run the command below.

```
./summarize_script.sh en fr
```

Where:

1. Param 1 is the `source_lang`, e.g. `en`
2. Param 2 is the `target_lang`, e.g. `fr`

You should see the average `elapsed_time` and `bleu_score` for each `num_chunks` scenario,
in my case there would be 6 summaries: `1, 2, 4, 8, 16, 32` chunks.
