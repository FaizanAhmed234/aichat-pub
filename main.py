from __future__ import annotations

import html
import json
import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st
from google import genai

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
APP_VERSION = "1.0.0"

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
# Gemini Client Setup
# -----------------------------------------------------------------------------
try:
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
except (FileNotFoundError, KeyError):
    gemini_api_key = None

client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None


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


def generate_gemini_response(chat_messages: list[dict[str, Any]], style: str = "Balanced") -> str:
    """Calls the Google GenAI SDK using gemini-2.5-flash with conversation history."""
    if not client:
        return (
            "⚠️ **API Key Missing:** Please configure your `GEMINI_API_KEY` in "
            "`.streamlit/secrets.toml` to connect to Gemini."
        )

    try:
        # Format history for client.chats.create
        history = []
        for msg in chat_messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        config = {}
        if style == "Concise":
            config["system_instruction"] = "Keep your answers brief, direct, and concise."
        elif style == "Detailed":
            config["system_instruction"] = "Provide thorough, well-explained, and detailed answers with comprehensive examples."

        chat_session = client.chats.create(
            model="gemini-3.6-flash",
            history=history,
            config=config if config else None
        )

        latest_message = chat_messages[-1]["content"]
        response = chat_session.send_message(latest_message)
        return response.text

    except Exception as e:
        return f"❌ **Error communicating with Gemini:** `{str(e)}`"


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
        '<div class="acp-brand"><div class="acp-logo">✦</div><div><div class="acp-brand-name">AI Chatbot Pro</div><div class="acp-brand-sub">Powered by Gemini</div></div></div>',
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
            "Model response style",
            ["Concise", "Balanced", "Detailed"],
            index=["Concise", "Balanced", "Detailed"].index(
                st.session_state.acp_settings.get("response_style", "Balanced")
            ),
            help="Adjusts system instructions to make responses concise, balanced, or detailed.",
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
    status_text = "<b style='color:#6ee7d8'>GEMINI CONNECTED</b>" if client else "<b style='color:#f87171'>API KEY MISSING</b>"
    st.markdown(
        f'<div class="acp-note">{status_text}<br>Powered by `gemini-2.5-flash`.<br><br>Session history is kept for this browser session.</div>',
        unsafe_allow_html=True,
    )
    st.caption(f"Version {APP_VERSION}")


# -----------------------------------------------------------------------------
# Main chat area
# -----------------------------------------------------------------------------
chat = active_chat()

st.markdown(
    '<div class="acp-topline"><span class="acp-eyebrow">A smarter workspace</span><span class="acp-pill">✦ GEMINI 2.5 FLASH</span></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="acp-title">Ideas start here.</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="acp-subtitle">A clean space to think, explore, and build with Gemini. Your conversations stay separate, and you can export them whenever you need.</div>',
    unsafe_allow_html=True,
)

header_col, info_col = st.columns([3, 1])
with header_col:
    st.markdown(f'<div class="acp-chat-title">{html.escape(chat["title"])}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="acp-chat-meta">{len(chat["messages"])} messages · Multi-turn chat active</div>',
        unsafe_allow_html=True,
    )
with info_col:
    pill_label = "● Connected" if client else "○ Key missing"
    st.markdown(f'<div style="text-align:right;padding-top:.1rem"><span class="acp-pill">{pill_label}</span></div>', unsafe_allow_html=True)

st.markdown('<div class="acp-divider"></div>', unsafe_allow_html=True)

if not chat["messages"]:
    st.markdown(
        '<div class="acp-empty"><div class="acp-empty-icon">✧</div><div class="acp-empty-title">What would you like to explore?</div><div class="acp-empty-copy">Start with a question, sketch an idea, or choose a prompt below. Gemini is ready to assist you.</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="acp-section-label">Try asking</div>', unsafe_allow_html=True)
    prompt_columns = st.columns(2)
    suggestions = [
        ("⌘  Explain Streamlit", "Explain what Streamlit is and how to build reactive web applications with it."),
        ("⌁  Help with Python", "Give me a practical checklist for debugging a complex Python asynchronous application."),
        ("◷  Plan a study session", "Help me plan a focused study session using the Pomodoro technique."),
        ("✦  Write a python script", "Write a clean Python script to parse large log files and count error frequencies."),
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
        avatar = "🧑‍💻" if role == "user" else "✨"

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
                    st.caption("Generated by Google Gemini (`gemini-2.5-flash`).")
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

        with st.spinner("Gemini is thinking…"):
            response = generate_gemini_response(
                current_chat["messages"],
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
    'AI Chatbot Pro · Powered by Google GenAI SDK & Gemini 2.5 Flash'
    '</div>',
    unsafe_allow_html=True,
)
