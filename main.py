import streamlit as st
import re
import string
import random
from datetime import datetime

# Common passwords list (for demonstration - use a more comprehensive list in production)
COMMON_PASSWORDS = [
    'password', '123456', 'qwerty', 'abc123', 'letmein', 'admin', 'welcome',
    'monkey', 'password1', '12345678', '123456789', 'baseball', 'football',
    'jennifer', 'iloveyou', '1234567', '1234567890', 'superman', 'sunshine'
]

def generate_password(length=12, include_special=True, include_numbers=True):
    """Generate a strong random password"""
    characters = string.ascii_letters
    if include_numbers:
        characters += string.digits
    if include_special:
        characters += string.punctuation

    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
    ]
    
    if include_numbers:
        password.append(random.choice(string.digits))
    if include_special:
        password.append(random.choice(string.punctuation))

    for _ in range(length - len(password)):
        password.append(random.choice(characters))

    random.shuffle(password)
    return ''.join(password)

def check_consecutive(password, max_consecutive=2):
    """Check for consecutive repeating characters"""
    consecutive_count = 1
    prev_char = password[0]
    for char in password[1:]:
        if char == prev_char:
            consecutive_count += 1
            if consecutive_count > max_consecutive:
                return True
        else:
            consecutive_count = 1
        prev_char = char
    return False

def check_sequential(password, min_seq_length=3):
    """Check for sequential characters (e.g., 'abc', '123')"""
    password_lower = password.lower()
    for i in range(len(password_lower) - min_seq_length + 1):
        slice = password_lower[i:i+min_seq_length]
        if slice in string.ascii_lowercase:
            return True
        if slice in '0123456789':
            return True
    return False

def check_date_pattern(password):
    """Check for date patterns (YYYY, YYYYMM, etc.)"""
    current_year = datetime.now().year
    for year in range(current_year - 100, current_year + 1):
        if str(year) in password:
            return True
    return False

def check_password_strength(password):
    """Evaluate password strength and return score and feedback"""
    feedback = {'positive': [], 'negative': []}
    score = 0

    # Basic checks
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in string.punctuation for c in password)

    # Length scoring
    if length >= 8:
        score += 1
        if length >= 12:
            score += 2
            feedback['positive'].append("Good password length (12+ characters)")
        else:
            feedback['positive'].append("Minimum length met (8+ characters)")
    else:
        feedback['negative'].append("Password too short (min 8 characters)")

    # Character type scoring
    type_count = sum([has_upper, has_lower, has_digit, has_special])
    if type_count >= 3:
        score += 2
        feedback['positive'].append("Good character variety")
    elif type_count >= 2:
        score += 1
        feedback['positive'].append("Moderate character variety")
    else:
        feedback['negative'].append("Add more character types (upper, lower, number, special)")

    # Deductions
    if password.lower() in [p.lower() for p in COMMON_PASSWORDS]:
        score -= 2
        feedback['negative'].append("Common password detected")

    if check_consecutive(password):
        score -= 1
        feedback['negative'].append("Consecutive repeating characters")

    if check_sequential(password):
        score -= 1
        feedback['negative'].append("Sequential characters detected")

    if check_date_pattern(password):
        score -= 1
        feedback['negative'].append("Date pattern detected")

    # Final score adjustments
    score = max(0, min(10, score + length//2))  # Cap score between 0-10

    return score, feedback

# Streamlit UI
st.set_page_config(page_title="Advanced Password Strength Meter", layout="wide")

st.title("🔒 Advanced Password Strength Meter")
st.write("Check your password strength and get suggestions for improvement")

col1, col2 = st.columns([2, 3])

with col1:
    password = st.text_input("Enter password:", type="password")
    generate = st.button("Generate Strong Password")
    
    if generate:
        generated_pw = generate_password(length=14)
        st.text_area("Generated Password", generated_pw,)

with col2:
    if password:
        score, feedback = check_password_strength(password)
        strength = min(max(score * 10, 0), 100)
        
        st.subheader("Password Strength")
        progress = st.progress(0)
        progress.progress(strength / 100)
        
        st.write(f"**Score:** {score}/10")
        
        if score <= 3:
            st.error("Very Weak 🔴")
        elif score <= 5:
            st.warning("Weak 🟠")
        elif score <= 7:
            st.info("Moderate 🟡")
        elif score <= 9:
            st.success("Strong 🟢")
        else:
            st.success("Very Strong 🔵")

        st.subheader("Feedback")
        
        if feedback['positive']:
            st.write("**Good points:**")
            for point in feedback['positive']:
                st.success(f"✓ {point}")
        
        if feedback['negative']:
            st.write("**Areas for improvement:**")
            for point in feedback['negative']:
                st.error(f"✗ {point}")

# Tips section
st.markdown("""
### Password Creation Tips:
- Use at least 12 characters
- Combine uppercase and lowercase letters
- Include numbers and special characters (!@#$%^&*)
- Avoid common words and personal information
- Don't use repeating (aaaa) or sequential (1234) patterns
- Consider using a passphrase (e.g., 'PurpleTiger#RunsFast!2023')
""")

# To run the app:
# streamlit run password_strength_meter.py