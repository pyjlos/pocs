import numpy as np
import triton_python_backend_utils as pb_utils
from transformers import pipeline


class TritonPythonModel:
    def initialize(self, args):
        self.pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )

    def execute(self, requests):
        responses = []
        for request in requests:
            text_tensor = pb_utils.get_input_tensor_by_name(request, "TEXT")
            texts = [t.decode("utf-8") for t in text_tensor.as_numpy().flatten()]

            results = self.pipeline(texts)

            labels = np.array([[r["label"].encode("utf-8")] for r in results], dtype=np.object_)
            scores = np.array([[r["score"]] for r in results], dtype=np.float32)

            label_tensor = pb_utils.Tensor("LABEL", labels)
            score_tensor = pb_utils.Tensor("SCORE", scores)
            responses.append(pb_utils.InferenceResponse(output_tensors=[label_tensor, score_tensor]))
        return responses
