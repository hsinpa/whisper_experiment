from transformers import WhisperProcessor, WhisperForConditionalGeneration, ProcessorMixin, WhisperPreTrainedModel
from datasets import load_dataset
import numpy as np

class WhisperOperator:

    __processor: WhisperProcessor
    __model: WhisperPreTrainedModel
    def __init__(self):
        self.__processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
        self.__model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
        self.__model.config.forced_decoder_ids = None

    def process(self, sample_size: int, data: np.array):
        input_features = self.__processor(data, sampling_rate=sample_size, return_tensors="pt").input_features

        predicted_ids = self.__model.generate(input_features, max_new_tokens=4000)

        transcription = self.__processor.batch_decode(predicted_ids, skip_special_tokens=True)

        return transcription