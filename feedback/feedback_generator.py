def generate_feedback(score):
    if score > 75:
        return "Strong match for the role."
    elif score > 50:
        return "Moderate match. Improve missing skills."
    else:
        return "Low match. Consider upskilling."
