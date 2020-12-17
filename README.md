# Machine Translation Service
A Flask-based API containing the Helsinki NLP models from HuggingFace.

Reference: `[Huggingface Transformers library](https://huggingface.co/Helsinki-NLP)`

## How to Use the API

### Download the Machine Translation (MT) Model

First, make a directory called `data` and download a specific MT model using the command below.
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

### Run the App

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

### Create a Directory
