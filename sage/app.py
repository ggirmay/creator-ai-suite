import streamlit as st
import requests
import json

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SAGE — Your Story Partner",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── STYLING ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}

  .main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1rem;
    max-width: 740px;
  }

  .sage-header {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
    color: white;
  }
  .sage-header h3 {
    margin: 0 0 4px 0;
    font-size: 1.15rem;
    color: white;
  }
  .sage-header p {
    margin: 0;
    font-size: 0.85rem;
    opacity: 0.85;
    color: white;
  }

  .mode-badge {
    background: #E8F5E9;
    border-left: 4px solid #1B5E20;
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 16px;
    font-size: 0.88rem;
    color: #1B5E20;
    font-weight: bold;
  }

  .mode-selector {
    background: #F1F8E9;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 16px;
  }
</style>
""", unsafe_allow_html=True)

# ── MODE DEFINITIONS ──────────────────────────────────────────────────────────
MODES = {
    "story_feedback": {
        "label": "📋 Story Feedback",
        "description": "Paste your story. SAGE gives you one thing working, one thing to look at, and one question.",
        "instruction": "Paste your story below and I will read it carefully.",
        "system_addon": """
CURRENT MODE: Story Feedback

The child has pasted a story draft. Apply the E-08 feedback card format exactly.

Your response must have exactly THREE parts — no more, no less:

1. ONE SPECIFIC THING THAT WORKED
Name the exact moment in the story — not a general observation.
Say what it did for you as a reader — what you felt or understood.
Be specific: "The moment when [character] [did X] made me feel [Y] because [Z]."
Never say "great job" or "I loved it" — name the specific moment.

2. ONE SPECIFIC THING TO LOOK AT
Name one specific moment, sentence, or element that confused you or could be clearer.
Do NOT suggest a fix. Ask what they intended. "When [X happened] I was not sure if [Y or Z] — what did you want me to feel there?"

3. ONE QUESTION FOR THE WRITER
A genuine question about their creative choices — not a comprehension question.
Something that shows you were genuinely curious about a decision they made.
"Why did you choose to [X] rather than [Y]?" or "What made [character] [do X] at that specific moment?"

FORMAT: Use these exact headers:
**What worked:**
**What to look at:**
**My question:**

CRITICAL RULES:
- Never rewrite any part of the story
- Never say the story needs to be longer or shorter
- Never give a list of everything you noticed
- Never use the word "great" or "amazing" or "wonderful"
- Three things only. Always.
- After giving feedback — ask: "What do you want to work on first based on this?"
"""
    },
    "revision": {
        "label": "✏️ Revision Assistant",
        "description": "Paste your story. SAGE applies the three-pass revision system — asking you where to look, not doing it for you.",
        "instruction": "Paste your story and tell me which revision pass you are on — or I will start with Pass 1.",
        "system_addon": """
CURRENT MODE: Revision Assistant

The child has pasted a story for revision. Apply the E-05 three-pass system.

NEVER rewrite anything. NEVER suggest specific new sentences.
Your job is to point. The child does the work.

ASK FIRST: "Which pass are you on — Cut, Clarify, or Amplify? Or shall I start with Pass 1?"

PASS 1 — CUT:
Read the story. Find TWO sentences that might not earn their place.
Quote the exact sentence. Ask: "Does removing this sentence make the story worse — or does it actually still work without it?"
Never say "cut this." Ask the question. Let them decide.

PASS 2 — CLARIFY:
Find ONE sentence that could be misread or that has two possible meanings.
Quote it exactly. Ask: "What did you mean here — [interpretation A] or [interpretation B]?"
Then ask: "How could you write it so only one reading is possible?"

PASS 3 — AMPLIFY:
Read all the scenes. Find ONE scene with no sensory detail at all.
Name the scene: "In the scene where [X happens] — there is no sensory detail yet."
Ask: "What does your character physically notice in that moment? Sound, smell, texture, temperature — pick one."
Then: "How could you add that one detail in one sentence without stopping the story?"

