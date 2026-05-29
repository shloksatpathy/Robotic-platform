import numpy as np
import faiss
import os
import shutil

class SpeakerDatabase:

    def __init__(self):
        self.index = None
        self.names = []
        self.db_path = os.path.join(os.path.dirname(__file__), "known_speakers.npz")
        self._migrate_old_db()
        self.load_known()

    def _migrate_old_db(self):
        old_db_dir = os.path.join(os.path.dirname(__file__), "known_db")
        if os.path.exists(old_db_dir):
            print("Migrating old known_db folder to single known_speakers.npz...")
            db = {}
            for file in os.listdir(old_db_dir):
                if file.endswith(".npy"):
                    name = file.replace(".npy", "")
                    emb = np.load(os.path.join(old_db_dir, file))
                    db[name] = emb
            if db:
                # If known_speakers.npz already exists, merge them
                if os.path.exists(self.db_path):
                    existing = dict(np.load(self.db_path))
                    existing.update(db)
                    db = existing
                np.savez(self.db_path, **db)
            
            # safely remove the old directory
            shutil.rmtree(old_db_dir)
            print("Migration complete.")

    def load_known(self):
        if not os.path.exists(self.db_path):
            return

        with np.load(self.db_path) as data:
            embeddings = []
            
            for name in data.files:
                emb = data[name].astype(np.float32)
                embeddings.append(emb)
                self.names.append(name)

        if len(embeddings) == 0:
            return

        dim = embeddings[0].shape[0]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(np.array(embeddings))

    def identify(self, embedding):
        if self.index is None:
            return None

        D, I = self.index.search(embedding.reshape(1, -1), 1)
        similarity = float(D[0][0])

        if similarity > 0.60:
            return self.names[I[0][0]]

        return None