import re
from functools import lru_cache
import json
from job_profile.job_loader import load_all_jobs
from analysis.education_matcher import extract_education_level
from analysis.skill_normalizer import normalize_skill, normalize_text_tokens
from analysis.experience_matcher import extract_experience_years


def normalize(text):
    return re.sub(r"[^a-z0-9+.# ]", " ", text.lower())

@lru_cache(maxsize=64)
def extract_skills_from_jd(jd_text):
    """
    Extract skill buckets from raw Job Description
    using the global job dataset as vocabulary.

    ⚡ Cached by JD text
    """

    jd_text = normalize(jd_text)

    buckets = {
        "critical_skills": set(),
        "core_skills": set(),
        "optional_skills": set(),
        "soft_skills": set()
    }

    jobs = load_all_jobs()

    # Build master skill map from dataset
    skill_to_bucket = {}

    for job in jobs.values():
        for group in buckets.keys():
            for skill in job.get(group, []):
                skill_to_bucket[skill.lower()] = group

    jd_tokens = normalize_text_tokens(jd_text)

    for skill, bucket in skill_to_bucket.items():
        normalized_skill = normalize_skill(skill)
        if normalized_skill in jd_tokens:
            buckets[bucket].add(normalized_skill)

    return {k: sorted(v) for k, v in buckets.items()}


@lru_cache(maxsize=32)
def infer_job_from_jd_cached(jd_key):
    """
    Cached version of job inference.
    jd_key must be a string.
    """
    jd_profile = json.loads(jd_key)
    jobs = load_all_jobs()
    scored_jobs = []

    for job in jobs.values():
        score = 0

        score += 4 * len(set(jd_profile["critical_skills"]) & set(job["critical_skills"]))
        score += 3 * len(set(jd_profile["core_skills"]) & set(job["core_skills"]))
        score += 1 * len(set(jd_profile["optional_skills"]) & set(job["optional_skills"]))
        score += 0.5 * len(set(jd_profile["soft_skills"]) & set(job["soft_skills"]))

        scored_jobs.append((score, job))

    scored_jobs.sort(key=lambda x: x[0], reverse=True)

    if not scored_jobs or scored_jobs[0][0] == 0:
        return None

    best_job = scored_jobs[0][1]

    return {
        "title": best_job["title"],
        "domain": best_job["domain"],
        "job_definition": best_job
    }



def infer_job_from_jd(jd_profile):
    """
    Match extracted JD skills against job database
    with caching.
    """

    # Convert dict → stable JSON string key
    jd_key = json.dumps(jd_profile, sort_keys=True)

    return infer_job_from_jd_cached(jd_key)


@lru_cache(maxsize=64)
def build_job_profile_from_jd(jd_text):
    """
    Build JD profile with caching.
    """

    jd_education_level = extract_education_level(jd_text)
    jd_experience_years = extract_experience_years(jd_text)

    jd_profile = extract_skills_from_jd(jd_text)
    best_job = infer_job_from_jd(jd_profile)

    return {
        "job_title": best_job["title"] if best_job else "Unknown",
        "domain": best_job["domain"] if best_job else "Unknown",
        "job_reference": best_job["job_definition"] if best_job else None,
        "jd_skills": jd_profile,
        "min_education_level": jd_education_level,
        "min_experience_years": jd_experience_years
    }
