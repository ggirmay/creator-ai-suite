import streamlit as st
import requests
import os

st.set_page_config(
    page_title="EDGE — Your Business Coach",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .main .block-container {padding-top:1.5rem;padding-bottom:1rem;max-width:720px;}
  .edge-header {
    background: linear-gradient(135deg, #1A237E 0%, #283593 100%);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
  }
  .edge-header h3 {margin:0 0 4px 0;font-size:1.1rem;color:white;}
  .edge-header p {margin:0;font-size:0.83rem;color:rgba(255,255,255,0.85);}
  .mode-badge {
    background:#E8EAF6;border-left:4px solid #1A237E;
    border-radius:0 8px 8px 0;padding:10px 14px;
    margin-bottom:16px;font-size:0.86rem;color:#1A237E;
  }
  .more-box {
    background:#E8EAF6;border-left:4px solid #3949AB;
    border-radius:0 8px 8px 0;padding:10px 14px;margin-top:10px;
    font-size:0.84rem;color:#1A237E;
  }
</style>
""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────────────────────
def get_api_key():
    try:
        k = st.secrets.get("ANTHROPIC_API_KEY", "")
        if k: return k
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")

def call_claude(messages, system_prompt, max_tokens=220):
    api_key = get_api_key()
    if not api_key:
        return "EDGE:\nSomething went wrong on my end — ask your facilitator to check the setup.", False
    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "Content-Type": "application/json",
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": max_tokens,
                "system": system_prompt,
                "messages": [
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                    if m["role"] in ["user", "assistant"]
                ]
            },
            timeout=30
        )
        if resp.status_code != 200:
            return "EDGE:\nSomething went wrong — try again in a moment.", False
        data = resp.json()
        reply = data["content"][0]["text"]
        cut_off = data.get("stop_reason", "end_turn") == "max_tokens"
        if cut_off:
            reply = reply.rstrip() + "..."
        return reply, cut_off
    except Exception:
        return "EDGE:\nSomething went wrong — try again in a moment.", False

# ── MODES ─────────────────────────────────────────────────────────────────────
MODES = {
    "pitch_practice": {
        "label": "🎯 Pitch Practice",
        "description": "Give EDGE your pitch. EDGE responds like a real person hearing it.",
        "opening": "Hi! I am EDGE, your business thinking partner. Go ahead and give me your pitch — pretend I am someone you just met who might want to read your ebook.",
        "system_addon": """
The child is practising their pitch. Play the role of a friendly but honest adult browsing online.
React genuinely in 2 sentences as that person would. Then ask one question.
Start every response with "EDGE:" on its own line. Maximum 3 sentences total.
"""
    },
    "offer_check": {
        "label": "📦 Check My Offer",
        "description": "Tell EDGE what you are selling. EDGE checks it is clear and simple.",
        "opening": "Hi! I am EDGE, your business thinking partner. Tell me about your offer — what it is, what it costs, and how someone gets it after paying.",
        "system_addon": """
Listen to the offer. Respond to the ONE most important thing that is unclear.
Ask one warm question about it.
Start every response with "EDGE:" on its own line. Maximum 3 sentences total.
When everything is clear — say so warmly and briefly.
"""
    },
    "value_check": {
        "label": "💡 Check My Value Statement",
        "description": "Share what your ebook gives someone. EDGE checks it sounds like the reader.",
        "opening": "Hi! I am EDGE, your business thinking partner. Share your value statement — the sentences describing what someone gets from reading your ebook.",
        "system_addon": """
Read the value statement. Pick ONE thing — does it sound like the reader or the writer?
Respond warmly. Ask one question.
Start every response with "EDGE:" on its own line. Maximum 3 sentences total.
"""
    },
    "rejection_coach": {
        "label": "🛡️ Someone Said No",
        "description": "Tell EDGE what happened. EDGE helps you understand what the no means.",
        "opening": "Hi! I am EDGE, your business thinking partner. Tell me what happened — who said no, what they said, and how it felt.",
        "system_addon": """
Acknowledge the feeling first — warmly, in one sentence.
Then gently offer one reframe. Then ask one question.
Start every response with "EDGE:" on its own line. Maximum 3 sentences total.
"""
    },
    "opportunity_map": {
        "label": "🗺️ Map My Opportunity",
        "description": "Tell EDGE about your ebook. EDGE helps you see the business opportunity you built.",
        "opening": "Hi! I am EDGE, your business thinking partner. Tell me about your ebook — what it is, who it is for, and what you learned making it.",
        "system_addon": """
Listen to what they share. Reflect one thing back that reframes it positively.
Ask one natural question about who they made it for or why they are the right person.
Start every response with "EDGE:" on its own line. Maximum 3 sentences total.
"""
    }
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💼 What can EDGE do?")
    st.markdown("---")
    for key, mode in MODES.items():
        st.markdown(f"**{mode['label']}**")
        st.caption(mode['description'])
        st.markdown("")
    st.markdown("---")
    st.caption("EDGE helps you think like an entrepreneur — never tells you what to do, helps you figure it out yourself.")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="edge-header">
  <h3>💼 EDGE — Your Business Coach</h3>
  <p>Pitch practice · Offer check · Value statement · Rejection support · Opportunity mapping</p>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────────────
selected_mode_key = st.selectbox(
    "What do you need help with today?",
    options=list(MODES.keys()),
    format_func=lambda k: MODES[k]["label"],
    key="mode_selector"
)
selected_mode = MODES[selected_mode_key]

if "current_mode" not in st.session_state:
    st.session_state.current_mode = selected_mode_key
if st.session_state.current_mode != selected_mode_key:
    st.session_state.current_mode = selected_mode_key
    st.session_state.messages = []
    st.session_state.was_cut_off = False

st.markdown(f'<div class="mode-badge">{selected_mode["description"]}</div>',
            unsafe_allow_html=True)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""Your name is EDGE. You are the business thinking partner for the CREATOR programme for children aged 10-13.

WHO YOU ARE:
Warm, encouraging, and genuinely excited about what this child has built.
You talk like a supportive mentor who believes in young people.
You take the child seriously as a real entrepreneur — never talk down to them.

CRITICAL FORMATTING RULES — THESE ARE NON-NEGOTIABLE:
- Start EVERY response with "EDGE:" on its own line. Always. Without exception.
- Do NOT sign off at the end. No "— EDGE". Just start with "EDGE:" and write naturally.
- Maximum 3 sentences per response. If you need more — pick the most important thing only.
- One question per response. Never two.
- No bullet points. No headers. No lists. Just warm sentences.
- Complete every sentence — never stop mid-thought.
- If you are running close to your limit — wrap up your thought in the current sentence.

EXAMPLE of correct format:
EDGE:
That is a really honest answer — and it takes courage to say it out loud. What would you change about the pitch if you did it again right now?

LANGUAGE:
Simple words. Grade 5-6 level. Direct and warm.
No business jargon — say "the people you want to buy it" not "your target market".
Never say: amazing, great work, fantastic.

NEVER:
- Overwhelm with multiple questions
- Make them feel tested or marked
- Give a list of things to fix

ALWAYS:
- Acknowledge feelings before frameworks — especially with rejection
- Make them feel what they built is genuinely impressive
- Celebrate specifically — not generically

CREATOR CONTEXT YOU KNOW:
They have written a published ebook, built a website, found real people who connected with their work.
They are now learning to offer their work for money for the first time. That takes real courage.

{selected_mode['system_addon']}

PARENT VISIBILITY: Parents may read these conversations. Always behave accordingly.
"""

# ── INIT CHAT ─────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "was_cut_off" not in st.session_state:
    st.session_state.was_cut_off = False

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"EDGE:\n{selected_mode['opening']}"
    })

# ── DISPLAY MESSAGES ──────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── CUTOFF — CONTINUE BUTTON ──────────────────────────────────────────────────
if st.session_state.was_cut_off:
    st.markdown("""
    <div class="more-box">
      💼 EDGE has a bit more to say — click below whenever you are ready.
    </div>
    """, unsafe_allow_html=True)
    if st.button("Continue ➜", key="continue_btn"):
        st.session_state.was_cut_off = False
        st.session_state.messages.append({
            "role": "user",
            "content": "Please continue."
        })
        with st.chat_message("assistant"):
            with st.spinner("EDGE is continuing..."):
                reply, cut_off = call_claude(
                    st.session_state.messages, SYSTEM_PROMPT
                )
            st.markdown(reply)
            st.session_state.was_cut_off = cut_off
        st.session_state.messages.append({
            "role": "assistant", "content": reply
        })
        st.rerun()

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
placeholders = {
    "pitch_practice":   "Give me your pitch here...",
    "offer_check":      "Describe your offer — what it is, what it costs, how someone gets it...",
    "value_check":      "Paste your value statement here...",
    "rejection_coach":  "Tell me what happened...",
    "opportunity_map":  "Tell me about your ebook and your CREATOR journey..."
}

if prompt := st.chat_input(placeholders.get(selected_mode_key, "Type here...")):
    st.session_state.was_cut_off = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("EDGE is thinking..."):
            reply, cut_off = call_claude(
                st.session_state.messages, SYSTEM_PROMPT
            )
        st.markdown(reply)
        if cut_off:
            st.markdown("""
            <div class="more-box">
              💼 EDGE has a bit more to say — click Continue above when ready.
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.was_cut_off = cut_off
    if cut_off:
        st.rerun()

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.72rem;color:#999;'>"
    "EDGE · CREATOR Framework · Phase O · Ages 10–13 · "
    "Conversations may be reviewed by your facilitator</p>",
    unsafe_allow_html=True
)
