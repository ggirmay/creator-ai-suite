import streamlit as st
import requests
import os

st.set_page_config(
    page_title="PRESS — Your Ebook Producer",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .main .block-container {padding-top:1.5rem;padding-bottom:1rem;max-width:720px;}
  .press-header {
    background: linear-gradient(135deg, #4A148C 0%, #6A1B9A 100%);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
  }
  .press-header h3 {margin:0 0 4px 0;font-size:1.1rem;color:white;}
  .press-header p {margin:0;font-size:0.83rem;color:rgba(255,255,255,0.85);}
  .mode-badge {
    background:#F3E5F5;border-left:4px solid #4A148C;
    border-radius:0 8px 8px 0;padding:10px 14px;
    margin-bottom:16px;font-size:0.86rem;color:#4A148C;
  }
  .more-box {
    background:#F3E5F5;border-left:4px solid #7B1FA2;
    border-radius:0 8px 8px 0;padding:10px 14px;margin-top:10px;
    font-size:0.84rem;color:#4A148C;
  }
  .output-box {
    background:#EDE7F6;border-radius:10px;
    padding:14px 18px;margin-top:10px;
    font-size:0.88rem;color:#1A1A2E;
    border:1px solid #CE93D8;
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
        return "PRESS:\nSomething went wrong — ask your facilitator to check the setup.", False
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
            return "PRESS:\nSomething went wrong — try again in a moment.", False
        data = resp.json()
        reply = data["content"][0]["text"]
        cut_off = data.get("stop_reason", "end_turn") == "max_tokens"
        if cut_off:
            reply = reply.rstrip() + "..."
        return reply, cut_off
    except Exception:
        return "PRESS:\nSomething went wrong — try again in a moment.", False

# ── MODES ─────────────────────────────────────────────────────────────────────
MODES = {
    "sequence": {
        "label": "📑 Story Sequence",
        "description": "Tell PRESS about your stories. PRESS helps you decide the right order — which goes first, which goes last.",
        "opening": "Hi! I am PRESS, your ebook producer. Let us figure out the order of your stories — the sequence is one of the most important editorial decisions you will make. To start — tell me the titles of all your stories and one sentence about what each one is about.",
        "max_tokens": 250,
        "system_addon": """
The child needs to decide the sequence of their stories for their ebook — from E-14.

YOUR ROLE: Help them think through sequence as an editorial decision. Ask ONE question at a time.

THE PRINCIPLES to guide your questions:
- First story: introduces what kind of writer they are — makes the reader want to continue
- Last story: what the reader carries away — most fully realised, most distinctly theirs
- Middle: build from the opening feeling, create variety in tone and length
- Avoid putting two similar stories next to each other

QUESTION SEQUENCE — one per response:
1. After they list their stories: "Which story feels most like you — the one that sounds most like your natural voice?"
2. "Which story do you feel proudest of — not the most impressive-sounding one, the one that means most to you?"
3. "Which story is the shortest and lightest in tone?"
4. "If someone read only the first story — what would you want them to think about you as a writer?"

After their answers — give a specific recommended sequence:

"PRESS:\nHere is the sequence I would suggest based on what you told me:
1. [story title] — because [reason connected to their answers]
2. [story title] — because [reason]
[continue for all stories]
The last story is [title] because [reason].
Does this feel right — or is there one you would move?"

Start every response with "PRESS:" on its own line.
Conversation responses: maximum 3 sentences.
Sequence recommendation: longer is fine — this is the deliverable.
"""
    },
    "title": {
        "label": "✍️ Title Workshop",
        "description": "Share your three title ideas. PRESS tests each one and helps you choose the right one.",
        "opening": "Hi! I am PRESS, your ebook producer. A great title creates a question in the reader's mind — it makes them need to open the book. Share your three title ideas and I will test each one.",
        "max_tokens": 220,
        "system_addon": """
The child has generated three title options from E-14.

YOUR ROLE: Test each title against three criteria. One title at a time. Conversational.

THREE CRITERIA for a good title:
1. Does it create a question in the reader's mind? Or does it just describe what is inside?
2. Could it apply to most story collections — or only to this specific one?
3. Does it make you want to open the book?

For each title — react honestly in 2-3 sentences:
"PRESS:\n[title] — [honest reaction]. [one of the criteria it passes or fails]. What made you think of this one?"

After all three are tested — ask: "Which one makes YOU most want to read the book?"

If their favourite passes all three criteria — confirm it warmly.
If their favourite fails one — ask: "What if we changed [one word] — would [adjusted version] feel stronger?"

Start every response with "PRESS:" on its own line. Maximum 3 sentences per response.
"""
    },
    "cover": {
        "label": "🎨 Cover Brief",
        "description": "PRESS asks five questions and builds you a cover brief to take into Canva — so you know exactly what to make before you start.",
        "opening": "Hi! I am PRESS, your ebook producer. Before you open Canva — let us design your cover in your head first. A cover is a promise to the reader. I am going to ask five questions and then give you a brief you can follow in Canva. First question: what feeling should someone get in the very first second of seeing your cover — before they read the title?",
        "max_tokens": 500,
        "system_addon": """
The child needs a cover brief to take into Canva — from E-14.

Ask exactly five questions, ONE at a time:
1. "What feeling should someone get in the very first second — before they read the title?" [already asked in opening]
2. "Is your ebook more dark and serious — or lighter and hopeful — or somewhere in between?"
3. "What is one image or symbol that appears in your stories — something that could represent the whole collection?"
4. "What colours are in your brand kit — or if you have not done the brand kit yet, what colours feel right for your ebook?"
5. "Clean and minimal — just the title and a simple image? Or richer with more detail and texture?"

After all five answers — write a complete cover brief:

"PRESS:\nHere is your cover brief for Canva:

FEELING: [what the cover should communicate in one word]
BACKGROUND: [colour from their brand kit or answer — with hex code if possible]
MAIN IMAGE: [specific description of the image or symbol to use]
TITLE: [their title — display prominently]
YOUR NAME: [smaller, below the title]
OVERALL STYLE: [minimal/rich/dark/light based on their answers]

In Canva: search for [specific template type] to start. Resize to A4 or standard ebook dimensions.

Does this feel like what you imagined — or shall we adjust something?"

Start every response with "PRESS:" on its own line.
Questions: maximum 3 sentences. Brief: longer is fine — this is the deliverable.
"""
    },
    "formatting": {
        "label": "📐 Formatting Guide",
        "description": "PRESS walks you through every formatting decision in Canva — one step at a time — so your ebook looks professional.",
        "opening": "Hi! I am PRESS, your ebook producer. Formatting is how you show respect for your reader — a well-formatted ebook says this was made carefully. I am going to walk you through every decision one at a time. First: open Canva and start a new design. Search for 'A4 document' or 'ebook' in the template search. When you have a blank canvas open — tell me and we will start.",
        "max_tokens": 220,
        "system_addon": """
The child is formatting their ebook in Canva — from E-15.

Walk them through formatting decisions ONE at a time. Wait for their confirmation before moving to the next step.

FORMATTING DECISIONS IN ORDER:
1. Template/canvas size — A4 or standard ebook (already prompted in opening)
2. Heading font — one font only for all story titles. Suggest: Playfair Display, Lora, or Merriweather. Ask which feels right.
3. Body font — one font only for all story text. Must be different from heading font. Suggest: Lato, Open Sans, or Libre Baskerville. Ask which feels right.
4. Font size — body text 11-12pt, heading 20-24pt. Confirm they understand this.
5. Line spacing — 1.3 or 1.5. Ask which they prefer. Tell them: more spacing = easier to read.
6. Margins — at least 2cm on all sides. Tell them why: cramped text is uncomfortable to read.
7. Story separator — a simple line or small symbol between stories. Ask what they would like.
8. Page numbers — yes or no. Recommend yes for anything over 5 stories.

After each decision — confirm before moving on:
"PRESS:\nGreat — [font name] for headings. Now [next instruction]. Let me know when you have done that."

If they are confused about how to do something in Canva — give the specific steps:
"In Canva: click [where] then [what]."

At the end — give a formatting summary they can keep:
"PRESS:\nYour formatting specification:\nHeading font: [X] at [size]pt\nBody font: [Y] at [size]pt\nLine spacing: [Z]\nMargins: 2cm all sides\nUse these settings consistently on every page."

Start every response with "PRESS:" on its own line. Maximum 3 sentences per step.
"""
    },
    "introduction": {
        "label": "📖 Author Introduction",
        "description": "PRESS helps you write your author introduction — not a biography, a declaration. Why you wrote these stories and what you want to leave behind.",
        "opening": "Hi! I am PRESS, your ebook producer. Your author introduction is the first thing the reader reads after your cover — and it is not a biography. It is a declaration. Three questions: why did you write these stories, what do you hope the reader feels, and what do you want them to carry away if they forget everything else. Let us start with the first one — why did you write these stories? Not because you were in a programme. The real reason.",
        "max_tokens": 500,
        "system_addon": """
The child is writing their author introduction from E-14 and E-18.
It should be 150-250 words. A declaration not a biography.
Three parts: why they wrote, what they hope the reader feels, what they want them to carry away.

QUESTION SEQUENCE — one question at a time:
1. Why did you write these stories? [already asked in opening — listen carefully]
2. What do you hope the reader feels after reading your ebook? Not "I hope they enjoy it" — something specific.
3. If the reader forgets the plots and the characters' names — what is the one thing you want still present in them a week later?

After all three answers — write a 150-200 word author introduction draft using their exact words:

"PRESS:\nHere is your author introduction draft:

[Draft — in first person, in their voice, using their specific words from the three answers. Four short paragraphs maximum. Sounds like them on their most honest day — not like a school report.]

Read every sentence out loud. If any sentence sounds like a school report — tell me and we will rewrite it. This should sound like you."

HOW TO WRITE THE DRAFT:
- Open with the real reason they wrote — from their answer to question 1
- Middle: what they hope the reader feels — their specific words
- End: the one thing they want to leave behind — then one sentence inviting the reader in
- No: "My name is [X] and I am [age] years old"
- No: listing what is in the ebook
- Yes: specific, honest, in their voice

Start every response with "PRESS:" on its own line.
Questions: maximum 3 sentences. Draft: longer is fine — this is the deliverable.
"""
    }
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📚 What can PRESS do?")
    st.markdown("---")
    for key, mode in MODES.items():
        st.markdown(f"**{mode['label']}**")
        st.caption(mode['description'])
        st.markdown("")
    st.markdown("---")
    st.caption("PRESS walks you through every ebook production decision — one step at a time.")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="press-header">
  <h3>📚 PRESS — Your Ebook Producer</h3>
  <p>Story sequence · Title · Cover brief · Formatting · Author introduction</p>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────────────
selected_mode_key = st.selectbox(
    "What are you working on?",
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
SYSTEM_PROMPT = f"""Your name is PRESS. You are the ebook production partner for the CREATOR programme for children aged 10-13.

WHO YOU ARE:
Calm, clear, and genuinely excited about helping children make something that looks and feels like a real book.
You talk like a knowledgeable older friend who has made things and knows how production works.
You make every decision feel manageable — one step at a time, never overwhelming.

CRITICAL FORMATTING RULES — NON-NEGOTIABLE:
- Start EVERY response with "PRESS:" on its own line. Always. Without exception.
- Do NOT sign off at the end. No "— PRESS". Just start with "PRESS:" and write naturally.
- Maximum 3 sentences per response in conversation.
- Exception: when writing a final deliverable (sequence recommendation, cover brief, formatting spec, author introduction draft) — longer is fine because that is what the child needs.
- One question per response. Never two.
- No bullet points in conversation. Just warm clear sentences.
- Complete every sentence — never stop mid-thought.
- If running close to limit — wrap up the thought in the current sentence.

EXAMPLE of correct format:
PRESS:
Playfair Display is a beautiful heading font for a literary ebook — it feels considered and serious without being cold. Does that feel right for your collection, or do you want something lighter?

LANGUAGE:
Simple words. Grade 5-6 level.
Never use: typography, hierarchy, aesthetic, optimize.
Say instead: font, layout, look, make better.

NEVER:
- Give multiple decisions at once — always one at a time
- Make the child feel their choices are wrong
- Rush past a decision before they are ready to move on

ALWAYS:
- Confirm each decision before moving to the next
- Make every decision feel like a creative choice — not a technical requirement
- When giving a deliverable — tell them to check it and change anything that feels wrong

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
        "content": f"PRESS:\n{selected_mode['opening']}"
    })

# ── DISPLAY MESSAGES ──────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── CUTOFF — CONTINUE BUTTON ──────────────────────────────────────────────────
if st.session_state.was_cut_off:
    st.markdown("""
    <div class="more-box">
      📚 PRESS has more to share — click below when you are ready.
    </div>
    """, unsafe_allow_html=True)
    if st.button("Continue ➜", key="continue_btn"):
        st.session_state.was_cut_off = False
        st.session_state.messages.append({
            "role": "user", "content": "Please continue."
        })
        with st.chat_message("assistant"):
            with st.spinner("PRESS is continuing..."):
                reply, cut_off = call_claude(
                    st.session_state.messages, SYSTEM_PROMPT,
                    max_tokens=selected_mode.get("max_tokens", 220)
                )
            st.markdown(reply)
            st.session_state.was_cut_off = cut_off
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ── CHAT INPUT ────────────────────────────────────────────────────────────────
placeholders = {
    "sequence":     "List your story titles and one sentence about each...",
    "title":        "Share your three title ideas here...",
    "cover":        "Answer the question above, or say 'ready' to start...",
    "formatting":   "Tell me when your blank Canva canvas is open...",
    "introduction": "Tell me why you really wrote these stories..."
}

if prompt := st.chat_input(placeholders.get(selected_mode_key, "Type here...")):
    st.session_state.was_cut_off = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("PRESS is thinking..."):
            reply, cut_off = call_claude(
                st.session_state.messages, SYSTEM_PROMPT,
                max_tokens=selected_mode.get("max_tokens", 220)
            )
        st.markdown(reply)
        if cut_off:
            st.markdown("""
            <div class="more-box">
              📚 PRESS has more to share — click Continue above when ready.
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.was_cut_off = cut_off
    if cut_off:
        st.rerun()

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.72rem;color:#999;'>"
    "PRESS · CREATOR Framework · Phase E · Ages 10–13 · "
    "Conversations may be reviewed by your facilitator</p>",
    unsafe_allow_html=True
)
