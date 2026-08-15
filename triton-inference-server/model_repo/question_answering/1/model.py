import numpy as np
import triton_python_backend_utils as pb_utils
from transformers import pipeline


class TritonPythonModel:
    def initialize(self, args):
        self.pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad",
        )

    def execute(self, requests):
        responses = []
        for request in requests:
            question_tensor = pb_utils.get_input_tensor_by_name(request, "QUESTION")
            context_tensor = pb_utils.get_input_tensor_by_name(request, "CONTEXT")

            questions = [q.decode("utf-8") for q in question_tensor.as_numpy().flatten()]
            contexts = [c.decode("utf-8") for c in context_tensor.as_numpy().flatten()]

            results = [
                self.pipeline(question=q, context=c) for q, c in zip(questions, contexts)
            ]

            answers = np.array([[r["answer"].encode("utf-8")] for r in results], dtype=np.object_)
            scores = np.array([[r["score"]] for r in results], dtype=np.float32)

            answer_tensor = pb_utils.Tensor("ANSWER", answers)
            score_tensor = pb_utils.Tensor("SCORE", scores)
            responses.append(pb_utils.InferenceResponse(output_tensors=[answer_tensor, score_tensor]))
        return responses
