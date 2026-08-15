import os
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from triton_client import TritonClient

app = FastAPI(title="Triton POC API")
client = TritonClient(url=os.environ.get("TRITON_URL", "localhost:8000"))

# Each adapter owns translating the generic envelope's "input" dict into
# whatever a given model actually needs, and normalizing its raw response
# back into a plain dict for the "output" envelope. Adding a model means
# adding one entry here — the envelope shape never changes.
ADAPTERS = {
    "classify": lambda input: client.classify(input["text"]),
    "answer": lambda input: client.answer(input["question"], input["context"]),
    "translate": lambda input: client.translate(input["text"]),
}

Task = Literal["classify", "answer", "translate"]


class InferRequest(BaseModel):
    task: Task
    input: dict


class InferResponse(BaseModel):
    task: Task
    output: dict


@app.post("/infer", response_model=InferResponse)
def infer(request: InferRequest):
    output = ADAPTERS[request.task](request.input)
    return InferResponse(task=request.task, output=output)
