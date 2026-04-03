import os
import sys
import base64
import html
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "src"))

from chatbot import MediaPulseChatbot

load_dotenv()


# PAGE CONFIG

logo_file = Path("E:\\mediapulse_ui_project\\data\\Logo\\Logo.png")
page_icon = "📈"

if logo_file.exists():
    try:
        page_icon = Image.open(logo_file)
    except Exception:
        page_icon = "📈"

st.set_page_config(
    page_title="MediaPulse AI",
    page_icon=page_icon,
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

if st.session_state.theme_mode == "dark":
    main_bg = "#0f172a"
    sidebar_bg = "#111827"
    card_bg = "#1f2937"
    soft_bg = "#111827"
    text_color = "#f9fafb"
    subtext_color = "#d1d5db"
    muted_text = "#9ca3af"
    border_color = "#374151"
    input_bg = "#111827"
    toggle_track = "#334155"
    toggle_track_active = "#6366f1"
    toggle_knob = "#ffffff"
    hover_bg = "#1e293b"
    button_bg = "#6366f1"
    button_hover_bg = "#4f46e5"
    toggle_bg = "#f3f4f6"
    toggle_icon = "#111827"
    user_bubble_bg = "#1e293b"
    user_bubble_text = "#f9fafb"
    user_avatar_bg = "#6366f1"
    user_avatar_text = "#ffffff"
    sidebar_toggle_bg = "#1f2937"
else:
    main_bg = "#f7f8fc"
    sidebar_bg = "#ffffff"
    card_bg = "#ffffff"
    soft_bg = "#f8fafc"
    text_color = "#111827"
    subtext_color = "#374151"
    muted_text = "#6b7280"
    border_color = "#94a3b8"
    input_bg = "#ffffff"
    toggle_track = "#94a3b8"
    toggle_track_active = "#6366f1"
    toggle_knob = "#ffffff"
    hover_bg = "#f8fafc"
    button_bg = "#6366f1"
    button_hover_bg = "#4f46e5"
    toggle_bg = "#1b53c4"
    toggle_icon = "#111827"
    user_bubble_bg = "#eef2ff"
    user_bubble_text = "#111827"
    user_avatar_bg = "#6366f1"
    user_avatar_text = "#ffffff"
    sidebar_toggle_bg = "#ffffff"


# CUSTOM CSS

st.markdown(f"""
<style>
            
    /* 🚫 REMOVE STREAMLIT TOP HEADER (BLACK BAR) */
    header[data-testid="stHeader"] {{
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }}

    [data-testid="stDecoration"] {{
        display: none !important;
    }}
            
    html, body, .stApp, [data-testid="stAppViewContainer"], .main {{
        background: {main_bg} !important;
        color: {text_color} !important;
        font-family: "Inter", "Segoe UI", sans-serif !important;
    }}

    [data-testid="stAppViewContainer"] > .main {{
        width: 100% !important;
        max-width: 100% !important;
    }}

            
    footer {{
        display: none !important;
    }}
            
    [data-testid="stToolbar"] {{
        display: none !important;
    }}
            
    /* sidebar width */
    section[data-testid="stSidebar"] {{
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
    }}

    /* when sidebar is collapsed */
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        border-right: none !important;
    }}
            
    /* 🎯 SIDEBAR TOGGLE BUTTON FIX */
    button[data-testid="collapsedControl"],
    button[kind="header"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: fixed !important;
        top: 14px !important;
        z-index: 9999 !important;
        background: {sidebar_toggle_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 6px !important;
        width: 36px !important;
        height: 36px !important;
        min-width: 36px !important;
        min-height: 36px !important;
    }}

    button[data-testid="collapsedControl"] {{
        left: 14px !important;
    }}

    button[kind="header"] {{
        left: 248px !important;
    }}

    button[data-testid="collapsedControl"] svg,
    button[kind="header"] svg {{
        fill: {text_color} !important;
        width: 18px !important;
        height: 18px !important;
    }}

    button[data-testid="collapsedControl"]:hover,
    button[kind="header"]:hover {{
        background: {hover_bg} !important;
    }}

    .block-container {{
        padding-top: 0.55rem !important;
        padding-bottom: 1rem !important;
        max-width: 1100px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
                    
    /* ===== SIDEBAR TOP SPACING ===== */
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1.8rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-bottom: 1rem !important;
    }}

    /* ===== SIDEBAR BRAND ===== */
    .sidebar-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 0.2rem;
        margin-bottom: 0.9rem;
        padding: 0.2rem 0.15rem 0.35rem 0.15rem;
    }}

    .sidebar-brand-logo {{
        width: 38px;
        height: 38px;
        object-fit: contain;
        flex-shrink: 0;
        display: block;
    }}

    section[data-testid="stSidebar"] img {{
        max-width: 38px !important;
        width: 38px !important;
        height: 38px !important;
    }}

    .sidebar-brand-text {{
        font-size: 1.80rem;
        font-weight: 750;
        color: {text_color};
        line-height: 1.05;
        letter-spacing: -0.02em;
        margin: 0;
    }}
            

    .small-note {{
        color: {subtext_color};
        font-size: 0.96rem;
        line-height: 1.7;
        margin-bottom: 0.9rem;
    }}

    [data-testid="stChatMessage"] {{
        background: transparent !important;
        margin-bottom: 10px !important;
    }}

    [data-testid="stBottomBlockContainer"] {{
        background: {main_bg} !important;
        border-top: none !important;
        padding-bottom: 10px !important;
    }}

    [data-testid="stChatInput"] {{
        background: {main_bg} !important;
        border-top: none !important;
        padding: 12px 0 !important;
        display: flex !important;
        justify-content: center !important;
    }}

    [data-testid="stChatInput"] > div {{
        max-width: 850px;
        width: 100%;
        margin: auto;
    }}

    [data-testid="stChatInput"] textarea {{
        background: {input_bg} !important;
        color: {text_color} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        padding: 14px 50px 14px 18px !important;
        font-size: 15px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        caret-color: {text_color} !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {muted_text} !important;
    }}

    [data-testid="stChatInput"] button {{
        position: absolute !important;
        right: 12px !important;
        bottom: 10px !important;
        background: {button_bg} !important;
        border: none !important;
        border-radius: 50% !important;
        height: 36px !important;
        width: 36px !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
    }}

    [data-testid="stChatInput"] button:hover {{
        background: {button_hover_bg} !important;
    }}

    code {{
        background: transparent !important;
        color: {subtext_color} !important;
        padding: 0 !important;
        border-radius: 0 !important;
        font-size: inherit !important;
        font-family: "Inter", "Segoe UI", sans-serif !important;
    }}

    .welcome-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 24px;
        padding: 24px 26px;
        margin-bottom: 22px;
        box-shadow: 0 4px 18px rgba(17, 24, 39, 0.03);
    }}

    .welcome-text {{
        font-size: 1.05rem;
        color: {subtext_color};
        line-height: 1.7;
        margin-bottom: 1rem;
    }}

    .section-heading {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {text_color};
        margin-top: 0.6rem;
        margin-bottom: 0.85rem;
    }}

    .result-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 22px;
        padding: 18px;
        margin-top: 12px;
        margin-bottom: 12px;
    }}

    .mini-grid {{
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 18px;
    }}

    .mini-box {{
        background: {soft_bg};
        border: 1px solid {border_color};
        border-radius: 18px;
        padding: 12px;
        min-height: 92px;
    }}

    .mini-label {{
        font-size: 0.78rem;
        color: {muted_text};
        margin-bottom: 6px;
        line-height: 1.3;
    }}

    .mini-value {{
        font-size: 0.95rem;
        font-weight: 700;
        color: {text_color};
        line-height: 1.3;
    }}

    .post-card {{
        background: {soft_bg};
        border: 1px solid {border_color};
        border-radius: 16px;
        padding: 14px;
        margin-top: 10px;
    }}
            
    [data-testid="stMarkdownContainer"],
    [data-testid="stMarkdownContainer"] * {{
        color: {text_color} !important;
        font-family: "Inter", "Segoe UI", sans-serif !important;
    }}

    .stButton > button {{
        width: 100%;
        border-radius: 14px !important;
        border: 1px solid {border_color} !important;
        background: {card_bg} !important;
        color: {text_color} !important;
        font-weight: 600 !important;
        min-height: 50px !important;
        box-shadow: none !important;
        font-family: "Inter", "Segoe UI", sans-serif !important;
    }}

    .stButton > button:hover {{
        border-color: {border_color} !important;
        background: {hover_bg} !important;
    }}

    button[kind="secondary"][data-testid="baseButton-secondary"][id*="post_type_"] {{
        min-height: 160px !important;
        border-radius: 20px !important;
        border: 1px solid {border_color} !important;
        background: {card_bg} !important;
        color: {text_color} !important;
        font-weight: 500 !important;
        font-size: 1.6rem !important;
        line-height: 1.3 !important;
        white-space: pre-wrap !important;
        text-align: center !important;
        padding: 30px 12px !important;
        box-shadow: none !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
        align-items: center !important;
    }}

    button[kind="secondary"][data-testid="baseButton-secondary"][id*="post_type_"]:hover {{
        border-color: {border_color} !important;
        background: {hover_bg} !important;
        transform: translateY(-1px);
    }}

    button[kind="secondary"][data-testid="baseButton-secondary"][id*="post_type_"]:focus {{
        border-color: #94a3b8 !important;
        box-shadow: 0 0 0 1px #94a3b8 !important;
    }}

    @media (max-width: 900px) {{
        .mini-grid {{
            grid-template-columns: 1fr;
        }}
    }}

</style>
""", unsafe_allow_html=True)


# CONFIG

csv_path = os.getenv("CSV_PATH", "mediapulse_dataset_updated.csv")
persist_directory = os.getenv("CHROMA_DIR", "chroma_db")
collection_name = os.getenv("CHROMA_COLLECTION", "mediapulse_dataset")
logo_path = os.getenv("LOGO_PATH", "E:/mediapulse_ui_project/FullLogo_Transparent_NoBuffer.png")


# LOAD BOT

@st.cache_resource
def load_bot():
    return MediaPulseChatbot(
        csv_path=csv_path,
        persist_directory=persist_directory,
        collection_name=collection_name,
    )

try:
    bot = load_bot()
except Exception as e:
    st.error("Vector store not found or app setup is incomplete.")
    st.exception(e)
    st.stop()


# SESSION STATE

if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "post_type"

if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "post_type": "",
        "post_description": "",
        "current_caption": "",
        "current_hashtags": "",
    }

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None



