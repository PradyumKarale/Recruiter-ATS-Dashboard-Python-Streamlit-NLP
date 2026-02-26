def get_match_for_detected_job(job_matches, detected_job):
    """
    From all job matches for a resume,
    return the one that matches the detected job.
    """
    for match in job_matches:
        if match["job_key"] == detected_job["job_key"]:
            return match

    # Fallback (should never happen)
    return job_matches[0]
