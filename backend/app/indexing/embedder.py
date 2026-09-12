import os
import numpy as np
from typing import List, Union
from sentence_transformers import SentenceTransformer
from ..config import MODEL_NAME

class Embedder:
    _instance = None

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.model = None
        self._load_model()

    @classmethod
    def get_instance(cls, model_name: str = MODEL_NAME):
        if cls._instance is None:
            cls._instance = cls(model_name=model_name)
        return cls._instance

    def _load_model(self):
        try:
            # Try loading from local cache first to avoid network delays
            self.model = SentenceTransformer(self.model_name, local_files_only=True)
            print(f"[Embedder] Loaded {self.model_name} from local cache.")
        except Exception:
            # Fallback to standard load
            print(f"[Embedder] Loading {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
            print(f"[Embedder] Successfully loaded {self.model_name}.")

    def encode(self, texts: Union[str, List[str]], batch_size: int = 64, show_progress_bar: bool = False) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings
