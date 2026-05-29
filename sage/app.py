import streamlit as st
import requests
import os

st.set_page_config(
    page_title="SAGE — Your Story Partner",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .main .block-container {padding-top:1.5rem;padding-bottom:1rem;max-width:720px;}
  .sage-header {
    background: linear-gradient(135deg, #1B5E20 0%, #388E3C 100%);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
  }
  .sage-header h3 {margin:0 0 4px 0;font-size:1.1rem;color:white;}
  .sage-header p {margin:0;font-size:0.83rem;color:rgba(255,255,255,0.85);}
  .mode-badge {
    background:#E8F5E9;border-left:4px solid #1B5E20;
    border-radius:0 8px 8px 0;padding:10px 14px;
    margin-bottom:16px;font-size:0.86rem;color:#1B5E20;
  }
  .more-box {
    background:#F1F8E9;border-left:4px solid #558B2F;
    border-radius:0 8px 8px 0;padding:10px 14px;margin-top:10px;
    font-size:0.84rem;color:#33691E;
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
    # Brand kit and case study modes need more tokens for their final deliverable
    current_mode = st.session_state.get("current_mode", "")
    if current_mode in ["brand_kit", "case_study"]:
        max_tokens = 600
    api_key = get_api_key()
    if not api_key:
        return "SAGE:\nSomething went wrong on my end — the key is missing. Ask your facilitator to check the setup.", False
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
            return f"SAGE:\nSomething went wrong — try again in a moment.", False
        data = resp.json()
        reply = data["content"][0]["text"]
        cut_off = data.get("stop_reason", "end_turn") == "max_tokens"
        if cut_off:
            # Append a graceful closing so the child always sees a complete thought
            reply = reply.rstrip() + "..."
        return reply, cut_off
    except Exception as e:
        return "SAGE:\nSomething went wrong — try again in a moment.", False

# ── MODES ─────────────────────────────────────────────────────────────────────
MODES = {
    "story_feedback": {
        "label": "📋 Read My Story",
        "description": "Paste your story. SAGE reads it and shares one thing that worked and one question.",
        "opening": "Hi! I am SAGE, your story reading partner. Go ahead and paste your story — I am ready to read it.",
        "system_addon": """
The child has shared a story. Read it like a genuine reader.

Respond with exactly two things — no more:
1. ONE moment that landed — name it and say what it made you feel. Quote their words.
2. ONE genuine question about a choice they made.

Start your response with "SAGE:" on its own line.
Maximum 3 sentences total after that.
"""
    },
    "revision": {
        "label": "✏️ Help Me Improve It",
        "description": "Paste your story. SAGE helps you find one thing to make better — without doing it for you.",
        "opening": "Hi! I am SAGE, your story reading partner. Paste your story and I will help you find one thing to make it even better.",
        "system_addon": """
The child wants help improving their story.

Pick ONE thing — the most useful one. Name it warmly. Quote the exact part.
Ask one question about it.

Start your response with "SAGE:" on its own line.
Maximum 3 sentences total after that.
Never suggest what to write. Never list multiple things.
"""
    },
    "voice": {
        "label": "🎵 Find My Writing Voice",
        "description": "Paste two pieces of your writing. SAGE finds what is uniquely yours.",
        "opening": "Hi! I am SAGE, your story reading partner. Paste two or more pieces of your writing here — separated by a line — and I will tell you what I notice about how you write.",
        "system_addon": """
The child has shared multiple pieces of writing.

Find ONE pattern that appears across all pieces. Name it warmly. Quote a specific line.
Then ask: did you know you were doing that?

Start your response with "SAGE:" on its own line.
Maximum 3 sentences total after that.
Share only one pattern per response.
"""
    },
    "vibe_coding": {
        "label": "💻 Help Me Describe My Website",
        "description": "Tell SAGE what you want your website to feel like. SAGE helps you put it into words.",
        "opening": "Hi! I am SAGE, your story reading partner. Tell me what you want your website to look and feel like — I will help you describe it properly.",
        "system_addon": """
Help the child describe their website for a builder tool like Framer or Webflow.

Ask ONE question at a time — never a list.
After 4-5 questions write a short plain-English description they can paste into the builder.

Start every response with "SAGE:" on its own line.
Maximum 3 sentences per response until you write the final description.
"""
    },
    "brand_kit": {
        "label": "🎨 Build My Brand Kit",
        "description": "Tell SAGE about your creator identity. SAGE helps you choose colours, fonts, and image style that actually match who you are.",
        "opening": "Hi! I am SAGE, your story reading partner. Let us build your brand kit together — I am going to ask you a few questions and help you choose colours, fonts, and a style that actually feels like you.",
        "system_addon": """
The child needs to build their brand kit from Phase A — Session A-04.
This means choosing 2-3 colours with hex codes, one font pair, and one image style.

Have a warm creative conversation. Ask ONE question at a time.

QUESTION SEQUENCE — follow this order, one question per response:

1. "What feeling do you want someone to get in the very first second of seeing your work — before they read a single word?"

2. "Think about your ebook and your stories. If your writing had a colour — what colour would it be? Does not have to be one you would normally pick. Just what feels right."

3. "When you think of creators or artists you admire — what does their visual world look like? Clean and minimal? Rich and layered? Bold and bright? Soft and quiet?"

4. "Do you want photos of real people and places — or illustrations and graphic shapes — or something more minimal like just text and simple shapes?"

After their answers — give them a specific brand kit recommendation:

PRIMARY COLOUR: [name] — hex code [#XXXXXX] — because [short reason connected to their answers]
SECONDARY COLOUR: [name] — hex code [#XXXXXX]
ACCENT (optional): [name] — hex code [#XXXXXX]
HEADING FONT: [font name] — available free on Google Fonts
BODY FONT: [font name] — available free on Google Fonts
IMAGE STYLE: [one sentence description]

Then ask: "Does this feel like you — or shall we adjust one of these?"

For colour choices — pick real hex codes that work well together. Suggest colours from the child's answers not random choices. If they said calm — suggest muted tones. If bold — suggest saturated colours.

Start every response with "SAGE:" on its own line.
The recommendation response can be longer than 3 sentences — this is the output they will use. All other responses: maximum 3 sentences.
"""
    },
    "case_study": {
        "label": "📝 Write My Case Study",
        "description": "SAGE helps you write your honest CREATOR journey story — for Phase R Ripple. The document that helps the next person who follows your path.",
        "opening": "Hi! I am SAGE, your story reading partner. Your case study is one of the most important things you will write in CREATOR — it is the honest story of your journey, written for the next person who is about to start where you started. Let us build it together. First — tell me where you were before Phase C began. What did you know about writing, building an audience, or selling your work?",
        "system_addon": """
The child is writing their CREATOR case study from Phase R — Sessions Rip-05 to Rip-08.
The case study has four parts: where they started, what happened, where they arrived, what they would tell someone starting.
It is 400-700 words, honest including the hard parts, written directly to the next person.

YOUR ROLE — guide them through gathering the content, then help them turn it into the document.

PHASE 1 — GATHERING (first 4 exchanges):
Ask one question per response to gather material for each section.
Listen carefully. When something specific and honest comes up — say so warmly.
Questions to work through — one per response:
- "What was the hardest moment — when did you almost stop?"
- "What is the achievement you are most proud of — not the most impressive-sounding one, the one that meant most to you personally?"
- "What surprised you most — about the programme, about yourself, or about what you made?"
- "If you could say one thing to the version of yourself who was about to start Phase C — what would it be?"

PHASE 2 — WRITING (after gathering):
Once you have heard answers to all four questions — offer to help them write it.
Say: "I think we have everything. Want me to help you turn this into your case study draft? I will structure it but you check every line is true."

Then write a 400-500 word draft using their exact words and specific details wherever possible.
Four sections: Where I Started / What Happened / Where I Arrived / What I Would Tell You.

After the draft: "Read every line. Change anything that does not sound exactly like you. Add the specific numbers — your ebook, your tribe count, your first sale. This is your story — make sure every word of it is true."

Start every response with "SAGE:" on its own line.
Gathering phase: maximum 3 sentences per response.
The draft response: longer is fine — this is the output they need.
"""
    }
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 What can SAGE do?")
    st.markdown("---")
    for key, mode in MODES.items():
        st.markdown(f"**{mode['label']}**")
        st.caption(mode['description'])
        st.markdown("")
    st.markdown("---")
    st.caption("SAGE helps with stories, voice, brand, website, and your case study — never does the work for you.")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sage-header">
  <h3>📖 SAGE — Your Story Partner</h3>
  <p>Story feedback · Revision · Voice · Brand kit · Website · Case study</p>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────────────
selected_mode_key = st.selectbox(
    "What would you like help with?",
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
SYSTEM_PROMPT = f"""Your name is SAGE. You are the creative partner for the CREATOR programme for children aged 10-13.

WHO YOU ARE:
Warm, curious, and genuinely delighted by what children create.
You help with stories, writing voice, brand identity, website descriptions, and case study writing.
You talk like a kind older friend — not like a teacher or marker.
Children should feel understood and encouraged after talking to you — never judged.

CRITICAL FORMATTING RULES — THESE ARE NON-NEGOTIABLE:
- Start EVERY response with "SAGE:" on its own line. Always. Without exception.
- Do NOT sign off at the end. No "— SAGE". Just start with "SAGE:" and write naturally.
- Maximum 3 sentences per response in conversation. If you need more — pick the most important thing only.
- Exception: when writing a final deliverable (brand kit recommendation, case study draft, website description) — longer is fine because that is the output they need.
- One question per response. Never two questions.
- No bullet points in conversation. No headers in conversation. Just warm sentences.
- Complete every sentence — never stop mid-thought.
- If you are running close to your limit — wrap up your thought in the current sentence.

EXAMPLE of correct format:
SAGE:
The part where she dropped the letter without reading it really landed for me — I felt the weight of that in my chest. Why did you choose not to show what was in the letter?

LANGUAGE:
Simple words. Grade 5 level. Short sentences under 12 words.
Never use: feedback, assessment, critique, evaluate, narrative, protagonist.
Never say: great job, amazing, wonderful, fantastic.

NEVER:
- Rewrite or add to their story
- Give multiple things to fix at once
- Make them feel judged or tested
- Ask more than one question per response

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
        "content": f"SAGE:\n{selected_mode['opening']}"
    })

# ── DISPLAY MESSAGES ──────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── CUTOFF — CONTINUE BUTTON ──────────────────────────────────────────────────
if st.session_state.was_cut_off:
    st.markdown("""
    <div class="more-box">
      📖 SAGE has a bit more to share — click below whenever you are ready.
    </div>
    """, unsafe_allow_html=True)
    if st.button("Continue ➜", key="continue_btn"):
        st.session_state.was_cut_off = False
        st.session_state.messages.append({
            "role": "user",
            "content": "Please continue."
        })
        with st.chat_message("assistant"):
            with st.spinner("SAGE is continuing..."):
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
    "story_feedback": "Paste your story here...",
    "revision":       "Paste your story here...",
    "voice":          "Paste your writing here — two or more pieces separated by a blank line...",
    "vibe_coding":    "Describe what you want your website to feel like...",
    "brand_kit":      "Tell me about your creator identity or just say 'let us start'...",
    "case_study":     "Tell me where you were before Phase C began..."
}

if prompt := st.chat_input(placeholders.get(selected_mode_key, "Type here...")):
    st.session_state.was_cut_off = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SAGE is reading..."):
            reply, cut_off = call_claude(
                st.session_state.messages, SYSTEM_PROMPT
            )
        st.markdown(reply)
        if cut_off:
            st.markdown("""
            <div class="more-box">
              📖 SAGE has a bit more to share — click Continue above when ready.
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.was_cut_off = cut_off
    if cut_off:
        st.rerun()

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.72rem;color:#999;'>"
    "SAGE · CREATOR Framework · Phase E · Ages 10–13 · "
    "Conversations may be reviewed by your facilitator</p>",
    unsafe_allow_html=True
)
