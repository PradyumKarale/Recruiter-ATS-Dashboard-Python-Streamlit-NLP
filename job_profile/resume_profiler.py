import re
from job_profile.job_loader import load_all_jobs
from analysis.skill_normalizer import normalize_skill
from analysis.finance_enricher import enrich_finance_skills
from analysis.education_levels import EDU_LEVELS


def normalize_inference_output(result):
    """
    Ensures consistent keys for UI & CSV consumption.
    """
    return {
        "job_title": result.get("job_title", "Unknown"),
        "domain": result.get("domain", "Unknown"),
        "confidence": result.get("confidence", 0.0),
        "confidence_band": result.get("confidence_band", "Unknown"),
        "seniority": result.get("seniority", "Unknown"),
        "fit_reasons": result.get("fit_reasons", []),
        "rejection_reasons": result.get("rejection_reasons", []),
        "compared_against": result.get("compared_against", []),
    }



def validate_seniority(job, resume_years):
    """
    Checks if resume experience matches job seniority expectation.
    """
    expectations = job.get("seniority_expectation")
    if not expectations or resume_years == -1:
        return 0.0

    for level, bounds in expectations.items():
        min_y = bounds.get("min", 0)
        max_y = bounds.get("max", float("inf"))

        if min_y <= resume_years <= max_y:
            return 1.0  # valid

    return -2.0  # mismatch penalty

def check_hard_rejection(resume, job):
    reasons = []

    # --- EDUCATION CHECK ---
    resume_edu = resume.get("education_level", -1)

    job_edu_raw = job.get("education", {}).get("min_level")

    if job_edu_raw:
        job_edu = EDU_LEVELS.get(job_edu_raw.lower(), -1)

        # only compare if BOTH are valid ints
        if resume_edu != -1 and job_edu != -1:
            if resume_edu < job_edu:
                reasons.append(
                    f"Education below requirement ({job_edu_raw})"
                )

    return reasons



def apply_discriminators(score, job, resume_tokens):
    """
    Softly adjusts score using role discriminators.
    """
    disc = job.get("discriminators")
    if not disc:
        return score

    # --- MUST HAVE ANY ---
    must_have = disc.get("must_have_any", [])
    if must_have:
        if not any(s in resume_tokens for s in must_have):
            score *= 0.6  # soft penalty

    # --- SHOULD NOT HAVE PRIMARY ---
    avoid = disc.get("should_not_have_primary", [])
    avoid_hits = sum(1 for s in avoid if s in resume_tokens)

    if avoid_hits >= 2:
        score *= 0.7  # another soft penalty

    return score

def apply_role_discriminators(resume, job):
    """
    Applies HARD role constraints.
    Returns a penalty score (negative or zero).
    HARD GATE: must_have_both
    """

    penalty = 0.0

    resume_text = resume.get("text", "").lower()
    resume_skills = set(normalize_skill(s) for s in resume.get("skills", []))

    discriminators = job.get("discriminators", {})

    # -----------------------------
    # HARD GATE: MUST HAVE BOTH
    # -----------------------------
    must_have_both = discriminators.get("must_have_both", [])
    for pair in must_have_both:
        if not any(
            normalize_skill(p) in resume_skills or p in resume_text
            for p in pair
        ):
            # ❌ FAIL HARD — role excluded
            return -100.0

    # -----------------------------
    # MUST HAVE ANY (soft gate)
    # -----------------------------
    must_have_any = discriminators.get("must_have_any", [])
    if must_have_any:
        if not any(
            normalize_skill(s) in resume_skills or s in resume_text
            for s in must_have_any
        ):
            penalty -= 5.0

    # -----------------------------
    # SHOULD NOT HAVE PRIMARY
    # -----------------------------
    should_not = discriminators.get("should_not_have_primary", [])
    for s in should_not:
        if normalize_skill(s) in resume_skills or s in resume_text:
            penalty -= 3.0

    return penalty