# SIDE BAR

with st.sidebar:
    if logo_file.exists():
        encoded_logo = base64.b64encode(logo_file.read_bytes()).decode()
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <img src="data:image/png;base64,{encoded_logo}" class="sidebar-brand-logo">
                <div class="sidebar-brand-text">MediaPulse AI</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-text">MediaPulse AI</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    

    theme_label = "🌙 Switch to Dark Mode" if st.session_state.theme_mode == "light" else "☀️ Switch to Light Mode"

    if st.button(theme_label, use_container_width=True):
        st.session_state.theme_mode = "dark" if st.session_state.theme_mode == "light" else "light"
        st.rerun()

    st.markdown(
        "<div class='small-note'>AI assistant for better Instagram posting suggestions.</div>",
        unsafe_allow_html=True
    )

    st.markdown("### How it works")
    st.markdown("""
    1. Choose your **post type**  
    2. Enter your **post description**  
    3. Add your **caption**  
    4. Add your **hashtags**  
    5. MediaPulse AI identifies trends from top-performing Instagram content  
    6. Get optimized suggestions for **best time**, **best day**, **caption**, and **hashtags**
        """)

    st.markdown("## Supported post types")
    st.markdown("""
    - 🎬 **Reels** → Boost reach with short-form video content  
    - 🖼️ **Posts** → Drive engagement with high-quality visuals  
    - 📚 **Carousels** → Increase likes with multi-slide storytelling  
        """)

    if st.button("Reset Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.step = "post_type"
        st.session_state.form_data = {
            "post_type": "",
            "post_description": "",
            "current_caption": "",
            "current_hashtags": "",
        }
        st.session_state.latest_result = None
        st.rerun()

    


# FIRST MESSAGE

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Choose your post type to begin."
    })