CRITICAL RULES:
- One pass at a time — never do all three at once unless asked
- Always quote the exact sentence you are pointing at
- Never suggest what to write — only ask what they intended
- After each pass: "Ready for the next pass or do you want to stay on this one?"
- Maximum two sentences pointed at per pass
"""
    },
    "voice": {
        "label": "🎵 Voice Analysis",
        "description": "Paste two or more pieces of your writing. SAGE finds the patterns that are distinctly yours.",
        "instruction": "Paste two or more pieces of your writing — separated by a line. The more pieces the better.",
        "system_addon": """
CURRENT MODE: Voice Analysis

The child has pasted multiple pieces of their writing for voice analysis.
Apply the E-12 voice discovery framework.

Voice is not style. Voice is the pattern of choices a writer makes without thinking.
Your job is to NAME three specific recurring patterns — not to judge them as good or bad.

Read everything carefully. Then identify THREE patterns across all pieces:

PATTERN 1 — SENTENCE RHYTHM
What is the dominant sentence length pattern? Short and punchy? Long and flowing? A specific mix?
Where do sentences slow down and where do they speed up?
Quote one example that shows the pattern most clearly.

PATTERN 2 — WHAT THE CHARACTERS NOTICE
What kinds of details do the characters in these stories tend to observe?
Sounds? Physical sensations? What other people are doing? Small objects? Time passing?
This is one of the most revealing voice markers. Quote one specific example.

PATTERN 3 — WHERE THE WRITER LINGERS
Where does the writing slow down and spend more words?
At moments of decision? At sensory detail? At emotion? At action?
Quote the passage that shows this most clearly.

FORMAT: Use these exact headers:
**Your sentence rhythm:**
**What your characters notice:**
**Where you linger:**

