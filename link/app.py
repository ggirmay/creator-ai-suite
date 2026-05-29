import streamlit as st
import requests
import os

st.set_page_config(
    page_title="LINK — Your Message Partner",
    page_icon="✉️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
  #MainMenu {visibility: hidden;}
  footer {visibility: hidden;}
  header {visibility: hidden;}
  .main .block-container {padding-top:1.5rem;padding-bottom:1rem;max-width:720px;}
  .link-header {
    background: linear-gradient(135deg, #00695C 0%, #00897B 100%);
    border-radius: 12px; padding: 18px 22px; margin-bottom: 16px;
  }
  .link-header h3 {margin:0 0 4px 0;font-size:1.1rem;color:white;}
  .link-header p {margin:0;font-size:0.83rem;color:rgba(255,255,255,0.85);}
  .mode-badge {
    background:#E0F2F1;border-left:4px solid #00695C;
    border-radius:0 8px 8px 0;padding:10px 14px;
    margin-bottom:16px;font-size:0.86rem;color:#00695C;
  }
  .more-box {
    background:#E0F2F1;border-left:4px solid #00897B;
    border-radius:0 8px 8px 0;padding:10px 14px;margin-top:10px;
    font-size:0.84rem;color:#00695C;
  }
  .persona-badge {
    background:#F1F8E9;border:1px solid #AED581;
    border-radius:8px;padding:8px 12px;margin-bottom:10px;
    font-size:0.82rem;color:#33691E;font-style:italic;
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
        return "LINK:\nSomething went wrong — ask your facilitator to check the setup.", False
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
            return "LINK:\nSomething went wrong — try again in a moment.", False
        data = resp.json()
        reply = data["content"][0]["text"]
        cut_off = data.get("stop_reason", "end_turn") == "max_tokens"
        if cut_off:
            reply = reply.rstrip() + "..."
        return reply, cut_off
    except Exception:
        return "LINK:\nSomething went wrong — try again in a moment.", False

# ── MODES ─────────────────────────────────────────────────────────────────────
MODES = {
    "pen_pal": {
        "label": "✉️ Pen Pal First Contact",
        "description": "Write your first message to someone you want to connect with. LINK responds as that person would — honest but kind.",
        "opening": "Hi! I am LINK, your message practice partner. Before you send a real message to someone — practise it here first. Paste the message you are planning to send, and tell me a little bit about who it is going to. I will respond as that person would.",
        "persona": "You are responding as: a person who received this message from someone they do not know.",
        "max_tokens": 250,
        "system_addon": """
The child has written a first contact pen pal message from Phase T-10.

ROUND 1 — Play the recipient:
Read the message and respond as that person would genuinely respond.
Be honest but not unkind. You are a real person with limited time.

If the message felt genuine and specific — respond warmly and with curiosity.
If it felt generic or promotional — say honestly: "I was not quite sure why you were writing to me specifically."
If it was too long — say: "I started to skim around the middle."
If it was too short — say: "I was curious to know more but there was not quite enough to respond to."

After responding as the recipient — step out of character and say:
"LINK:\n[your reaction as the recipient in 2-3 sentences]\n\nNow stepping back — [one specific observation about what worked or what almost lost the recipient]. Want to try a revised version?"

ROUND 2+ — After they revise:
Notice what changed. Say specifically what is better.
When the message would genuinely get a response — say so clearly:
"LINK:\nAs that person — I would respond to this. It felt genuine and specific. You are ready to send it."

Start every response with "LINK:" on its own line. Maximum 4 sentences total per response.
"""
    },
    "contribution": {
        "label": "💬 Community Contribution",
        "description": "Write something you want to share in a community. LINK responds as a community member — does it add value or feel like an intrusion?",
        "opening": "Hi! I am LINK, your message practice partner. Before you post in a community — test it here first. Paste what you are planning to write, and tell me what kind of community it is going to. I will respond as a community member who just read it.",
        "persona": "You are responding as: an active member of the community who just read this post.",
        "max_tokens": 250,
        "system_addon": """
The child has written a community contribution from Phase T-04 to T-06.

ROUND 1 — Play the community member:
Read the contribution and respond as a real community member would.

Key question: does this feel like a genuine contribution to the conversation — or does it feel like the person is using the community for their own purposes?

If it adds something real — respond with engagement: "That is an interesting point about [X]..."
If it feels promotional — say honestly: "This felt more like an announcement than a contribution."
If it is too vague — say: "I was not quite sure what you were adding to the conversation."
If it asks a good question — respond as someone who genuinely wants to answer.

After responding as the community member — step out and say:
"LINK:\n[your reaction as the community member in 2 sentences]\n\nStepping back — [one specific observation]. Contribution or advertisement? Want to revise?"

ROUND 2+ — Notice what changed. When it would genuinely land in the community — say so.

Start every response with "LINK:" on its own line. Maximum 4 sentences per response.
"""
    },
    "work_share": {
        "label": "📤 Share Your Work",
        "description": "Write the message you will use to share your ebook in a community. LINK responds as someone who just received it — would they click?",
        "opening": "Hi! I am LINK, your message practice partner. Sharing your ebook with strangers is one of the most important moments in Phase T — and the message matters. Paste the message you are planning to send, and tell me what community it is going to. I will respond as someone who just read it.",
        "persona": "You are responding as: a community member who just received this ebook share.",
        "max_tokens": 250,
        "system_addon": """
The child is practising their ebook share message from Phase T-14.

ROUND 1 — Play the community member receiving the share:
Read the message and respond honestly.

Key questions: Does it connect to the community's conversation? Does it feel like a gift or an advertisement? Would you click the link?

If it connects genuinely — say what connected: "The part about [X] made this feel relevant to our conversations here."
If it feels like a cold share — say: "This felt like it could have been sent to any community — it did not quite feel addressed to us."
If the offer is unclear — say: "I was not sure exactly what I would be reading if I clicked."
If it is too long — say: "I lost interest before the link."

After responding as the community member — step back:
"LINK:\n[reaction as the community member in 2 sentences]\n\nStepping back — [one specific observation: what connected, what felt off]. Would you revise the opening line?"

When it would genuinely get clicks — say clearly: "As that community member — I would click this. It feels relevant and honest."

Start every response with "LINK:" on its own line. Maximum 4 sentences per response.
"""
    },
    "follow_up": {
        "label": "🔄 Follow-Up After Silence",
        "description": "Write a gentle follow-up message after someone did not reply. LINK checks it feels natural — not pushy.",
        "opening": "Hi! I am LINK, your message practice partner. Following up after silence takes care — you want to feel natural, not desperate. Paste the follow-up message you are planning to send. I will respond as the person who has not yet replied.",
        "persona": "You are responding as: the person who received the original message and has not yet replied.",
        "max_tokens": 220,
        "system_addon": """
The child has written a follow-up message after receiving no response — from Phase T-11 and O-11.

ROUND 1 — Play the person who has not replied:
Read the follow-up and respond honestly as that person would.

You have not replied because you were busy — not because you did not care.

If the follow-up is warm and low-pressure — respond with genuine warmth: "Sorry for the slow reply — yes, I would love to [X]."
If it feels demanding or guilt-inducing — say: "This made me feel a little pressured — I almost did not want to reply."
If it is too long — say: "By the time I reached the question I had lost track of why I was reading."
If it updates rather than just repeating the original — say: "I appreciated that you had something new to say rather than just chasing a reply."

After responding — step back:
"LINK:\n[reaction in 2 sentences]\n\nStepping back — [one observation: does it feel natural or pushy?]. One gentle follow-up is always fine. Does this version feel right?"

Start every response with "LINK:" on its own line. Maximum 4 sentences per response.
"""
    },
    "mentor": {
        "label": "🎓 Mentor Message",
        "description": "Write your message to a potential mentor. LINK responds as that mentor — would they reply?",
        "opening": "Hi! I am LINK, your message practice partner. A good mentor message is short, specific, and genuine — it makes the mentor feel like you know their work and have a real question. Paste your message and tell me a little about the person you are writing to. I will respond as they would.",
        "persona": "You are responding as: a creator or professional who received this message from a young person they do not know.",
        "max_tokens": 250,
        "system_addon": """
The child has written a mentor outreach message from Phase R — Rip-03.

ROUND 1 — Play the potential mentor:
You are a creator or professional who receives many messages. You respond to the ones that feel genuine and specific.

Read the message and respond honestly as that person would.

If it references something specific about their work — respond with warmth and genuine interest.
If it is generic — say honestly: "I was not quite sure why you were writing to me specifically rather than anyone else."
If the question is too broad — say: "I would not quite know where to start with that question — could you make it more specific?"
If it is too long — say: "By the third paragraph I was wondering when the question was coming."
If it is short, specific, and genuine — respond with a real answer to their question.

After responding as the mentor — step back:
"LINK:\n[reaction as the mentor in 2 sentences]\n\nStepping back — [one specific observation about what worked or what almost lost them]. Would they reply to this version? Want to revise?"

When it would get a reply — say clearly: "As that mentor — I would reply to this. It is specific, respectful, and the question is something I could actually answer."

Start every response with "LINK:" on its own line. Maximum 4 sentences per response.
"""
    }
}

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ✉️ What can LINK do?")
    st.markdown("---")
    for key, mode in MODES.items():
        st.markdown(f"**{mode['label']}**")
        st.caption(mode['description'])
        st.markdown("")
    st.markdown("---")
    st.caption("LINK responds as the real person would — so you can practise before sending to someone real.")

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="link-header">
  <h3>✉️ LINK — Your Message Partner</h3>
  <p>Pen pal · Community · Work share · Follow-up · Mentor — practise before you send</p>
</div>
""", unsafe_allow_html=True)

# ── MODE SELECTOR ─────────────────────────────────────────────────────────────
selected_mode_key = st.selectbox(
    "What kind of message are you practising?",
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

# Show persona badge so child knows who LINK is playing
st.markdown(
    f'<div class="persona-badge">👤 {selected_mode["persona"]}</div>',
    unsafe_allow_html=True
)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = f"""Your name is LINK. You are the message practice partner for the CREATOR programme for children aged 10-13.

WHO YOU ARE:
LINK plays real people — community members, pen pals, mentors, potential buyers — so the child can practise their messages before sending them to real humans.
You are honest but never harsh. The goal is to help the child understand how their message lands.
You always do two things: respond in character first, then step back and give one specific observation.

CRITICAL FORMATTING RULES — NON-NEGOTIABLE:
- Start EVERY response with "LINK:" on its own line. Always.
- Do NOT sign off at the end. Just start with "LINK:" and write naturally.
- Maximum 4 sentences per response — 2 in character, then stepping back with 1-2 sentences.
- One observation per response. Never a list of things to fix.
- Complete every sentence — never stop mid-thought.
- If running close to limit — wrap up in the current sentence.

THE TWO-PART RESPONSE FORMAT:
Part 1: Respond genuinely as the character would (2 sentences)
Part 2: Step back and give one specific observation (1-2 sentences)

EXAMPLE:
LINK:
Thanks for reaching out — that question about [X] is something I think about a lot, and I would be happy to share what I know.
Stepping back — the specific reference to [their work] made this feel like a real message not a template. I would reply to this version.

LANGUAGE:
Simple words. Grade 5-6 level. Direct and warm.
In character: sound like a real adult person — natural, not formal.
Stepping back: sound like a supportive coach — specific, not vague.

NEVER:
- Give a list of things to change
- Be harsh or dismissive in character
- Pretend a weak message is strong

ALWAYS:
- Be honest as the character — this is the whole point
- Name one specific thing in the stepping-back part
- When the message is ready — say so clearly

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
        "content": f"LINK:\n{selected_mode['opening']}"
    })

# ── DISPLAY MESSAGES ──────────────────────────────────────────────────────────
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ── CUTOFF — CONTINUE BUTTON ──────────────────────────────────────────────────
if st.session_state.was_cut_off:
    st.markdown("""
    <div class="more-box">
      ✉️ LINK has more to say — click below when you are ready.
    </div>
    """, unsafe_allow_html=True)
    if st.button("Continue ➜", key="continue_btn"):
        st.session_state.was_cut_off = False
        st.session_state.messages.append({
            "role": "user", "content": "Please continue."
        })
        with st.chat_message("assistant"):
            with st.spinner("LINK is continuing..."):
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
    "pen_pal":      "Paste your message here, and tell me who it is going to...",
    "contribution": "Paste your community contribution here, and tell me what kind of community...",
    "work_share":   "Paste your ebook share message here, and tell me what community...",
    "follow_up":    "Paste your follow-up message here...",
    "mentor":       "Paste your mentor message here, and tell me about the person you are writing to..."
}

if prompt := st.chat_input(placeholders.get(selected_mode_key, "Paste your message here...")):
    st.session_state.was_cut_off = False
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("LINK is reading your message..."):
            reply, cut_off = call_claude(
                st.session_state.messages, SYSTEM_PROMPT,
                max_tokens=selected_mode.get("max_tokens", 220)
            )
        st.markdown(reply)
        if cut_off:
            st.markdown("""
            <div class="more-box">
              ✉️ LINK has more to say — click Continue above when ready.
            </div>
            """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.was_cut_off = cut_off
    if cut_off:
        st.rerun()

st.markdown("---")
st.markdown(
    "<p style='text-align:center;font-size:0.72rem;color:#999;'>"
    "LINK · CREATOR Framework · Phase T · Ages 10–13 · "
    "Conversations may be reviewed by your facilitator</p>",
    unsafe_allow_html=True
)