def calibrate_confidence(raw_score: float) -> dict:
    """
    Converts raw confidence score into recruiter-friendly bands.
    """
    if raw_score >= 0.85:
        return {"score": round(raw_score, 2), "band": "Strong Fit"}
    elif raw_score >= 0.65:
        return {"score": round(raw_score, 2), "band": "Good Fit"}
    elif raw_score >= 0.45:
        return {"score": round(raw_score, 2), "band": "Borderline"}
    else:
        return {"score": round(raw_score, 2), "band": "Weak Fit"}



def infer_domain_from_resume(resume, jobs):
    """
    Infers best-fit domain using aggregated skill scores.
    """
    resume_skills = set(normalize_skill(s) for s in resume.get("skills", []))
    resume_text = resume.get("text", "").lower()
    raw_tokens = re.findall(r"[a-z0-9+.#]+", resume_text)

    resume_tokens = set(normalize_skill(t) for t in raw_tokens)

    # ALSO add joined bigrams (CRITICAL)
    for i in range(len(raw_tokens) - 1):
     joined = raw_tokens[i] + raw_tokens[i + 1]
     resume_tokens.add(normalize_skill(joined))




    domain_scores = {}

    for job in jobs.values():
        domain = job["domain"]
        score = 0.0

        for skill in job.get("critical_skills", []):
            if normalize_skill(skill) in resume_skills or normalize_skill(skill) in resume_tokens:
                score += 4.0

        for skill in job.get("core_skills", []):
            if normalize_skill(skill) in resume_skills or normalize_skill(skill) in resume_tokens:
                score += 3.0

        domain_scores[domain] = domain_scores.get(domain, 0) + score

    if not domain_scores:
        return "Unknown"

    return max(domain_scores.items(), key=lambda x: x[1])[0]

def infer_seniority_from_resume(resume):
    """
    Infers seniority level from resume experience.
    """
    years = resume.get("experience_years", -1)

    if years == -1:
        return "Unknown"
    if years < 1:
        return "Intern / Fresher"
    if years <= 2:
        return "Junior"
    if years <= 5:
        return "Mid"
    if years <= 9:
        return "Senior"
    return "Lead"

def infer_seniority_from_language(resume_text: str) -> str:
    """
    Infers seniority hints from resume language.
    Soft signal only.
    """
    if not resume_text:
        return "Unknown"

    text = resume_text.lower()

    senior_signals = [
        "lead", "leading", "architect", "architecture",
        "mentored", "mentoring", "ownership",
        "designed system", "scalable system"
    ]

    mid_signals = [
        "independently", "end to end", "responsible for",
        "developed", "implemented", "production"
    ]

    entry_signals = [
        "intern", "internship", "trainee",
        "fresher", "junior", "student"
    ]

    if any(s in text for s in senior_signals):
        return "Senior"

    if any(s in text for s in mid_signals):
        return "Mid"

    if any(s in text for s in entry_signals):
        return "Entry"

    return "Unknown"

def reconcile_seniority(experience_years: int,
                         language_hint: str,
                         role_expectation: dict) -> str:
    """
    Reconciles experience, resume language, and role expectations
    into a final seniority label.
    """

    # --- BASE SENIORITY FROM EXPERIENCE ---
    if experience_years == -1:
        base = "Unknown"
    elif experience_years <= 1:
        base = "Entry"
    elif experience_years <= 5:
        base = "Mid"
    elif experience_years <= 9:
        base = "Senior"
    else:
        base = "Lead"

    # --- SOFT ADJUSTMENT FROM LANGUAGE ---
    ladder = ["Entry", "Mid", "Senior", "Lead"]

    if base in ladder and language_hint in ladder:
        base_idx = ladder.index(base)
        hint_idx = ladder.index(language_hint)

        # allow movement by ONE step only
        if hint_idx == base_idx + 1:
            base = ladder[base_idx + 1]
        elif hint_idx == base_idx - 1:
            base = ladder[base_idx - 1]

    # --- ROLE EXPECTATION BOUNDING ---
    if role_expectation:
        for level, bounds in role_expectation.items():
            min_exp = bounds.get("min", 0)
            max_exp = bounds.get("max", float("inf"))

            if min_exp <= experience_years <= max_exp:
                return level.capitalize()

    return base