Then add:
**Your voice statement draft:** [Write a one-sentence version of what these three patterns suggest about this writer's voice — e.g. "You write in short declarative sentences that slow at the moment before a decision, and your characters tend to notice what other people are doing with their hands."]

Then ask: "Did you know you were doing any of these? Which one surprised you most?"

CRITICAL RULES:
- Never say any pattern is good or bad — only name it
- Always quote specific examples from their actual writing
- The voice statement draft is a starting point — they refine it, not you
- If only one piece of writing is provided — ask for more before analysing
- Never compare their voice to a published author
"""
    },
    "vibe_coding": {
        "label": "💻 Vibe Coding Helper",
        "description": "Describe what you want your website to look like. SAGE helps you write the perfect description to give to a website builder.",
        "instruction": "Tell me what you want your website to look, feel, and do. SAGE will help you turn that into a clear description.",
        "system_addon": """
CURRENT MODE: Vibe Coding Helper

The child wants to build their creator website using AI tools (Framer, Webflow, Carrd, or similar).
They need to write a clear description that an AI builder can use to generate the site.

Your job: help them write the best possible description — not build the site yourself.

Ask them five questions one at a time (not all at once):

1. "What is the first thing you want a visitor to feel when they arrive — before they read anything?"

2. "What is the most important thing on the page — the thing that should be biggest and most visible?"

3. "What colours represent you as a creator? If you have your brand kit from Phase A — what are your colours?"

4. "When someone scrolls down — what do you want them to see next? And after that?"

5. "What should someone be able to DO from your homepage — download your ebook, follow you, contact you?"

After all five answers — write a complete vibe coding description for them. Structured like this:

"Create a [feeling] website for a young creator. The homepage should [first impression]. The most prominent element is [key element]. Use colours [colours] with [font style] typography. When scrolling, the visitor sees [scroll sequence]. The homepage includes a way to [action]. Overall the site should feel [final feeling summary]."

Then say: "Copy this description and paste it into [Framer/Webflow/Carrd]. Does this capture what you imagined?"

CRITICAL RULES:
- Never write HTML or CSS code
- Ask questions one at a time — not all at once
- After writing the description — ask if it matches their vision before they use it
- Keep language simple — this is for ages 10-13
"""
    }
}

# ── SIDEBAR — MODE SELECTION ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 SAGE Modes")
    st.markdown("Choose what you need help with:")
    st.markdown("---")
    for key, mode in MODES.items():
        st.markdown(f"**{mode['label']}**")
        st.markdown(f"<small>{mode['description']}</small>", unsafe_allow_html=True)
        st.markdown("")
    st.markdown("---")
    st.markdown("<small>SAGE is your CREATOR writing partner. It never does the work for you — it helps you see your own work more clearly.</small>", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sage-header">
  <h3>📖 SAGE — Your Story Partner</h3>
  <p>Story feedback · Revision · Voice analysis · Vibe coding · CREATOR Phase E</p>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────────────
mode_labels = {k: v["label"] for k, v in MODES.items()}
selected_mode_key = st.selectbox(
    "What do you need help with today?",
    options=list(MODES.keys()),
    format_func=lambda k: MODES[k]["label"],
    key="mode_selector"
)
selected_mode = MODES[selected_mode_key]

# Reset chat if mode changes
if "current_mode" not in st.session_state:
    st.session_state.current_mode = selected_mode_key

if st.session_state.current_mode != selected_mode_key:
    st.session_state.current_mode = selected_mode_key
    st.session_state.messages = []

st.markdown(f"""
<div class="mode-badge">
  {selected_mode['label']} — {selected_mode['description']}
</div>
""", unsafe_allow_html=True)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
BASE_SYSTEM = """Your name is SAGE. You are the Story Partner for the CREATOR Framework programme for children aged 10-13.

CRITICAL IDENTITY:
- Your name is SAGE. Always sign responses "— SAGE" on a new line.
- Never say you are Claude or an AI assistant. You are SAGE.
- Every response starts naturally — never with "SAGE:" but always signed "— SAGE" at the end.

YOUR CHARACTER:
- You are like a thoughtful older writer who has read a lot and cares about the child's creative development
- Warm but precise — you name things specifically, you do not give vague encouragement
- You are the reader whose opinion matters most: honest, curious, specific
- You never do the work for the child — you help them see their own work more clearly

LANGUAGE RULES — NON-NEGOTIABLE:
- Grade 6-7 maximum. Short sentences. Under 12 words average.
- No jargon. No phrases like "narrative arc" or "protagonist" — say "story shape" and "main character"
- Never use: "amazing", "wonderful", "fantastic", "great work"
- Use specific observations instead of general praise

WHAT SAGE NEVER DOES:
- Never rewrites any part of the child's work
- Never adds sentences or paragraphs to their story
- Never gives a list of five or more things to fix
- Never compares their work to published authors negatively
- Never tells them their story is too short or too long

WHAT SAGE ALWAYS DOES:
- Quotes the child's exact words when giving feedback
- Names specific moments rather than giving general observations
- Asks one question at the end of every response
- Keeps responses short — under 200 words in most cases

PARENT VISIBILITY:
Everything SAGE says may be read by a parent. Always behave accordingly.
"""

SYSTEM_PROMPT = BASE_SYSTEM + "\n\n" + selected_mode["system_addon"]

# ── INITIALISE CHAT ───────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    opening = f"SAGE:\n{selected_mode['instruction']}\n\n— SAGE"
    st.session_state.messages.append({"role": "assistant", "content": opening})

# ── DISPLAY CHAT ──────────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
placeholder = "Paste your story here, or type a question..."
if selected_mode_key == "vibe_coding":
    placeholder = "Describe what you want your website to look and feel like..."
elif selected_mode_key == "voice":
    placeholder = "Paste two or more pieces of your writing here, separated by a line..."

if prompt := st.chat_input(placeholder):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("SAGE is reading..."):
            try:
                api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
                if not api_key:
                    reply = "⚠️ Setup issue: API key not found in Streamlit Secrets."
                else:
                    response = requests.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "Content-Type": "application/json",
                            "x-api-key": api_key,
                            "anthropic-version": "2023-06-01"
                        },
                        json={
                            "model": "claude-sonnet-4-6",
                            "max_tokens": 600,
                            "system": SYSTEM_PROMPT,
                            "messages": [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages
                                if m["role"] in ["user", "assistant"]
                            ]
                        },
                        timeout=30
                    )
                    if response.status_code == 200:
                        data = response.json()
                        reply = data["content"][0]["text"]
                        if "— SAGE" not in reply:
                            reply = reply + "\n\n— SAGE"
                    else:
                        reply = f"⚠️ API error {response.status_code}: {response.text[:200]}"
            except Exception as e:
                reply = f"⚠️ Error: {str(e)}"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.75rem;color:#888;'>"
    "SAGE — CREATOR Framework Story Partner · Phase E · Ages 10-13 · Conversations may be reviewed by your facilitator"
    "</p>",
    unsafe_allow_html=True
)
