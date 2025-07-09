import difflib

def evaluate_user_phrase(user_input, expected):
    ratio = difflib.SequenceMatcher(None, user_input.lower(), expected.lower()).ratio()
    if ratio > 0.85:
        return "✅ Excellent!"
    elif ratio > 0.6:
        return "🟡 Almost correct. Try again!"
    else:
        return "❌ Not quite right. Speak clearly and try again."
