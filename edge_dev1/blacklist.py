import os
import numpy as np
import cv2
from insightface.app import FaceAnalysis

BLACKLIST_DIR = os.path.join(os.path.dirname(__file__), "blacklist_faces")
MATCH_THRESHOLD = 0.45  # cosine similarity; lower = stricter, raise if too many false negatives

_app = None
_embeddings = {}  # name -> normed_embedding


def _get_app():
    global _app
    if _app is None:
        _app = FaceAnalysis(
            name="buffalo_s",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        _app.prepare(ctx_id=0, det_size=(320, 320))
    return _app


def load_blacklist():
    """Load reference photos from blacklist_faces/. Filename (without extension) = person name."""
    global _embeddings
    app = _get_app()
    _embeddings = {}
    if not os.path.isdir(BLACKLIST_DIR):
        print(f"[blacklist] {BLACKLIST_DIR} not found — no blacklist loaded")
        return
    for fname in sorted(os.listdir(BLACKLIST_DIR)):
        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        name = os.path.splitext(fname)[0]
        img = cv2.imread(os.path.join(BLACKLIST_DIR, fname))
        if img is None:
            print(f"[blacklist] Could not read {fname}, skipping")
            continue
        faces = app.get(img)
        if not faces:
            print(f"[blacklist] No face detected in {fname}, skipping")
            continue
        face = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
        _embeddings[name] = face.normed_embedding
        print(f"[blacklist] Enrolled: {name}")
    print(f"[blacklist] {len(_embeddings)} person(s) in blacklist")


def get_app():
    return _get_app()


def match_face(normed_embedding, threshold=MATCH_THRESHOLD):
    """Return (name, similarity) for best blacklist match, or (None, best_sim) if below threshold."""
    if not _embeddings:
        return None, 0.0
    best_name, best_sim = None, -1.0
    for name, ref in _embeddings.items():
        sim = float(np.dot(normed_embedding, ref))
        if sim > best_sim:
            best_name, best_sim = name, sim
    if best_sim >= threshold:
        return best_name, best_sim
    return None, best_sim
