import os
import pickle
import logging
import numpy as np
from deepface import DeepFace

from src.config import (
    MEMORY_FILE, 
    REFERENCE_DIR, 
    FILE_TYPES,
    MODEL,
    DETECTOR,
    MAX_EMBEDDINGS
)
from src.scanning.util import normalize

logger = logging.getLogger("SASHA.scanning.memory")

class FaceMemory:
    def __init__(self):
        self.memory = {}
        self.load_memory()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "rb") as f:
                    loaded = pickle.load(f)

                for name, vectors in loaded.items():
                    self.memory[name] = [
                        normalize(v) for v in vectors
                    ]
                logger.info("Loaded %s face profile(s) from memory", len(self.memory))

            except Exception:
                logger.exception("Could not load face memory from %s", MEMORY_FILE)
                return False

        os.makedirs(REFERENCE_DIR, exist_ok=True)

        for filename in os.listdir(REFERENCE_DIR):
            if not filename.lower().endswith(FILE_TYPES):
                continue

            name = os.path.splitext(filename)[0].capitalize()
            if name in self.memory:
                continue

            path = os.path.join(REFERENCE_DIR, filename)

            try:
                embded_objects = DeepFace.represent(
                    img_path=path,
                    model_name=MODEL,
                    detector_backend=DETECTOR,
                    enforce_detection=True
                )

                if len(embded_objects) != 1:
                    logger.warning(
                        "Skipped reference %s: expected one face, found %s",
                        filename, len(embded_objects)
                    )
                    continue

                vector = normalize(embded_objects[0]["embedding"])

                self.memory[name] = [vector]
                logger.info("Registered reference profile %s", name)
            except Exception:
                logger.exception("Could not process reference image %s", filename)

        logger.info("Face memory ready with %s profile(s)", len(self.memory))
        return bool(self.memory)

    def save_memory(self):
        tmp = MEMORY_FILE + ".tmp"
        try:
            with open(tmp, "wb") as f:
                pickle.dump(
                    self.memory,
                    f,
                    protocol=pickle.HIGHEST_PROTOCOL
                )

            os.replace(tmp, MEMORY_FILE)
            logger.info("Saved %s face profile(s) to %s", len(self.memory), MEMORY_FILE)

        except Exception:
            logger.exception("Could not save face memory to %s", MEMORY_FILE)

    def add_embedding(self, name, vector):
        if name not in self.memory:
            return

        vectors = self.memory[name]
        if len(vectors) >= MAX_EMBEDDINGS:
            if len(vectors) > 1:
                vectors.pop(1)
            else:
                return
        vectors.append(vector.copy())
        logger.info("Added embedding for %s; profile now has %s", name, len(vectors))


