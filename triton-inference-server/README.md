# Triton Inference Server POC

Serves three Hugging Face models behind NVIDIA Triton Inference Server, fronted
by a FastAPI gateway that exposes one generic endpoint for all of them.

## Architecture

- **Triton** (`model_repo/`) — one directory per model, each with its own
  `config.pbtxt` (tensor I/O contract) and `model.py` (Python backend wrapping
  a `transformers.pipeline`):
  - `text_classification` — `distilbert-base-uncased-finetuned-sst-2-english`
  - `question_answering` — `distilbert-base-cased-distilled-squad`
  - `translation` — `Helsinki-NLP/opus-mt-en-fr`
- **API** (`api/`) — FastAPI gateway with a single `POST /infer` endpoint.
  Request/response use a generic `{"task": ..., "input"/"output": {...}}`
  envelope; an adapter per task translates that envelope to/from each model's
  specific Triton tensor contract.

## Prerequisites

- Docker + Docker Compose
- Internet access at *build* time — `docker/prefetch_models.py` downloads all
  three models' weights into the image during `docker build`, so containers
  never hit Hugging Face Hub at runtime (no cold-start latency, no egress
  dependency — this is what makes the image viable on EKS)

## Run

```bash
docker compose up --build
```

First build is slow — it builds the `triton` image (installs `transformers`,
`torch`, `sentencepiece` via `uv`, then bakes in all three models' weights).
Container startup after that is fast, since weights are already in the
image. Wait for log lines like:

```
| text_classification  | 1  | READY |
| question_answering   | 1  | READY |
| translation           | 1  | READY |
```

The API is then available at `http://localhost:8080`. Triton itself listens
on `8000` (HTTP), `8001` (gRPC), `8002` (metrics).

## Usage

All requests go through `POST /infer`:

```bash
curl -X POST localhost:8080/infer -H 'Content-Type: application/json' \
  -d '{"task":"classify","input":{"text":"I love this product"}}'
# {"task":"classify","output":{"label":"POSITIVE","score":0.999...}}

curl -X POST localhost:8080/infer -H 'Content-Type: application/json' \
  -d '{"task":"answer","input":{"question":"What is Triton?","context":"Triton is an inference server."}}'
# {"task":"answer","output":{"answer":"an inference server","score":0.9...}}

curl -X POST localhost:8080/infer -H 'Content-Type: application/json' \
  -d '{"task":"translate","input":{"text":"Hello, how are you?"}}'
# {"task":"translate","output":{"translation":"Bonjour, comment allez-vous ?"}}
```

Note: `question_answering` is extractive — it can only return a span of text
that already exists in `context`. If the answer isn't literally in the
context, expect a low `score` rather than a wrong-but-confident answer.

## Adding another model

1. `model_repo/<name>/config.pbtxt` — define the tensor input/output contract.
2. `model_repo/<name>/1/model.py` — `TritonPythonModel` wrapping whatever
   `transformers.pipeline` (or other logic) the model needs.
3. `docker/prefetch_models.py` — add the same `pipeline(...)` call so its
   weights get baked into the image at build time too.
4. `api/triton_client.py` — add a method that calls the new model via
   `tritonclient` and returns a plain dict.
5. `api/main.py` — add one entry to `ADAPTERS` and add the task name to the
   `Task` literal.

Rebuild with `docker compose up --build` (rebuilding is required whenever
`docker/triton-requirements.txt` or `docker/prefetch_models.py` changes —
Docker's layer cache otherwise serves a stale image).

Note: model names live in two places — `docker/prefetch_models.py` and each
model's `model.py`. If they drift, the worst case is that one model silently
falls back to a runtime download instead of failing outright.

## Troubleshooting

- **A model shows `UNAVAILABLE` in the Triton startup log** — check for a
  missing Python dependency (e.g. `sentencepiece` for Marian-based
  tokenizers) and add it to `docker/triton-requirements.txt`, then rebuild.
- **Whole `triton` container exits after one model fails to load** — this is
  Triton's default `strict_readiness` behavior: it won't serve *any* model if
  *any* model fails to load. Fix the failing model, or pass
  `--exit-on-error=false` to `tritonserver` in `docker-compose.yml` to serve
  the models that did load.
