from core.logger_utils import get_logger
from core.config import settings

from sentence_transformers import CrossEncoder

logger = get_logger(__name__)


class CrossEncoderModelSingleton:
    def __init__(self,
            model_id: str = settings.CROSS_ENCODER_MODEL_ID,
            device:str = settings.EMBEDDING_MODEL_DEVICE):

        self._model_id = model_id
        self._device = device

        self._model = CrossEncoder(model_name=self.model_id, device=self.device)

    # def get_model(self):
    #     return self._model

    # for sake of time
    def __call__(self, pairs: list[tuple[str, str]]) -> list[float]:
        score = self._model.predict(pairs)
        return score.tolist()
