from job_profile.resume_profiler import infer_job_from_resume

# ✅ MOCK RESUME (NO PDF, NO OCR, NO POPPLER)
resume = {
  "skills": ["recruitment", "sourcing", "interviewing", "ats", "linkedin"],
  "text": """
  Accountant with 3 years experience.
  Worked on GST filing, audits, balance sheet preparation
  and statutory compliance.
  """,
  "experience_years": 3
}


print(infer_job_from_resume(resume))

