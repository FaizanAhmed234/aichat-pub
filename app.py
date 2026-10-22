from __future__ import annotations

import html
import json
import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st


# -----------------------------------------------------------------------------
# Page configuration and visual design
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Chatbot Pro",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "AI Chatbot Pro"
APP_VERSION = "0.1.0"

st.markdown(
    r"""
    <style>
    :root {
        --acp-bg: #0b0d12;
        --acp-panel: #11151d;
        --acp-panel-2: #171c27;
        --acp-border: rgba(160, 174, 198, .16);
        --acp-text: #edf1f8;
        --acp-muted: #9ba6b8;
        --acp-accent: #a78bfa;
        --acp-accent-2: #6ee7d8;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 80% -10%, rgba(124, 92, 255, .13), transparent 38%),
          radial-gradient(ellipse at 0% 15%, rgba(66, 211, 194, .07), transparent 30%),
          var(--acp-bg);
        color: var(--acp-text);
    }
    [data-testid="stHeader"] { background: rgba(11, 13, 18, .72); }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10141c 0%, #0d1017 100%);
        border-right: 1px solid var(--acp-border);
    }
    [data-testid="stSidebarContent"] { padding-top: 1.1rem; }
    .block-container { padding-top: 1.5rem; padding-bottom: 7rem; max-width: 1120px; }
    .acp-brand { display:flex; align-items:center; gap:.7rem; margin:.15rem 0 1.3rem; }
    .acp-logo {
        width: 42px; height: 42px; border-radius: 14px; display:flex;
        align-items:center; justify-content:center; color:#0c1016; font-size:1.35rem;
        font-weight:900; background:linear-gradient(135deg, #a78bfa, #6ee7d8);
        box-shadow: 0 7px 24px rgba(167,139,250,.18);
    }
    .acp-brand-name { color:var(--acp-text); font-weight:750; letter-spacing:-.035em; font-size:1.12rem; line-height:1.2; }
    .acp-brand-sub { color:var(--acp-muted); font-size:.75rem; margin-top:.2rem; }
    .acp-topline { display:flex; align-items:center; gap:.55rem; flex-wrap:wrap; margin-bottom:.55rem; }
    .acp-eyebrow { color:var(--acp-accent-2); text-transform:uppercase; font-size:.72rem; letter-spacing:.13em; font-weight:750; }
    .acp-pill { border:1px solid rgba(167,139,250,.32); color:#d8ccff; background:rgba(167,139,250,.10); border-radius:999px; padding:.22rem .55rem; font-size:.72rem; font-weight:650; }
    .acp-title { font-size:clamp(2rem, 5vw, 3.15rem); font-weight:800; letter-spacing:-.06em; line-height:1.08; margin:.25rem 0 .65rem; color:#f4f5fb; }
    .acp-subtitle { color:var(--acp-muted); font-size:1rem; line-height:1.65; max-width:700px; margin-bottom:1.2rem; }
    .acp-divider { height:1px; background:var(--acp-border); margin:1.1rem 0 1.2rem; }
    .acp-section-label { color:#aab4c6; text-transform:uppercase; font-size:.72rem; font-weight:750; letter-spacing:.11em; margin:.3rem 0 .65rem; }
    .acp-empty {
        border:1px solid var(--acp-border); border-radius:22px; padding:1.5rem;
        background:linear-gradient(145deg, rgba(24,29,41,.88), rgba(15,19,27,.8));
        margin:1.2rem 0 1.1rem;
    }
    .acp-empty-icon { font-size:1.65rem; margin-bottom:.5rem; }
    .acp-empty-title { color:#f2f4fb; font-size:1.2rem; font-weight:750; letter-spacing:-.025em; }
    .acp-empty-copy { color:var(--acp-muted); line-height:1.6; margin-top:.35rem; }
    .acp-feature { border:1px solid var(--acp-border); background:rgba(20,24,34,.68); padding:.9rem; border-radius:15px; min-height:112px; }
    .acp-feature-icon { font-size:1.2rem; margin-bottom:.45rem; }
    .acp-feature-title { color:#e8edf7; font-weight:700; font-size:.9rem; }
    .acp-feature-copy { color:var(--acp-muted); font-size:.79rem; line-height:1.45; margin-top:.25rem; }
    .acp-note { color:var(--acp-muted); font-size:.78rem; line-height:1.5; }
    .acp-chat-title { font-size:1.05rem; font-weight:750; color:#edf1f8; letter-spacing:-.02em; }
    .acp-chat-meta { color:var(--acp-muted); font-size:.76rem; margin-top:.2rem; }
    div[data-testid="stChatMessage"] { border:1px solid rgba(160,174,198,.10); border-radius:17px; padding:.85rem 1rem; background:rgba(18,22,31,.58); margin-bottom:.8rem; }
    div[data-testid="stChatInput"] { border-color:rgba(167,139,250,.36) !important; background:#141923 !important; border-radius:18px !important; }
    div[data-testid="stChatInput"] textarea { color:#f1f3fa !important; }
    .stButton > button, .stDownloadButton > button {
        border-radius:12px; border:1px solid var(--acp-border); transition:all .15s ease;
    }
    .stButton > button:hover, .stDownloadButton > button:hover { border-color:rgba(167,139,250,.7); color:#fff; }
    button[kind="primary"] { background:linear-gradient(120deg, #a78bfa, #77ddd1) !important; color:#10131b !important; border:0 !important; font-weight:750 !important; }
    [data-testid="stMetric"] { background:rgba(20,24,34,.68); border:1px solid var(--acp-border); padding:.75rem; border-radius:14px; }
    [data-testid="stMetricLabel"] { color:var(--acp-muted) !important; }
    @media (max-width: 640px) {
        .block-container { padding-top:1rem; padding-left:1rem; padding-right:1rem; }
        .acp-title { font-size:2.1rem; }
        .acp-empty { padding:1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Data model and state helpers
# -----------------------------------------------------------------------------
def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def new_chat() -> dict[str, Any]:
    return {
        "id": uuid.uuid4().hex[:12],
        "title": "New conversation",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "messages": [],
    }


def initialise_state() -> None:
    if "acp_chats" not in st.session_state:
        first_chat = new_chat()
        st.session_state.acp_chats = {first_chat["id"]: first_chat}
        st.session_state.acp_active_chat_id = first_chat["id"]
    if "acp_settings" not in st.session_state:
        st.session_state.acp_settings = {
            "show_timestamps": False,
            "compact_messages": False,
            "response_style": "Balanced",
        }
    if "acp_pending_prompt" not in st.session_state:
        st.session_state.acp_pending_prompt = None


def active_chat() -> dict[str, Any]:
    chats = st.session_state.acp_chats
    active_id = st.session_state.acp_active_chat_id
    if active_id not in chats:
        replacement = new_chat()
        chats[replacement["id"]] = replacement
        st.session_state.acp_active_chat_id = replacement["id"]
        return replacement
    return chats[active_id]


def make_title(text: str, max_length: int = 34) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return "New conversation"
    if len(cleaned) > max_length:
        return cleaned[: max_length - 1].rstrip() + "…"
    return cleaned


def add_message(chat: dict[str, Any], role: str, content: str) -> None:
    chat["messages"].append({"role": role, "content": content, "created_at": now_iso()})
    chat["updated_at"] = now_iso()


def format_chat_markdown(chat: dict[str, Any]) -> str:
    lines = [f"# {chat['title']}", "", f"Exported from {APP_NAME}", ""]
    for message in chat["messages"]:
        label = "You" if message["role"] == "user" else APP_NAME
        lines.extend([f"## {label}", "", message["content"], ""])
    return "\n".join(lines).strip() + "\n"


def generate_demo_response(prompt: str, style: str = "Balanced") -> str:
    """A transparent rule-based demo. Replace this function with Gemini later."""
    text = prompt.strip()
    lower = text.lower()

    if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", lower):
        answer = (
            "Hello! I’m **AI Chatbot Pro**. This build is running in demo mode, so I can "
            "demonstrate the chat experience but I’m not connected to a real AI model yet.\n\n"
            "Try asking about Python, Streamlit, study planning, or how this project works."
        )
    elif any(word in lower for word in ("streamlit", "deploy", "deployment", "web app")):
        answer = (
            "### Streamlit quick guide\n\n"
            "Streamlit turns Python scripts into interactive web apps. For this project:\n\n"
            "1. `main.py` contains the interface and conversation logic.\n"
            "2. `requirements.txt` lists the packages the host must install.\n"
            "3. GitHub stores the project files.\n"
            "4. Streamlit Community Cloud can deploy the app from your repository.\n\n"
            "**Current status:** this is a local, rule-based demo. Gemini integration comes later, "
            "and the API key should be stored in Streamlit Secrets—not in source code."
        )
    elif any(word in lower for word in ("python", "programming", "code", "debug", "error")):
        answer = (
            "### A practical way to approach a coding problem\n\n"
            "1. **Define the expected behaviour** with a small example.\n"
            "2. **Break it into functions** with one clear responsibility each.\n"
            "3. **Test the normal case**, then empty input and unexpected input.\n"
            "4. **Read the first traceback line that points to your own file**; it often identifies the failure location.\n\n"
            "This demo cannot inspect or execute your code yet. Once Gemini is connected, we can make this response genuinely context-aware."
        )
    elif any(word in lower for word in ("study", "exam", "timetable", "revision", "school")):
        answer = (
            "### A simple study-planning framework\n\n"
            "- Pick one specific outcome for each study block.\n"
            "- Use active recall: close the notes and explain the idea from memory.\n"
            "- Practise questions, then review mistakes instead of only rereading.\n"
            "- Leave short breaks between focused blocks and protect your sleep.\n\n"
            "Tell me the subject, topic, and time available if you want a more tailored plan. "
            "(In this demo, the reply is generated from keywords rather than an AI model.)"
        )
    elif any(word in lower for word in ("feature", "features", "roadmap", "build", "project")):
        answer = (
            "### AI Chatbot Pro roadmap\n\n"
            "**In this foundation:** multi-chat sessions, message history, chat titles, delete/clear controls, "
            "suggested prompts, export, and settings.\n\n"
            "**Next:** connect Gemini securely, add model settings, then introduce file-aware conversations "
            "and other features one at a time.\n\n"
            "A useful rule: finish and test one feature before stacking on the next. It makes bugs much easier to isolate."
        )
    elif any(word in lower for word in ("joke", "funny", "make me laugh")):
        answer = (
            "Why did the Python developer wear glasses?\n\n"
            "Because they couldn’t C. 🐍\n\n"
            "Tiny disclaimer: even my jokes are running locally in demo mode."
        )
    elif any(word in lower for word in ("help", "what can you do", "capabilities")):
        answer = (
            "### What you can try here\n\n"
            "- Start and switch between separate conversations.\n"
            "- Rename, clear, or delete a conversation.\n"
            "- Export a chat as Markdown or JSON.\n"
            "- Explore the interface and its settings.\n\n"
            "For now, responses are keyword-based demonstrations. Real reasoning, up-to-date answers, and file analysis require the later Gemini integration."
        )
    else:
        answer = (
            "I’ve received your message. This build is currently a **UI and conversation-logic demo**, "
            "so it cannot understand arbitrary questions like a real AI model yet.\n\n"
            "When we connect Gemini, this same chat interface will pass your message and the conversation "
            "history to the model. For now, try a topic such as **Python**, **Streamlit**, **study planning**, "
            "or **project features** to see the demo response rules."
        )

    if style == "Concise":
        # Keep the first section/paragraph only for the concise demo setting.
        parts = answer.split("\n\n")
        answer = "\n\n".join(parts[:2])
    elif style == "Detailed" and not answer.endswith("\n"):
        answer += "\n\n*Demo note: this response is rule-based, not generated by Gemini.*"
    return answer


def safe_json_export(chat: dict[str, Any]) -> str:
    payload = {
        "app": APP_NAME,
        "version": APP_VERSION,
        "title": chat["title"],
        "created_at": chat["created_at"],
        "updated_at": chat["updated_at"],
        "messages": chat["messages"],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


initialise_state()

if st.session_state.acp_settings.get("compact_messages", False):
    st.markdown(
        "<style>div[data-testid=\"stChatMessage\"] { padding:.5rem .7rem; margin-bottom:.35rem; }</style>",
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# Sidebar: conversations, controls, settings, export
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="acp-brand"><div class="acp-logo">✦</div><div><div class="acp-brand-name">AI Chatbot Pro</div><div class="acp-brand-sub">Your workspace for ideas</div></div></div>',
        unsafe_allow_html=True,
    )

    if st.button("＋  New chat", type="primary", use_container_width=True, key="acp_new_chat"):
        chat = new_chat()
        st.session_state.acp_chats[chat["id"]] = chat
        st.session_state.acp_active_chat_id = chat["id"]
        st.session_state.acp_pending_prompt = None
        st.rerun()

    st.markdown('<div class="acp-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="acp-section-label">Your conversations</div>', unsafe_allow_html=True)

    chats = st.session_state.acp_chats
    ordered_chats = sorted(chats.values(), key=lambda item: item["updated_at"], reverse=True)
    for chat_item in ordered_chats:
        chat_id = chat_item["id"]
        is_active = chat_id == st.session_state.acp_active_chat_id
        count = len(chat_item["messages"])
        label = ("●  " if is_active else "○  ") + chat_item["title"]
        if st.button(
            label,
            key=f"acp_select_{chat_id}",
            use_container_width=True,
            help=f"Open conversation · {count} messages",
            type="secondary" if not is_active else "primary",
        ):
            st.session_state.acp_active_chat_id = chat_id
            st.session_state.acp_pending_prompt = None
            st.rerun()

    current = active_chat()
    st.markdown('<div class="acp-divider"></div>', unsafe_allow_html=True)

    with st.expander("✎  Manage current chat", expanded=False):
        rename_value = st.text_input(
            "Conversation title",
            value=current["title"],
            max_chars=60,
            key=f"acp_rename_input_{current['id']}",
        )
        if st.button("Save title", use_container_width=True, key=f"acp_rename_{current['id']}"):
            cleaned_title = rename_value.strip()
            if cleaned_title:
                current["title"] = make_title(cleaned_title, max_length=60)
                current["updated_at"] = now_iso()
                st.toast("Conversation renamed.")
                st.rerun()
            else:
                st.warning("Enter a title before saving.")

        if st.button("Clear messages", use_container_width=True, key=f"acp_clear_{current['id']}"):
            current["messages"] = []
            current["title"] = "New conversation"
            current["updated_at"] = now_iso()
            st.session_state.acp_pending_prompt = None
            st.toast("Messages cleared.")
            st.rerun()

        if len(chats) > 1:
            if st.button("Delete this chat", use_container_width=True, key=f"acp_delete_{current['id']}"):
                del st.session_state.acp_chats[current["id"]]
                remaining = sorted(
                    st.session_state.acp_chats.values(),
                    key=lambda item: item["updated_at"],
                    reverse=True,
                )
                st.session_state.acp_active_chat_id = remaining[0]["id"]
                st.session_state.acp_pending_prompt = None
                st.toast("Conversation deleted.")
                st.rerun()
        else:
            st.caption("Create another chat before deleting this one.")

    with st.expander("⚙️  Preferences", expanded=False):
        st.session_state.acp_settings["response_style"] = st.selectbox(
            "Demo response style",
            ["Concise", "Balanced", "Detailed"],
            index=["Concise", "Balanced", "Detailed"].index(
                st.session_state.acp_settings.get("response_style", "Balanced")
            ),
            help="Controls the length of rule-based demo replies. This will be adapted for the model later.",
            key="acp_response_style",
        )
        st.session_state.acp_settings["show_timestamps"] = st.toggle(
            "Show message timestamps",
            value=st.session_state.acp_settings.get("show_timestamps", False),
            key="acp_show_timestamps",
        )
        st.session_state.acp_settings["compact_messages"] = st.toggle(
            "Compact chat spacing",
            value=st.session_state.acp_settings.get("compact_messages", False),
            key="acp_compact_messages",
        )

    current = active_chat()
    if current["messages"]:
        st.markdown('<div class="acp-section-label">Export conversation</div>', unsafe_allow_html=True)
        safe_name = re.sub(r"[^a-zA-Z0-9_-]+", "-", current["title"]).strip("-").lower() or "conversation"
        st.download_button(
            "↓  Download Markdown",
            data=format_chat_markdown(current),
            file_name=f"{safe_name}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"acp_export_md_{current['id']}",
        )
        st.download_button(
            "↓  Download JSON",
            data=safe_json_export(current),
            file_name=f"{safe_name}.json",
            mime="application/json",
            use_container_width=True,
            key=f"acp_export_json_{current['id']}",
        )

    st.markdown('<div class="acp-divider"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="acp-note"><b style="color:#d8ccff">DEMO MODE</b><br>Replies are rule-based. Gemini is not connected yet.<br><br>Session history is temporary and may reset when the session restarts.</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Version {APP_VERSION}")


# -----------------------------------------------------------------------------
# Main chat area
# -----------------------------------------------------------------------------
chat = active_chat()

st.markdown(
    '<div class="acp-topline"><span class="acp-eyebrow">A smarter workspace</span><span class="acp-pill">✦ DEMO BUILD</span></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="acp-title">Ideas start here.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="acp-subtitle">A clean space to think, explore, and build. Your conversations stay separate, and you can export them whenever you need.</div>',
    unsafe_allow_html=True,
)

header_col, info_col = st.columns([3, 1])
with header_col:
    st.markdown(f'<div class="acp-chat-title">{html.escape(chat["title"])}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="acp-chat-meta">{len(chat["messages"])} messages · Conversation stored for this session</div>',
        unsafe_allow_html=True,
    )
with info_col:
    st.markdown('<div style="text-align:right;padding-top:.1rem"><span class="acp-pill">● Offline demo</span></div>', unsafe_allow_html=True)

st.markdown('<div class="acp-divider"></div>', unsafe_allow_html=True)

if not chat["messages"]:
    st.markdown(
        '<div class="acp-empty"><div class="acp-empty-icon">✧</div><div class="acp-empty-title">What would you like to explore?</div><div class="acp-empty-copy">Start with a question, sketch an idea, or choose a prompt below. The real AI engine will be connected in a later step.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="acp-section-label">Try asking</div>', unsafe_allow_html=True)
    prompt_columns = st.columns(2)
    suggestions = [
        ("⌘  Explain Streamlit", "Explain what Streamlit is and how this app will be deployed."),
        ("⌁  Help with Python", "Give me a practical checklist for debugging a Python error."),
        ("◷  Plan a study session", "Help me plan a focused study session with breaks."),
        ("✦  Explore this project", "What are the important features and next steps for AI Chatbot Pro?"),
    ]
    for index, (label, prompt_text) in enumerate(suggestions):
        with prompt_columns[index % 2]:
            if st.button(label, use_container_width=True, key=f"acp_suggest_{index}"):
                st.session_state.acp_pending_prompt = prompt_text
                st.rerun()
else:
    for message_index, message in enumerate(chat["messages"]):
        role = message.get("role", "assistant")
        content = str(message.get("content", ""))
        avatar = "🧑‍💻" if role == "user" else "✦"
        with st.chat_message(role, avatar=avatar):
            st.markdown(content)
            if st.session_state.acp_settings.get("show_timestamps"):
                try:
                    shown_time = datetime.fromisoformat(message["created_at"]).astimezone().strftime("%d %b · %I:%M %p")
                except (KeyError, ValueError, TypeError):
                    shown_time = ""
                if shown_time:
                    st.caption(shown_time)
            if role == "assistant":
                with st.expander("Message details", expanded=False):
                    st.caption("This reply was produced by the local demo rules, not by a connected AI model.")
                    st.download_button(
                        "Download this reply",
                        data=content,
                        file_name=f"reply-{message_index + 1}.md",
                        mime="text/markdown",
                        key=f"acp_reply_download_{chat['id']}_{message_index}",
                    )


# Apply suggested prompts and chat input through one processing path.
prompt = st.chat_input("Message AI Chatbot Pro…", key="acp_chat_input")

pending_prompt = st.session_state.get("acp_pending_prompt")
if pending_prompt:
    prompt = pending_prompt
    st.session_state.acp_pending_prompt = None

if prompt is not None:
    cleaned_prompt = prompt.strip()

    if cleaned_prompt:
        current_chat = active_chat()
        is_first_message = len(current_chat["messages"]) == 0

        if is_first_message:
            current_chat["title"] = make_title(cleaned_prompt)

        add_message(current_chat, "user", cleaned_prompt)

        with st.spinner("Preparing demo response…"):
            response = generate_demo_response(
                cleaned_prompt,
                st.session_state.acp_settings.get(
                    "response_style", "Balanced"
                ),
            )

        add_message(current_chat, "assistant", response)
        current_chat["updated_at"] = now_iso()

        st.rerun()

st.markdown(
    '<div style="text-align:center;color:#7f8a9c;'
    'font-size:.75rem;margin-top:.9rem">'
    'AI Chatbot Pro · Foundation build · '
    'Don’t rely on demo replies for factual decisions'
    '</div>',
    unsafe_allow_html=True,
)
