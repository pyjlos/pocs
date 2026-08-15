FROM nvcr.io/nvidia/tritonserver:24.08-py3

RUN pip install --no-cache-dir uv

COPY docker/triton-requirements.txt /tmp/triton-requirements.txt
RUN uv pip install --system --no-cache -r /tmp/triton-requirements.txt

# Bake model weights into the image so pods don't hit Hugging Face Hub at
# container startup (no cold-start latency, no runtime egress dependency).
COPY docker/prefetch_models.py /tmp/prefetch_models.py
RUN python3 /tmp/prefetch_models.py
