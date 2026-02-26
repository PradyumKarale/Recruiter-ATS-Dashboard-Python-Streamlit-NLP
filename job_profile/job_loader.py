import json
from pathlib import Path
from functools import lru_cache
from analysis.skill_normalizer import normalize_skill

BASE_DIR = Path(__file__).parent
DB_DIR = BASE_DIR / "job_database"


def _load_all_jobs_uncached():
    """
    Internal loader.
    DO NOT CALL DIRECTLY.
    """

    index_file = DB_DIR / "data.json"

    with open(index_file, "r", encoding="utf-8") as f:
        index = json.load(f)

    all_jobs = {}

    for domain_key in index["domains"]:
        domain_file = DB_DIR / f"{domain_key}.json"

        with open(domain_file, "r", encoding="utf-8") as f:
            domain_data = json.load(f)

        domain_name = domain_data["domain"]

        for role_key, role in domain_data["roles"].items():

            # -----------------------------
            # NEW + OLD SCHEMA SUPPORT
            # -----------------------------
            skills_block = role.get("skills", {})

            critical = skills_block.get("critical", role.get("critical_skills", []))
            core = skills_block.get("core", role.get("core_skills", []))
            tools = skills_block.get("tools", [])
            optional = skills_block.get("optional", role.get("optional_skills", []))
            soft = skills_block.get("soft", role.get("soft_skills", []))

            all_skills = critical + core + tools + optional + soft

            all_jobs[role_key] = {
                "title": role["title"],
                "domain": domain_name,

                # unified normalized skill vocab
                "skills": [normalize_skill(s) for s in all_skills],

                # structured buckets (USED BY INFERENCERS)
                "critical_skills": critical,
                "core_skills": core,
                "optional_skills": optional + tools,
                "soft_skills": soft,

                # metadata
                "seniority": role.get("seniority", "Unknown"),
                "education": role.get("education", {}),
                "experience": role.get("experience", {}),
                "aliases": role.get("aliases", []),
                "discriminators": role.get("discriminators", {}),
                "seniority_expectation": role.get("seniority_expectation", {})
            }

    return all_jobs


@lru_cache(maxsize=1)
def load_all_jobs():
    """
    Cached public API.
    Safe to call from anywhere.
    """
    return _load_all_jobs_uncached()
