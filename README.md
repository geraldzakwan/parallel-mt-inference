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

Same as previous.

### Run Parallel Inference

Run the command below.

```
python3 inference.py --source_lang en --target_lang fr --num_chunks 2 --url http://0.0.0.0:5000/translate
```

Specify your source and target language in the param `source_lang` and `target_lang` respectively.

Specify `num_chunks`, i.e. the number of document splits.
For example, `--num_chunks 2` will split your document into two smaller
documents with the same number of sentences each.

Specify `url`, i.e. the service endpoint where you hosted your web app.
If you run it locally, you don't need to change it.

You will have outputs like below.

```
results
  en-fr
    2
      elapsed_time.txt (How long the inference takes)
      reference_0.txt (Chunk 0 of your target document)
      reference_1.txt (Chunk 1 of your target document)
      translation_0.txt (Chunk 0 of your translated source document)
      translation_1.txt (Chunk 1 of your translated source document)
```

You can compare the inference time by looking at the `elapsed_time.txt` file in each corresponding directory.

### Run Evaluation

Finally, you should evaluate the translation result to see if the number of chunks affect translation quality.
Currently, this project only supports `BLEU` metric.

Run the command below.

```
python3 evaluate.py --eval_metric bleu --source_lang en --target_lang fr --num_chunks 2
```

Set `eval_metric` to `bleu` and the rest of the parameters are the same as previous, except you remove the `url`.

Now, your directory will have one more file, `bleu_score.txt`.

```
results
  en-fr
    2
      bleu_score.txt (The BLEU score for this inference scenario)
      elapsed_time.txt (How long the inference takes)
      reference_0.txt (Chunk 0 of your target document)
      reference_1.txt (Chunk 1 of your target document)
      translation_0.txt (Chunk 0 of your translated source document)
      translation_1.txt (Chunk 1 of your translated source document)
```

You can compare the `bleu` score for each inference scenario, i.e. differing `num_chunks`, by looking at `bleu_score.txt`.
