import streamlit as st
from pathlib import Path
import tempfile

# -----------------------------
# BACKEND IMPORTS
# -----------------------------
from resume_parser.parser import parse_resume
from job_profile.jd_profiler import build_job_profile_from_jd
from ranking.jd_ranker import rank_resumes_against_jd
from analysis.rejection_feedback import generate_rejection_feedback
from utils.export_utils import export_to_csv

def show_if_known_badge(value, color="info"):
    if value and value not in ["Unknown", -1, [], {}]:
        if color == "error":
            st.error(value)
        elif color == "success":
            st.success(value)
        elif color == "warning":
            st.warning(value)
        else:
            st.info(value)


# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Recruiter ATS Dashboard",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Recruiter ATS Dashboard")
st.caption("Paste job requirements • Auto-detect role • Rank candidates")
st.divider()

# -----------------------------
# SIDEBAR INPUTS (UNCHANGED)
# -----------------------------
with st.sidebar:
    st.header("📄 Upload Resumes")
    uploaded_resumes = st.file_uploader(
        "Upload PDF resumes",
        type=["pdf"],
        accept_multiple_files=True
    )

    st.divider()

    # -----------------------------
    # JOB REQUIREMENTS CARD
    # -----------------------------
    st.header("📝 Job Requirements")

    if "jd_locked" not in st.session_state:
        st.session_state.jd_locked = False
    if "jd_text" not in st.session_state:
        st.session_state.jd_text = ""

    if not st.session_state.jd_locked:
        st.caption("Paste skills, tools, responsibilities, requirements")

        jd_input = st.text_area(
            "Enter Job Description",
            height=200,
            placeholder=(
                "Example:\n"
                "- 0–3 years experience in web development\n"
                "- HTML, CSS, JavaScript, React\n"
                "- REST APIs, Git\n"
                "- Strong communication skills"
            ),
            key="jd_editor"
        )

        if st.button("🔒 Lock Job Description", use_container_width=True):
            if jd_input.strip():
                st.session_state.jd_text = jd_input
                st.session_state.jd_locked = True
                st.rerun()
            else:
                st.warning("Please enter a job description first.")

    else:
        st.success("Job Description Locked")
        st.text_area(
            "Locked Job Description",
            value=st.session_state.jd_text,
            height=200,
            disabled=True
        )

        if st.button("✏️ Edit Job Description", use_container_width=True):
            st.session_state.jd_locked = False
            st.rerun()

    st.divider()

    st.markdown("### 🎯 Shortlist Threshold")
    SHORTLIST_THRESHOLD = st.slider("", 30, 95, 60, 5)

# -----------------------------
# VALIDATION
# -----------------------------
job_text = st.session_state.get("jd_text", "")

if not uploaded_resumes or not st.session_state.jd_locked:
    st.info("👈 Upload resumes and lock a job description to begin")
    st.stop()


# -----------------------------
# BUILD JD PROFILE (JD → KEYWORDS → JOB LABEL)
# -----------------------------
jd_profile = build_job_profile_from_jd(job_text)

st.subheader("🎯 Job Detected From Your Description")
st.success(f"{jd_profile['job_title']}  —  {jd_profile['domain']}")
st.divider()

# -----------------------------
# PARSE RESUMES (SAFE STRUCTURE)
# -----------------------------
parsed_resumes = []

with st.spinner("📄 Parsing resumes..."):
    for file in uploaded_resumes:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tf:
            tf.write(file.read())
            resume_path = Path(tf.name)

        resume_data = parse_resume(resume_path)

        parsed_resumes.append({
            "filename": file.name,   # 🔑 REQUIRED by jd_ranker
            "resume": resume_data
        })

# -----------------------------
# SCORE RESUMES VS JD ONLY
# -----------------------------
results = rank_resumes_against_jd(
    resumes=parsed_resumes,
    jd_profile=jd_profile,
    shortlist_threshold=SHORTLIST_THRESHOLD
)

# -----------------------------
# ADD ATS FEEDBACK
# -----------------------------
for r in results:
    r["feedback"] = generate_rejection_feedback(
        resume_name=r["filename"],
        score=r["score"],
        matched_skills=r["matched_skills"],
        missing_skills=r["missing_skills"],
        threshold=SHORTLIST_THRESHOLD
    )

# -----------------------------
# RANKED CANDIDATES UI (UNCHANGED)
# -----------------------------
st.header("🏅 Ranked Candidates")

