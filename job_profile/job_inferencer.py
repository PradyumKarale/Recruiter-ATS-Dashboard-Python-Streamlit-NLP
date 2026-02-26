from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def infer_job_from_text(text, jobs_db):
    """
    Returns the best matching job as a structured dict
    """

    job_names = []
    job_texts = []

    for job_key, job in jobs_db.items():
        job_names.append(job_key)
        combined = (
            job["title"] + " " +
            " ".join(job["skills"]) + " " +
            job["domain"]
        )
        job_texts.append(combined)

    job_embeddings = model.encode(job_texts, convert_to_tensor=True)
    user_embedding = model.encode(text, convert_to_tensor=True)

    scores = util.cos_sim(user_embedding, job_embeddings)[0]

    best_idx = int(scores.argmax())

    best_job_key = job_names[best_idx]
    best_job = jobs_db[best_job_key]

    return {
        "job_key": best_job_key,
        "title": best_job["title"],
        "domain": best_job["domain"],
        "confidence": float(scores[best_idx])
    }