# WELCOME CARD

if st.session_state.step == "post_type" and not st.session_state.latest_result:
    st.markdown("""
    <div class="welcome-card">
        <div class="welcome-text">
            Start by choosing your post type. Then I'll guide you step by step and suggest the best posting time, caption, and hashtags.
        </div>
    </div>
    <br><br>
    """, unsafe_allow_html=True)


# POST TYPE SELECTOR

def select_post_type(post_type: str):
    st.session_state.form_data["post_type"] = post_type
    st.session_state.step = "post_description"
    st.session_state.messages.append({
        "role": "user",
        "content": post_type
    })
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Great. Now send your **post description**.\n\nExample: nature post with mountains, sunset, calm travel vibe"
    })
    st.rerun()


if st.session_state.step == "post_type":
    st.markdown("<div class='section-heading'>Select post type</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button(
            "🎬\n\nReel",
            key="post_type_reel",
            use_container_width=True
        ):
            select_post_type("reel")

    with c2:
        if st.button(
            "🖼️\n\nPost",
            key="post_type_post",
            use_container_width=True
        ):
            select_post_type("post")

    with c3:
        if st.button(
            "📚\n\nCarousel",
            key="post_type_carousel",
            use_container_width=True
        ):
            select_post_type("carousel")

    st.markdown("<br>", unsafe_allow_html=True)