def columns_for(n):
    if n <= 1: return 1
    if n <= 2: return 2
    if n <= 4: return 3
    return 4

cols_per_row = columns_for(len(results))
rows = [results[i:i + cols_per_row] for i in range(0, len(results), cols_per_row)]

rank = 1
for row in rows:
    cols = st.columns(cols_per_row)
    for col, r in zip(cols, row):
        with col:
            shortlisted = r["score"] >= SHORTLIST_THRESHOLD
            status_icon = "🟢" if shortlisted else "🔴"
            status_text = "Shortlisted" if shortlisted else "Rejected"

            with st.container(border=True):
                st.subheader(f"🏅 #{rank} — {r['filename']}")
                st.caption(f"{status_icon} **{status_text}**")

                st.caption(f"🎯 Best Fit Job: **{r['best_fit_job']}**")
                st.caption(f"📂 Domain: **{r['domain']}**")

                band = r.get("confidence_band", "Unknown")

                if band == "Strong Fit":
                 st.success("Algo Confidence: Strong Fit for this JD")
                elif band == "Good Fit":
                 st.info("Algo Confidence: Good Fit for this JD")
                elif band == "Borderline":
                 st.warning("Algo Confidence: Borderline Fit for this JD")
                elif band == "Weak Fit":
                 st.warning("Algo Confidence: Weak Fit for this JD")

                edu_match = r.get("education_match", "not_required")
                jd_requires_edu = jd_profile.get("min_education_level", -1) != -1

                if not jd_requires_edu:
                  st.info("🎓 Education: Not specified in JD")

                else:
                    if edu_match == "meets":
                        st.success("🎓 Education: Meets requirement")
                    elif edu_match == "partial":
                        st.warning("🎓 Education: Partially meets requirement")
                    elif edu_match == "missing":
                        st.error("🎓 Education: Does NOT meet requirement")
                    else:  # unknown
                        st.warning("🎓 Education: Not found in resume")

                st.divider()

                c1, c2 = st.columns(2)
                c1.metric("📊 Score (%)", f"{r['score']:.1f}")
                c2.metric("🚀 Potential (%)", f"{r['improvement_score']:.1f}")

                st.progress(min(r["score"] / 100, 1.0))
                st.progress(min(r["improvement_score"] / 100, 1.0))

                fit_reasons = r.get("fit_reasons", [])

                if fit_reasons:
                    st.markdown("### ✅ Why this fits")
                    for reason in fit_reasons:
                        st.write("•", reason)

                rejections = r.get("rejection_reasons", [])

                if rejections:
                    st.markdown("### ❌ Rejection reasons")
                    for reason in rejections:
                        st.error(reason)

                st.markdown("### ✅ Matched Skills")
                st.success(", ".join(r["matched_skills"]) if r["matched_skills"] else "None")

                st.markdown("### ❌ Missing Skills")
                st.warning(", ".join(r["missing_skills"]) if r["missing_skills"] else "None")

                compared = r.get("compared_against", [])
                 
                
                if compared:
                 with st.expander("🔍 Compared against other roles"):
                  for c in compared:
                   conf = c["confidence"]

                   if conf <= 5:
                     conf_text = "Very Low Match"
                   else:
                     conf_text = f"{conf:.1f}%"

                   st.write(
                        f"• **{c['job_title']}** — {c['confidence']}% fit"
                    )    




                with st.expander("🧠 ATS Feedback"):
                    suggestions = r["feedback"].get("suggestions", [])
                    if suggestions:
                        for s in suggestions:
                            st.write("•", s)
                    else:
                        st.success("Resume is ATS optimized")

        rank += 1

# -----------------------------
# SHORTLIST SUMMARY
# -----------------------------
shortlisted = [r for r in results if r["score"] >= SHORTLIST_THRESHOLD]
st.divider()
st.success(f"✅ Shortlisted {len(shortlisted)} / {len(results)} candidates (≥ {SHORTLIST_THRESHOLD}%)")

# -----------------------------
# EXPORT CSV
# -----------------------------
output_path = Path("output/resume_ranking.csv")
output_path.parent.mkdir(exist_ok=True)
export_to_csv(results, output_path, SHORTLIST_THRESHOLD)

with open(output_path, "rb") as f:
    st.download_button(
        "📥 Download Ranking CSV",
        f,
        file_name="resume_ranking.csv",
        mime="text/csv"
    )
