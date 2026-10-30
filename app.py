import os
import streamlit as st
import requests
from therapist_matcher import find_therapists

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="MindMate | Emotional Wellness",
    page_icon="💙",
    layout="wide"
)

# ---------------- AI CONFIGURATION ----------------

# On Streamlit Cloud, add GROQ_API_KEY under App settings > Secrets.
# On your own laptop, MindMate falls back to your local Ollama installation.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

try:
    GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", GROQ_API_KEY)
except Exception:
    pass

GROQ_MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """
You are MindMate, an empathetic emotional support companion.

Listen without judging. Understand the user's emotions.
Ask meaningful follow-up questions and remember the conversation context.
Suggest safe coping strategies and offer guided reflection and relaxation exercises.
Never diagnose mental health conditions or prescribe medication.
Never claim to be a licensed therapist or replace professional care.
Encourage professional help when appropriate.
If the user may be in immediate danger or at risk of harming themselves or someone else,
encourage them to contact local emergency services or a trusted person immediately.
Respond naturally, warmly, clearly and conversationally.
"""

# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp { background-color: #F4F8FC; }
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1150px;
}
h1, h2, h3 { color: #183B56; }
.subtitle { color: #648096; font-size: 17px; }
.hero {
    background: linear-gradient(120deg, #DCEEFF, #EAF6F7);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 25px;
}
div.stButton > button {
    background-color: #2878A8;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
}
div.stButton > button:hover {
    background-color: #185C85;
    color: white;
}
[data-testid="stChatMessage"] {
    background-color: white;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #E4EDF4;
}
[data-testid="stSidebar"] { background-color: #EAF3FA; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("# 💙 MindMate")
    st.caption("Your emotional wellness companion")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        ["Home", "Talk to MindMate", "Find a Therapist"]
    )

    st.divider()
    st.markdown("### 🌱 A gentle reminder")
    st.write(
        "Taking care of your emotional well-being "
        "is just as important as taking care of your body."
    )
    st.caption("AI support is not a substitute for professional care.")

# ---------------- HOME PAGE ----------------

if page == "Home":
    st.markdown("""
    <div class="hero">
        <h1>Welcome to MindMate 💙</h1>
        <p class="subtitle">
            A supportive space to express your feelings,
            explore your emotions and find the right help.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("How can we support you today?")
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown("### 💬 Talk to MindMate")
            st.write(
                "Share what's on your mind and have "
                "a supportive conversation with your AI companion."
            )

    with col2:
        with st.container(border=True):
            st.markdown("### 👩‍⚕️ Find a Therapist")
            st.write(
                "Explore professional support based on "
                "your location, language and preferences."
            )

    st.divider()
    st.subheader("What MindMate offers")
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 💙")
        st.markdown("**Emotional Support**")
        st.caption("A space to express your thoughts without judgement.")

    with c2:
        st.markdown("### 🌿")
        st.markdown("**Guided Exercises**")
        st.caption("Explore relaxation, reflection and coping techniques.")

    with c3:
        st.markdown("### 🤝")
        st.markdown("**Professional Help**")
        st.caption("Find qualified mental health professionals.")

# ---------------- CHAT PAGE ----------------

elif page == "Talk to MindMate":
    st.title("💬 Talk to MindMate")
    st.markdown(
        '<p class="subtitle">You can share whatever is on your mind. '
        'I am here to listen.</p>',
        unsafe_allow_html=True
    )

    if GROQ_API_KEY:
        st.info(
            "Privacy notice: When you use this chat, your messages and "
            "recent conversation context are sent to Groq's API to generate "
            "replies. Do not share information you are not comfortable "
            "sending to an external AI service."
        )
        consent_to_cloud = st.checkbox(
            "I understand that my chat messages will be sent to Groq to generate replies."
        )
    else:
        st.info(
            "Local mode: MindMate will use Ollama running on this computer. "
            "Your chat is kept in this browser session and is not saved by "
            "this app to a database."
        )
        consent_to_cloud = True

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    prompt = st.chat_input(
        "What's on your mind?",
        disabled=bool(GROQ_API_KEY) and not consent_to_cloud
    )

    if prompt:
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("MindMate is listening..."):
                try:
                    if GROQ_API_KEY:
                        messages = [
                            {"role": "system", "content": SYSTEM_PROMPT}
                        ] + st.session_state.messages[-10:]

                        response = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {GROQ_API_KEY}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": GROQ_MODEL,
                                "messages": messages,
                                "temperature": 0.7,
                                "max_completion_tokens": 700
                            },
                            timeout=120
                        )
                        response.raise_for_status()
                        reply = response.json()["choices"][0]["message"]["content"]

                    else:
                        conversation = SYSTEM_PROMPT + "\n"
                        for msg in st.session_state.messages[-10:]:
                            conversation += (
                                msg["role"] + ": " + msg["content"] + "\n"
                            )

                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": "llama3.2:1b",
                                "prompt": conversation,
                                "stream": False
                            },
                            timeout=180
                        )
                        response.raise_for_status()
                        reply = response.json()["response"]

                except requests.HTTPError as error:
                    details = ""
                    try:
                        details = error.response.text
                    except Exception:
                        pass
                    reply = (
                        "I couldn't get a response from the AI service. "
                        "Please try again later. "
                        + details[:500]
                    )
                except requests.RequestException:
                    if GROQ_API_KEY:
                        reply = (
                            "I couldn't connect to Groq. Please check the "
                            "deployment's API key and try again."
                        )
                    else:
                        reply = (
                            "I'm having trouble connecting. Please check "
                            "whether Ollama is running on your computer."
                        )
                except (KeyError, TypeError, ValueError):
                    reply = (
                        "The AI service returned an unexpected response. "
                        "Please try again."
                    )

                st.write(reply)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply
        })

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# ---------------- THERAPIST PAGE ----------------

elif page == "Find a Therapist":
    st.title("👩‍⚕️ Find the Right Professional")
    st.markdown(
        '<p class="subtitle">Explore professional mental health '
        'support based on your preferences.</p>',
        unsafe_allow_html=True
    )

    st.info(
        "Therapist recommendations are optional. "
        "Your preferences help us filter available directory listings. "
        "Please independently confirm credentials, fees and availability."
    )

    with st.form("therapist_form"):
        st.subheader("Your Preferences")

        location = st.text_input(
            "Preferred location",
            placeholder="Example: Bengaluru"
        )

        specialization = st.selectbox(
            "Area of support",
            [
                "Any", "Anxiety", "Depression", "Stress",
                "Relationship Issues", "Family Issues", "Trauma"
            ]
        )

        language = st.selectbox(
            "Preferred language",
            ["Any", "English", "Kannada", "Hindi", "Tamil", "Telugu"]
        )

        max_fee = st.number_input(
            "Maximum consultation fee (₹)",
            min_value=0,
            value=1000,
            step=100
        )

        consent = st.checkbox(
            "I agree to use these preferences to search the therapist directory."
        )

        submitted = st.form_submit_button(
            "Find Matching Therapists",
            use_container_width=True
        )

    if submitted:
        if not consent:
            st.warning("Please provide consent before searching.")
        else:
            try:
                matches = find_therapists(
                    location=location if location else None,
                    specialization=(
                        specialization if specialization != "Any" else None
                    ),
                    language=language if language != "Any" else None,
                    max_fee=max_fee
                )

                st.divider()

                if matches:
                    st.subheader("Matching Professionals")

                    for therapist in matches:
                        with st.container(border=True):
                            st.subheader(
                                "👩‍⚕️ " + therapist.get("name", "Name unavailable")
                            )
                            st.write(
                                "**Qualification:**",
                                therapist.get("qualification", "Not provided")
                            )
                            st.write(
                                "**Registration:**",
                                therapist.get("registration", "Not provided")
                            )
                            st.write(
                                "**Location:**",
                                therapist.get("location", "Not provided")
                            )
                            st.write(
                                "**Specialisations:**",
                                ", ".join(therapist.get("specializations", []))
                            )
                            st.write(
                                "**Languages:**",
                                ", ".join(therapist.get("languages", []))
                            )

                            fee = therapist.get("fee")
                            if fee is None or fee == 0:
                                st.write("**Consultation Fee:** Not verified")
                            else:
                                st.write(f"**Consultation Fee:** ₹{fee}")

                            st.write(
                                "**Availability:**",
                                therapist.get("availability", "Not verified")
                            )

                            source = therapist.get("source_url")
                            if source:
                                st.link_button("View Professional Profile", source)
                else:
                    st.warning(
                        "No matching professionals were found in the current directory."
                    )

            except (FileNotFoundError, ValueError, KeyError, TypeError) as error:
                st.error(
                    "There is a problem with the therapist directory: "
                    + str(error)
                )

# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "MindMate | Supporting emotional well-being 💙 "
    "| Not a replacement for professional mental healthcare."
)
