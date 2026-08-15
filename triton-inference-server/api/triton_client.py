import numpy as np
import tritonclient.http as httpclient


def _string_tensor(name: str, value: str) -> httpclient.InferInput:
    tensor = httpclient.InferInput(name, [1, 1], "BYTES")
    tensor.set_data_from_numpy(np.array([[value.encode("utf-8")]], dtype=np.object_))
    return tensor


class TritonClient:
    def __init__(self, url: str):
        self.client = httpclient.InferenceServerClient(url=url)

    def classify(self, text: str) -> dict:
        inputs = [_string_tensor("TEXT", text)]
        outputs = [httpclient.InferRequestedOutput("LABEL"), httpclient.InferRequestedOutput("SCORE")]
        result = self.client.infer("text_classification", inputs=inputs, outputs=outputs)
        label = result.as_numpy("LABEL")[0][0].decode("utf-8")
        score = float(result.as_numpy("SCORE")[0][0])
        return {"label": label, "score": score}

    def answer(self, question: str, context: str) -> dict:
        inputs = [_string_tensor("QUESTION", question), _string_tensor("CONTEXT", context)]
        outputs = [httpclient.InferRequestedOutput("ANSWER"), httpclient.InferRequestedOutput("SCORE")]
        result = self.client.infer("question_answering", inputs=inputs, outputs=outputs)
        answer = result.as_numpy("ANSWER")[0][0].decode("utf-8")
        score = float(result.as_numpy("SCORE")[0][0])
        return {"answer": answer, "score": score}

    def translate(self, text: str) -> dict:
        inputs = [_string_tensor("TEXT", text)]
        outputs = [httpclient.InferRequestedOutput("TRANSLATION")]
        result = self.client.infer("translation", inputs=inputs, outputs=outputs)
        translation = result.as_numpy("TRANSLATION")[0][0].decode("utf-8")
        return {"translation": translation}
