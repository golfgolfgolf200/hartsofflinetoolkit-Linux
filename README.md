# HartsOfflineToolkit

A zero-cloud, strictly CPU-only, resource-governed hybrid semantic search
appliance engineered for commodity Linux hardware, air-gapped workstations,
and sovereign data vaults using Google's EmbeddingGemma 2.

---

## 100% CPU-Native Architecture

Unlike most modern AI retrieval frameworks that expect high-end NVIDIA GPUs
or offload embeddings to metered third-party cloud APIs,
HartsOfflineToolkit is engineered from the ground up to run strictly on
commodity x86_64 CPUs.

- No GPU / No VRAM Required: Runs on integrated graphics desktops (for
  example, Intel UHD 630 / 8th Gen i5 or equivalent) without hardware
  acceleration cards.
- Deterministic Resource Governor: Strict process niceness, idle I/O
  priority (`ionice`), and hard CPU thread/core clamps (`taskset`/
  `cpu_affinity`) guarantee that high-volume indexing runs silently in the
  background without dropping audio packets, freezing video playback, or
  lagging the desktop compositor.
- Zero Network Traffic: Operates completely offline with zero telemetry,
  zero model API tokens, and zero outbound network calls once weights are
  cached locally.

---

## Core Differentiators

Compared to traditional search utilities such as `grep` or Recoll, cloud
RAG platforms, and unconstrained local AI tools, HartsOfflineToolkit solves
specific operational bottlenecks that make offline search impractical:

- Hybrid Reciprocal Rank Fusion (vs. vector-only cloud APIs): Most vector
  search tools fail on exact model numbers, error codes, tax IDs, or
  invoice references because dense embeddings blend specific tokens into
  generalized conceptual math. HartsOfflineToolkit combines lexical BM25
  with EmbeddingGemma 2 vectors via RRF (k=60), ensuring exact statutory
  codes and natural-language concepts match with equal precision.
- Deterministic Hardware Governor (vs. resource-hungry local AI tools):
  Tools such as Ollama or PrivateGPT saturate all available cores, causing
  UI latency, fan noise, and stutter during audio/video playback.
  HartsOfflineToolkit pins worker threads, sets CPU core affinity, and
  applies idle process scheduling (`ionice` / `nice`) so multi-gigabyte
  document batches index silently in the background.
- MRL 256-D Truncation (vs. bloated full-dimension embeddings): Leverages
  EmbeddingGemma 2's native Matryoshka Representation Learning (MRL) to
  truncate vectors from 768 to 256 dimensions. This reduces memory
  footprint and disk I/O by approximately 66% while accelerating CPU
  dot-product math with negligible impact on retrieval accuracy.
- Structured Tabular Ingestion (vs. naive text chunking): Standard RAG
  text-splitters break spreadsheets, tax forms, and financial ledgers into
  fragmented, unsearchable sentences. HartsOfflineToolkit extracts tables
  into formatted Markdown grids via `pdfplumber`, preserving row-and-column
  relationships for accurate accounting and compliance retrieval.
- Zero-Server In-Process LanceDB (vs. complex client-server databases):
  Avoids running background Docker daemons or standalone network services
  like Qdrant, Chroma, or Milvus. The vector store operates serverless
  directly against local NVMe or SSD files.

---

## Use Cases

### 1. Legal & Regulatory Discovery (Air-Gapped Workstations)

- Privileged Attorney-Client Records: Search litigation files, discovery
  bundles, depositions, and non-disclosure agreements without exposing
  confidential data to cloud LLM vendors.
- Regulatory Compliance & Audits: Match obscure contract clauses (for
  example, "30-day cancellation terms without cause") alongside exact
  statutory references (for example, "CFR Title 26 § 501").

### 2. Accounting, Tax & Corporate Financial Auditing

- Tabular Invoice & Ledger Extraction: Accurately locate financial figures
  across balance sheets, Form 1099/W-9 bundles, and P&L statements
  preserved in clean tabular Markdown format.
- Vendor Reference Matching: Instantly look up audit vouchers, wire
  details, and purchase order tracking numbers (for example,
  `REF-99482-TX`) that standard vector-only RAG pipelines fail to locate.

### 3. Healthcare, Clinical & Patient Records (HIPAA Compliance)

- Sovereign Patient Histories: Ingest electronic medical records (EMRs),
  discharge summaries, and clinical trial notes on air-gapped hospital
  clinic hardware where external internet egress is strictly prohibited by
  law.
- Medical Jargon & Synonym Retrieval: Map natural patient symptom
  descriptions to clinical terminology without relying on exact character
  matches.

### 4. Field Engineering, Maritime & Tactical Edge Operations

- Remote Infrastructure Maintenance: Search hundreds of gigabytes of
  technical schematics, diesel generator manuals, or avionics guides aboard
  marine vessels, offshore rigs, and aircraft hangars with zero satellite
  or internet connectivity.
