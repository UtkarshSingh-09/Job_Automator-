import hashlib
from typing import Dict, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

from resume_agent.db import get_db
from resume_agent.models import ProjectModel, JobModel
from resume_agent.logging import logger

_EMBED_MODEL: Optional[SentenceTransformer] = None
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def get_embed_model() -> SentenceTransformer:
    """Lazy singleton loader for local SentenceTransformer model."""
    global _EMBED_MODEL
    if _EMBED_MODEL is None:
        logger.info(f"Loading local embedding model '{MODEL_NAME}' on CPU...")
        _EMBED_MODEL = SentenceTransformer(MODEL_NAME, device="cpu")
    return _EMBED_MODEL


def build_project_embedding_text(project: ProjectModel) -> str:
    """
    Assemble high-density technical grounding representation for a project.
    Combines name, language, description, topics, verified manual notes, and first 1200 chars of README.
    """
    parts = []
    name = project.display_name or project.repo_name
    parts.append(f"Project: {name}")

    if project.primary_language:
        parts.append(f"Language: {project.primary_language}")

    if project.description:
        parts.append(f"Description: {project.description}")

    if project.languages:
        parts.append(f"Technologies: {', '.join(project.languages)}")

    if project.topics:
        parts.append(f"Topics: {', '.join(project.topics)}")

    if project.manual_notes:
        parts.append(f"Verified Technical Highlights: {project.manual_notes}")

    if project.readme_md:
        parts.append(f"README: {project.readme_md[:1200]}")

    return "\n".join(parts)


def build_job_embedding_text(job: JobModel) -> str:
    """
    Assemble high-density representation of target job posting for semantic vector encoding.
    """
    desc_snippet = job.description_md[:1500] if job.description_md else ""
    return (
        f"Job Title: {job.title}\n"
        f"Company: {job.company_name}\n"
        f"Location: {job.location or 'N/A'}\n"
        f"Remote Status: {job.remote_type or 'onsite'}\n"
        f"Key Description & Requirements:\n{desc_snippet}"
    )


def compute_source_hash(text: str) -> str:
    """Compute SHA-256 hash of raw input text to detect cache invalidation."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_text(text: str) -> np.ndarray:
    """Encode an arbitrary text string into a normalized 384-dimensional float32 vector."""
    model = get_embed_model()
    vec = model.encode(text, normalize_embeddings=True)
    return np.array(vec, dtype=np.float32)


def get_or_compute_project_embeddings() -> Dict[int, np.ndarray]:
    """
    Retrieve or compute normalized 384-dim embeddings for all projects in database.
    Caches vectors directly as SQLite BLOBs with source hash checking for instant subsequent retrieval.
    Returns: mapping of project_id -> np.ndarray (shape: (384,), dtype: float32).
    """
    from resume_agent.github.sync import get_all_projects

    projects = get_all_projects()
    embeddings_map: Dict[int, np.ndarray] = {}
    updates: List[Tuple[bytes, str, int]] = []

    model = None

    for p in projects:
        if p.id is None:
            continue

        text = build_project_embedding_text(p)
        source_hash = compute_source_hash(text)

        # Check existing valid cached BLOB
        if p.embedding and p.embedding_source_hash == source_hash:
            try:
                vec = np.frombuffer(p.embedding, dtype=np.float32)
                if vec.shape == (384,):
                    embeddings_map[p.id] = vec
                    continue
            except Exception:
                pass

        # Compute embedding using local model
        if model is None:
            model = get_embed_model()

        vec = model.encode(text, normalize_embeddings=True)
        vec_f32 = np.array(vec, dtype=np.float32)
        embeddings_map[p.id] = vec_f32
        updates.append((vec_f32.tobytes(), source_hash, p.id))

    if updates:
        with get_db() as conn:
            conn.executemany(
                "UPDATE projects SET embedding = ?, embedding_source_hash = ? WHERE id = ?;",
                updates,
            )
        logger.info(f"Computed and persisted vector embeddings for {len(updates)} projects in database.")

    return embeddings_map
