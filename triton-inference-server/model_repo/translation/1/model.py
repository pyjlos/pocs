import numpy as np
import triton_python_backend_utils as pb_utils
from transformers import pipeline


class TritonPythonModel:
    def initialize(self, args):
        self.pipeline = pipeline(
            "translation_en_to_fr",
            model="Helsinki-NLP/opus-mt-en-fr",
            revision="dd7f6540a7a48a7f4db59e5c0b9c42c8eea67f18",
        )

    def execute(self, requests):
        responses = []
        for request in requests:
            text_tensor = pb_utils.get_input_tensor_by_name(request, "TEXT")
            texts = [t.decode("utf-8") for t in text_tensor.as_numpy().flatten()]

            results = self.pipeline(texts)

            translations = np.array(
                [[r["translation_text"].encode("utf-8")] for r in results], dtype=np.object_
            )

            translation_tensor = pb_utils.Tensor("TRANSLATION", translations)
            responses.append(pb_utils.InferenceResponse(output_tensors=[translation_tensor]))
        return responses
