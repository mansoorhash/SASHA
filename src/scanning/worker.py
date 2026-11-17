import time
import logging
import numpy as np

from queue import Queue, Full, Empty
from threading import Event
from scipy.optimize import linear_sum_assignment
from PySide6.QtCore import QThread, Signal
from deepface import DeepFace
from src.config import (
    MODEL,
    DETECTOR,
    MATCH_THRESHOLD,
    LEARN_INTERVAL,
    MIN_FACE_SIZE
)
from src.scanning.memory import FaceMemory
from src.scanning.util import normalize

face_memory = FaceMemory()
logger = logging.getLogger("SASHA.scanning.worker")

class ScanWorker(QThread):
    ready = Signal()
    result = Signal(object)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._frames = Queue(maxsize=1)
        self._stop = Event()
        self._last_learn = {}
        self._new_embeddings = 0
        
        self.face_memory = face_memory

    def submit_frame(self, frame):
        if self._stop.is_set() or self._frames.full():
            return
        try:
            self._frames.put_nowait(frame.copy())
        except Full:
            pass

    def run(self):
        processed_frames = 0
        logger.info("Scan worker started")
        try:
            self.ready.emit()

            while not self._stop.is_set():
                try:
                    frame = self._frames.get(timeout=0.1)
                except Exception as exc:
                    if not isinstance(exc, Empty):
                        logger.exception("Could not read a queued scan frame")
                    continue

                processed_frames += 1
                try:
                    embded_faces = DeepFace.represent(
                        img_path=frame,
                        model_name=MODEL,
                        detector_backend=DETECTOR,
                        enforce_detection=True,
                    )

                except ValueError:
                    logger.debug("No face detected in scan frame")
                    embded_faces = []

                faces = []
                now = time.monotonic()

                candidates = [
                    emb for emb in embded_faces
                    if emb["facial_area"]["w"] >= MIN_FACE_SIZE
                    and emb["facial_area"]["h"] >= MIN_FACE_SIZE
                ]

                candidates.sort(key=self._area, reverse=True)
                valid_faces = []

                for emb in candidates:
                    if any(self._contained(emb, larger) for larger in valid_faces):
                        continue
                    valid_faces.append(emb)

                names = [
                    name for name, saved_vectors in self.face_memory.memory.items()
                    if saved_vectors
                ]

                if valid_faces:
                    vectors = [normalize(emb["embedding"]) for emb in valid_faces]
                    scores = np.full((len(valid_faces), len(names)), np.inf)

                    for face_index, vector in enumerate(vectors):
                        for name_index, name in enumerate(names):
                            scores[face_index, name_index] = min(
                                1.0 - float(np.dot(vector, saved_vector))
                                for saved_vector in self.face_memory.memory[name]
                            )

                    costs = np.full(
                        (len(valid_faces), len(names) + len(valid_faces)),
                        MATCH_THRESHOLD,
                    )
                    costs[:, :len(names)] = np.where(
                        scores < MATCH_THRESHOLD,
                        scores,
                        MATCH_THRESHOLD + 1.0,
                    )

                    row_indices, column_indices = linear_sum_assignment(costs)
                    assignments = dict(zip(row_indices, column_indices))

                    for face_index, emb in enumerate(valid_faces):
                        column = assignments[face_index]

                        if column < len(names) and scores[face_index, column] < MATCH_THRESHOLD:
                            name = names[column]
                            distance = float(scores[face_index, column])
                        else:
                            name = "unknown"
                            distance = (
                                float(np.min(scores[face_index]))
                                if names else float("inf")
                            )

                        if name != "unknown":
                            first_seen = self._last_learn.setdefault(name, now)

                            if now - first_seen >= LEARN_INTERVAL:
                                self.face_memory.add_embedding(name, vectors[face_index])
                                self._new_embeddings += 1
                                self._last_learn[name] = now

                            faces.append({
                                "name": name,
                                "distance": distance,
                                "box": emb["facial_area"],
                            })

                self.result.emit({
                    "faces": faces,
                    "detected_faces": len(faces),
                    "new_embeddings": self._new_embeddings
                })
                
        except Exception as exc:
            logger.exception("Scan worker failed")
            self.error.emit(str(exc))
        finally:
            if self.face_memory.memory is not None:
                self.face_memory.save_memory()
            logger.info(
                "Scan worker exited after %s frame(s); %s embedding(s) added",
                processed_frames, self._new_embeddings
            )

    def stop(self):
        logger.info("Scan worker stop requested")
        self._stop.set()

    def _area(self, emb):
        box = emb["facial_area"]
        return box["w"] * box["h"]

    def _contained(self, inner, outer):
        a = inner["facial_area"]
        b = outer["facial_area"]
        return (
            a["x"] >= b["x"]
            and a["y"] >= b["y"]
            and a["x"] + a["w"] <= b["x"] + b["w"]
            and a["y"] + a["h"] <= b["y"] + b["h"]
        )