- Offline Codebase & Incident Triage: Query historical post-mortems,
  legacy codebases, and stack traces during network outages or secure SCIF
  operations.

### 5. Private Desktop Personal Copilot

- Zero-Lag Background Assistant: Silently index personal research papers,
  Obsidian vaults, Markdown notes, and personal tax returns on an everyday
  home desktop while simultaneously gaming, compiling code, or streaming
  music and video.

---

## Installation & Setup

### Prerequisites

- OS: Ubuntu 22.04 / 24.04 LTS (or a modern Linux distribution)
- CPU: 4+ physical cores (Intel 8th Gen or AMD Ryzen equivalent
  recommended)
- RAM: 8 GB minimum (16 GB - 32 GB recommended for large document
  collections)
- Python: 3.10 - 3.12

### Step-by-Step Installation

```bash
# 1. Clone repository
git clone https://github.com/<your-username>/hartsofflinetoolkit.git
cd hartsofflinetoolkit

# 2. Create an isolated virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install CPU-only PyTorch and Torchvision
#    (prevents multi-gigabyte CUDA bloat)
pip install --upgrade pip setuptools wheel
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 4. Install toolkit dependencies
pip install -r requirements.txt

# 5. Create runtime directories and initialize configuration
mkdir -p data/raw data/db
cp .env.example .env
```

### Pre-Caching Model Weights (One-Time Setup)

Because HartsOfflineToolkit strictly enforces air-gapped operation
(`HF_HUB_OFFLINE=1`), download Google's EmbeddingGemma 2 model snapshot
once while connected to the internet before taking the host offline:

```bash
python3 - <<'PY'
from huggingface_hub import snapshot_download
path = snapshot_download("google/embeddinggemma-2")
print(f"Weights cached at: {path}")
PY
```

Then copy the returned snapshot path into your `.env` file under
`MODEL_PATH`:

```env
MODEL_PATH=/home/<username>/.cache/huggingface/hub/models--google--embeddinggemma-2/snapshots/<snapshot_hash>
```

## Usage

### 1. Ingest Documents into the Vault

Drop PDFs, plain text files, or Markdown notes into `./data/raw` (or
specify a custom target path) and run the indexer:

```bash
python3 cli.py index --path ./data/raw
```

### 2. Execute Hybrid Search

Query the index using natural-language phrasing or exact code tokens:

```bash
# Semantic query (EmbeddingGemma 2 MRL-256 vector match)
python3 cli.py search "What fee is taken out if we rush a payment?"

# Exact token / identifier query (BM25 exact match)
python3 cli.py search "REF-99482-TX"
```

### 3. Resetting / Purging the Vault

Because LanceDB is serverless and stored directly on disk, purging indexed
documents or resetting the database after deleting raw files is as simple
as removing the database directory:

```bash
# Wipe the LanceDB table and indices
rm -rf data/db/*

# Re-index clean source documents
python3 cli.py index --path ./data/raw
```

## Running Verification Tests

Run the test suite to verify hardware thread clamping, CPU affinity, and
hybrid search precision:

```bash
PYTHONPATH=. pytest -v tests/test_engine.py
```

## Security & Sandboxing Posture

Because HartsOfflineToolkit is engineered for air-gapped environments,
confidential discovery, and sensitive enterprise data, deployment should
follow strict host-level isolation:

- Strict Offline Operation: The runtime hardcodes `HF_HUB_OFFLINE=1` to
  block outbound calls, socket telemetry, or remote checkpoint pulling.
- Untrusted Document Ingestion: The parsing layer extracts text and tables
  from external PDFs via `pdfplumber`. If you run this service on a host
  that handles untrusted third-party uploads, run the ingestion worker in
  an unprivileged Linux container, bubblewrap sandbox, or a dedicated
  restricted user account without sudo privileges.
- Model Weight Integrity: Restrict the Hugging Face cache directory to
  read-only permissions (`chmod -R a-w <path_to_model>`) to prevent worker
  processes or browser automation tools running on the same machine from
  tampering with embedding weights.
- Zero-Egress Host Policy: For maximum compliance (for example, HIPAA or
  legal discovery), pair local operation with standard firewall enforcement
  (`ufw default deny incoming`) and disable WAN egress on the indexing
  interface.

## License

This project is licensed under the MIT License. See `LICENSE.md` for
details.

## Acknowledgments & Citation

HartsOfflineToolkit uses Google DeepMind's EmbeddingGemma 2
(`google/embeddinggemma-2`, licensed under Apache 2.0) for local semantic
embeddings:

```bibtex
@misc{embeddinggemma2_2026,
  title={EmbeddingGemma 2: Unified and Efficient Multimodal Representations},
  author={Schechter Vera, Henrique and Dua, Sahil and Team, EmbeddingGemma},
  year={2026},
  eprint={2610.37364},
  archivePrefix={arXiv},
  primaryClass={cs.LG},
  url={https://arxiv.org/abs/2610.37364}
}
```
