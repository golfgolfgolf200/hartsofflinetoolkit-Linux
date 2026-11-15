import os
import sys
import psutil
import torch
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    model_path: str = os.getenv("MODEL_PATH", "")
    affinity_cores: list[int] = [
        int(c.strip()) for c in os.getenv("CPU_AFFINITY_CORES", "0,1,2").split(",") if c.strip()
    ]
    worker_threads: int = int(os.getenv("CPU_WORKER_THREADS", "3"))
    niceness: int = int(os.getenv("NICENESS_LEVEL", "10"))
    ionice_class: int = int(os.getenv("IONICE_CLASS", "3"))
    matryoshka_dim: int = int(os.getenv("MATRYOSHKA_DIM", "256"))
    rrf_k: int = int(os.getenv("RRF_K", "60"))
    db_path: str = os.getenv("LANCEDB_PATH", "./data/db")
    ingest_path: str = os.getenv("DATA_INGEST_PATH", "./data/raw")

    # Chunking, Batching & Security Guardrails
    chunk_words: int = int(os.getenv("CHUNK_WORDS", "400"))
    chunk_overlap_words: int = int(os.getenv("CHUNK_OVERLAP_WORDS", "50"))
    embed_batch_size: int = Field(default=int(os.getenv("EMBED_BATCH_SIZE", "16")), ge=1, le=64)
    max_file_bytes: int = int(os.getenv("MAX_FILE_BYTES", str(50 * 1024 * 1024)))  # 50 MB
    max_chunks_per_doc: int = int(os.getenv("MAX_CHUNKS_PER_DOC", "500"))

settings = Settings()

def apply_hardware_governor(allow_hub_download: bool = False):
    torch.set_num_threads(settings.worker_threads)
    os.environ["OMP_NUM_THREADS"] = str(settings.worker_threads)
    os.environ["MKL_NUM_THREADS"] = str(settings.worker_threads)

    if allow_hub_download:
        os.environ.pop("HF_HUB_OFFLINE", None)
    else:
        os.environ["HF_HUB_OFFLINE"] = "1"

    p = psutil.Process()
    try:
        p.cpu_affinity(settings.affinity_cores)
    except Exception as e:
        sys.stderr.write(f"[WARN] Unable to set CPU affinity: {e}\n")

    try:
        os.nice(settings.niceness)
    except Exception as e:
        sys.stderr.write(f"[WARN] Unable to set nice level: {e}\n")

    try:
        p.ionice(ioclass=psutil.IOPRIO_CLASS_IDLE)
    except Exception as e:
        sys.stderr.write(f"[WARN] Unable to set ionice: {e}\n")