def build_fit_reasons(resume, job, score, seniority, inferred_count=0):
    """
    Generates human-readable reasons for fit / mismatch.
    """
    reasons = []
    rejects = []

    resume_skills = set(normalize_skill(s) for s in resume.get("skills", []))
    years = resume.get("experience_years", -1)

    # --- SKILLS ---
    matched_critical = [
        s for s in job.get("critical_skills", [])
        if normalize_skill(s) in resume_skills
    ]

    if matched_critical:
        reasons.append(
            f"Matched critical skills: {', '.join(matched_critical)}"
        )
    else:
        rejects.append("No critical skills matched")

    if inferred_count > 0:
        reasons.append(
        f"Inferred finance experience from resume context ({inferred_count} signals)"
    )


    # --- EXPERIENCE ---
    job_exp = job.get("experience", {})
    min_years = job_exp.get("min_years", -1)

    if min_years != -1 and years != -1:
        if years >= min_years:
            reasons.append(
                f"Experience meets requirement ({years} years)"
            )
        else:
            rejects.append(
                f"Experience below requirement ({years} < {min_years} years)"
            )

    # --- SENIORITY ---
    if seniority != "Unknown":
        reasons.append(f"Seniority inferred as {seniority}")

    # --- DISCRIMINATORS ---
    disc = job.get("discriminators", {})
    if disc.get("must_have_both"):
        reasons.append("Passed Full-Stack hard skill gate")

    return reasons, rejects

def build_comparison_reasons(resume, best_job, all_jobs):
    """
    Explains why other roles were not selected.
    """
    reasons = []

    resume_skills = set(normalize_skill(s) for s in resume.get("skills", []))
    resume_text = resume.get("text", "").lower()

    for job in all_jobs.values():
        if job["title"] == best_job["title"]:
            continue

        disc = job.get("discriminators", {})

        # --- MUST HAVE BOTH ---
        must_have_both = disc.get("must_have_both", [])
        for pair in must_have_both:
            if not any(
                normalize_skill(p) in resume_skills or p in resume_text
                for p in pair
            ):
                reasons.append({
                    "role": job["title"],
                    "reason": f"Rejected: missing required skill pair ({' / '.join(pair)})"
                })
                break

        # --- SHOULD NOT HAVE PRIMARY ---
        should_not = disc.get("should_not_have_primary", [])
        for s in should_not:
            if normalize_skill(s) in resume_skills or s in resume_text:
                reasons.append({
                    "role": job["title"],
                    "reason": f"Rejected: conflicting primary skill ({s})"
                })
                break

    return reasons

def explain_job_loss(job, score, best_score):
    """
    Generates human-readable reason why this job lost.
    """
    reasons = []

    if score < best_score * 0.7:
        reasons.append("Significantly weaker skill match")

    if job.get("critical_skills"):
        reasons.append("Missing or partial critical skills")

    return reasons or ["Lower overall relevance"]