# DISPLAY CHAT

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
    else:
        safe_text = html.escape(msg["content"])
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-end; align-items:flex-end; gap:10px; margin:12px 0;">
                <div style="
                    background:{user_bubble_bg};
                    color:{user_bubble_text};
                    padding:10px 14px;
                    border-radius:14px;
                    max-width:420px;
                    box-shadow:0 1px 4px rgba(0,0,0,0.04);
                    word-break:break-word;
                ">
                    {safe_text}
                </div>
                <div style="
                    width:36px;
                    height:36px;
                    border-radius:50%;
                    background:{user_avatar_bg};
                    color:{user_avatar_text};
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:16px;
                    font-weight:700;
                    flex-shrink:0;
                ">
                    👨🏼‍💻
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# RESULT DISPLAY FUNCTION

def show_result(result):

    st.markdown("""
    <div class='mini-grid'>
        <div class='mini-box'>
            <div class='mini-label'>Best posting time</div>
            <div class='mini-value'>{}</div>
        </div>
        <div class='mini-box'>
            <div class='mini-label'>Best day</div>
            <div class='mini-value'>{}</div>
        </div>
        <div class='mini-box'>
            <div class='mini-label'>Matched examples</div>
            <div class='mini-value'>{}</div>
        </div>
        <div class='mini-box'>
            <div class='mini-label'>Estimated likes uplift</div>
            <div class='mini-value'>{}</div>
        </div>
        <div class='mini-box'>
            <div class='mini-label'>Estimated reach uplift</div>
            <div class='mini-value'>{}</div>
        </div>
    </div>
    """.format(
        result.get("best_posting_time", "N/A"),
        result.get("best_day", "N/A"),
        result.get("matched_examples_count", 0),
        result.get("estimated_likes_uplift", "N/A"),
        result.get("estimated_reach_uplift", "N/A")
    ), unsafe_allow_html=True)

    st.markdown("### Suggested caption")
    current_caption = result.get("current_caption", "").strip()
    if current_caption:
        st.write(f"Current caption: {result.get('current_caption', 'N/A')}")
        st.write(f"Improved version: {result.get('suggested_caption', 'N/A')}")
    else:
        st.write(result.get("suggested_caption", "N/A"))

    st.markdown("### Suggested hashtags")
    st.write(result.get("suggested_hashtags", "N/A"))

    st.caption("Estimated uplift is based on how the suggested caption aligns with similar high-performing posts.")

    st.markdown("### Why this suggestion?")
    reasons = result.get("reasons", [])
    if reasons:
        for reason in reasons:
            st.write(f"- {reason}")
    else:
        st.write("- Based on similar high-performing posts from your dataset.")

    similar_posts = result.get("similar_posts", [])
    if similar_posts:
        st.markdown("### Top similar results")
        for i, item in enumerate(similar_posts, start=1):
            posting_hour = item.get("posting_hour", "")
            posting_label = ""
            if posting_hour != "":
                try:
                    hour = int(float(posting_hour))
                    suffix = "AM" if hour < 12 else "PM"
                    hour_12 = hour % 12
                    if hour_12 == 0:
                        hour_12 = 12
                    posting_label = f"{hour_12} {suffix}"
                except Exception:
                    posting_label = str(item.get("posting_time", ""))
            else:
                posting_label = str(item.get("posting_time", ""))

            st.markdown(f"""
            <div class="post-card">
                <b>Match {i}</b><br><br>
                <b>Caption:</b> {html.escape(str(item.get('caption', '')))}<br>
                <b>Hashtags:</b> {html.escape(str(item.get('hashtags', '')))}<br>
                <b>Posting Time:</b> {html.escape(posting_label)}<br>
                <b>Day:</b> {html.escape(str(item.get('day_of_week', '')))}<br>
                <b>Content Type:</b> {html.escape(str(item.get('content_type', '')))}<br>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# USER INPUT

user_input = st.chat_input("Type your answer here...")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    if st.session_state.step == "post_type":
        value = user_input.strip().lower()

        if value not in ["reel", "post", "carousel"]:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Please choose a valid post type: **reel**, **post**, or **carousel**."
            })
        else:
            st.session_state.form_data["post_type"] = value
            st.session_state.step = "post_description"
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Great. Now send your **post description**.\n\nExample: nature post with mountains, sunset, calm travel vibe"
            })

    elif st.session_state.step == "post_description":
        st.session_state.form_data["post_description"] = user_input.strip()
        st.session_state.step = "current_caption"
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Nice. Now send your **current caption**.\n\nExample: Lost in the beauty of nature 🌄"
        })

    elif st.session_state.step == "current_caption":
        st.session_state.form_data["current_caption"] = user_input.strip()
        st.session_state.step = "current_hashtags"
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Good. Now send your **current hashtags**.\n\nExample: #nature #sunset #travel"
        })

    elif st.session_state.step == "current_hashtags":
        st.session_state.form_data["current_hashtags"] = user_input.strip()

        with st.spinner("Analyzing similar posts..."):
            result = bot.generate_recommendation(
                post_type=st.session_state.form_data["post_type"],
                post_description=st.session_state.form_data["post_description"],
                current_caption=st.session_state.form_data["current_caption"],
                current_hashtags=st.session_state.form_data["current_hashtags"],
            )

        st.session_state.latest_result = result
        st.session_state.step = "done"

        st.session_state.messages.append({
            "role": "assistant",
            "content": "Done — I analyzed your post and generated suggestions below."
        })

    elif st.session_state.step == "done":
        st.session_state.messages.append({
            "role": "assistant",
            "content": "You already have a result below. Use **Reset Chat** in the sidebar to try another post."
        })

    st.rerun()


# SHOW FINAL RESULT

if st.session_state.latest_result:
    show_result(st.session_state.latest_result)