def infer_job_from_resume(resume):
    """
    Infers best-fit job & domain based ONLY on resume content.
    """

    jobs = load_all_jobs()

    # --- STAGE 1: DOMAIN ---
    best_domain = infer_domain_from_resume(resume, jobs)

    resume_skills = set(normalize_skill(s) for s in resume.get("skills", []))

    # 🔹 Finance implicit enrichment
    finance_inferred = enrich_finance_skills(resume)
    resume_skills |= finance_inferred
    inferred_count = len(finance_inferred)

    resume_text = resume.get("text", "").lower()

    import re
    raw_tokens = re.findall(r"[a-z0-9+.#]+", resume_text)
    resume_tokens = set(normalize_skill(t) for t in raw_tokens)

    for i in range(len(raw_tokens) - 1):
        resume_tokens.add(normalize_skill(raw_tokens[i] + raw_tokens[i + 1]))

    scored_jobs = []
    rejected_jobs = []

    # ============================
    # JOB SCORING LOOP
    # ============================
    for job in jobs.values():

        if best_domain != "Unknown" and job["domain"] != best_domain:
             domain_penalty = 0.4
        else:
             domain_penalty = 1.0


        hard_reasons = check_hard_rejection(resume, job)

        if hard_reasons:
            rejected_jobs.append({
                "job": job,
                "reasons": hard_reasons
            })
            continue

        # --- FINANCE TOOL INFERENCE (SOFT SIGNAL) ---
        if best_domain == "Finance":
         if "report" in resume_text or "spreadsheet" in resume_text:
           resume_tokens.add("excel")

         if "accounting software" in resume_text:
            resume_tokens.update(["tally", "quickbooks"])

        score = 0.0

        for skill in job.get("critical_skills", []):
            if normalize_skill(skill) in resume_skills or normalize_skill(skill) in resume_tokens:
                score += 4.0

        for skill in job.get("core_skills", []):
            if normalize_skill(skill) in resume_skills or normalize_skill(skill) in resume_tokens:
                score += 3.0

        for skill in job.get("optional_skills", []):
            if normalize_skill(skill) in resume_skills or normalize_skill(skill) in resume_tokens:
                score += 1.0

        for skill in job.get("soft_skills", []):
            if normalize_skill(skill) in resume_tokens:
                score += 0.5

        score += validate_seniority(job, resume.get("experience_years", -1))
        score += apply_role_discriminators(resume, job)

        total_possible = (
            4 * len(job.get("critical_skills", [])) +
            3 * len(job.get("core_skills", [])) +
            1 * len(job.get("optional_skills", [])) +
            0.5 * len(job.get("soft_skills", []))
        )

        normalized_score = score / total_possible if total_possible > 0 else 0.0
        normalized_score *= domain_penalty

        # 🔹 Soft boost for inferred finance skills (cap at +0.15)
        if inferred_count > 0:
         normalized_score += min(0.05 * inferred_count, 0.15)

        normalized_score = apply_discriminators(normalized_score, job, resume_tokens)

        # --- DOMAIN CALIBRATION ---
        DOMAIN_CALIBRATION = {
         "Technology": 1.0,
         "Finance": 1.25,
         "Design": 1.2,
         "Healthcare": 1.15,
         "Education": 1.1
        }

        normalized_score *= DOMAIN_CALIBRATION.get(best_domain, 1.0)

        # Clamp to valid range
        normalized_score = max(min(normalized_score, 1.0), 0.0)


        scored_jobs.append((normalized_score, job))
    # ============================
    # NO VALID JOBS → HARD REJECT
    # ============================
    if not scored_jobs:
        return normalize_inference_output({
          "job_title": "Rejected",
          "domain": best_domain,
          "confidence": 0.0,
          "confidence_band": "Rejected",
          "seniority": infer_seniority_from_resume(resume),
          "rejection_reasons": list(
             set(r for j in rejected_jobs for r in j["reasons"])
          ),
          "fit_reasons": [],
          "compared_against": []
        })


    # ============================
    # PICK BEST VALID JOB
    # ============================
    scored_jobs.sort(key=lambda x: x[0], reverse=True)
    best_score, best_job = scored_jobs[0]

    calibrated = calibrate_confidence(best_score)

    # ============================
    # COMPARE AGAINST OTHERS
    # ============================
    TOP_K = 3
    compared_against = []

    for score, job in scored_jobs[1:TOP_K]:
     compared_against.append({
         "job_title": job["title"],
         "confidence": round(score * 100, 1),  # real percentage
         "reason": explain_job_loss(job, score, best_score)
        })


    # ============================
    # SENIORITY
    # ============================
    language_hint = infer_seniority_from_language(resume_text)
    final_seniority = reconcile_seniority(
        resume.get("experience_years", -1),
        language_hint,
        best_job.get("seniority_expectation", {})
    )

    fit_reasons, rejection_reasons = build_fit_reasons(
        resume,
        best_job,
        round(calibrated["score"] * 100, 1),
        final_seniority,
        inferred_count
    )

    return normalize_inference_output({
       "job_title": best_job["title"],
       "domain": best_domain,
       "confidence": round(calibrated["score"] * 100, 1),
       "confidence_band": calibrated["band"],
       "seniority": final_seniority,
       "fit_reasons": fit_reasons,
       "rejection_reasons": rejection_reasons,
       "compared_against": compared_against
    })






