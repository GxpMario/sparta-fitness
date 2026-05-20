import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, timedelta
import altair as alt

st.set_page_config(page_title="Gxpr Stats", layout="wide", page_icon="▣")

BLOOMBERG_CSS = """
<style>
/* Restore Streamlit's Material Icons (used for expander arrows etc.) */
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');

/* Consolas on all text — exclude SVG/icon elements */
body,
p, h1, h2, h3, h4, h5, h6, li, a, td, th,
input, textarea, select, label, option,
.stMarkdown, .stText,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"],
[data-baseweb="tab"] div,
.streamlit-expanderHeader p,
button, .stButton > button, .stFormSubmitButton > button, .stRadio > label > div {
    font-family: Consolas, 'Courier New', monospace !important;
}
.material-icons, i.material-icons {
    font-family: 'Material Icons' !important;
    font-size: 18px !important;
    font-style: normal !important;
}

/* ── Base ── */
.stApp { background-color: #0A0D14 !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ── Metric tiles ── */
[data-testid="stMetric"] {
    background-color: #0E1220 !important;
    border: 1px solid #3C4555 !important;
    border-top: 2px solid #FF9900 !important;
    padding: 14px 18px !important;
}
[data-testid="stMetricValue"] {
    color: #FF9900 !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    line-height: 1.15 !important;
}
[data-testid="stMetricLabel"] {
    color: #00CCFF !important;
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

/* ── Inputs ── */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea, .stDateInput input,
.stSelectbox [data-baseweb="select"] > div input {
    background-color: #0C0F18 !important;
    color: #E0E0E0 !important;
    border: 1px solid #3C4555 !important;
    border-radius: 0 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    caret-color: #FF9900;
}
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #FF9900 !important;
    box-shadow: 0 0 0 1px #FF990030 !important;
    outline: none !important;
}

/* Select box */
.stSelectbox [data-baseweb="select"] > div {
    background-color: #0C0F18 !important;
    border: 1px solid #3C4555 !important;
    border-radius: 0 !important;
    color: #E0E0E0 !important;
    font-weight: 600 !important;
}

/* ── Widget labels ── */
label,
[data-testid="stWidgetLabel"] p,
.stCheckbox label,
.stRadio label {
    color: #00CCFF !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Checkboxes ── */
.stCheckbox input[type="checkbox"] { accent-color: #FF9900; }

/* ── Number steppers ── */
.stNumberInput [data-testid="stNumberInputStepUp"],
.stNumberInput [data-testid="stNumberInputStepDown"] {
    background-color: #1C2028 !important;
    border-color: #3C4555 !important;
    color: #666 !important;
    border-radius: 0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #0A0D14 !important;
    color: #FF9900 !important;
    border: 1px solid #FF9900 !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.45rem 1rem !important;
    transition: background 0.1s, color 0.1s;
}
.stButton > button:hover {
    background-color: #FF9900 !important;
    color: #000000 !important;
}

/* Form submit */
.stFormSubmitButton > button {
    background-color: #110D00 !important;
    color: #FF9900 !important;
    border: 1px solid #FF9900 !important;
    border-radius: 0 !important;
    width: 100% !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 0.65rem !important;
    margin-top: 0.6rem;
    transition: background 0.1s, color 0.1s;
}
.stFormSubmitButton > button:hover {
    background-color: #FF9900 !important;
    color: #000000 !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background-color: #0E1220 !important;
    color: #00CCFF !important;
    border: 1px solid #3C4555 !important;
    border-radius: 0 !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.6rem 0.9rem !important;
}
.streamlit-expanderContent {
    background-color: #0C0F18 !important;
    border: 1px solid #3C4555 !important;
    border-top: none !important;
    padding: 1rem 1.1rem 0.9rem 1.1rem !important;
}

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background-color: #0A0D14 !important;
    border-bottom: 1px solid #3C4555 !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    background-color: #0A0D14 !important;
    border-radius: 0 !important;
    border: 1px solid #3C4555 !important;
    border-bottom: none !important;
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.5rem 1.4rem !important;
}
[data-baseweb="tab"] div { color: #5A6A80 !important; }
[data-baseweb="tab"][aria-selected="true"] {
    background-color: #0E1220 !important;
    border-color: #FF9900 !important;
    border-bottom: 2px solid #FF9900 !important;
}
[data-baseweb="tab"][aria-selected="true"] div { color: #FF9900 !important; }
 
/* ── Radio ── */
.stRadio [data-baseweb="radio"] span:first-child { border-color: #2A3A50 !important; }
.stRadio [data-baseweb="radio"] [aria-checked="true"] span:first-child {
    background: #FF9900 !important;
    border-color: #FF9900 !important;
}

/* ── Alerts ── */
[data-testid="stNotification"], .stAlert { border-radius: 0 !important; }
.stInfo    > div { background-color: #080C16 !important; border-left: 3px solid #00CCFF !important; }
.stSuccess > div { background-color: #071200 !important; border-left: 3px solid #33AA00 !important; }
.stWarning > div { background-color: #130A00 !important; border-left: 3px solid #FF9900 !important; }
.stError   > div { background-color: #130000 !important; border-left: 3px solid #CC2200 !important; }

/* ── HR / captions / dataframe ── */
hr { border: none !important; border-top: 1px solid #3C4555 !important; margin: 0.8rem 0 !important; }
[data-testid="stCaptionContainer"] { color: #5A6A80 !important; font-size: 0.7rem !important; }
[data-testid="stDataFrame"] { border: 1px solid #3C4555 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #0A0D14; }
::-webkit-scrollbar-thumb { background: #3C4555; border-radius: 0; }
::-webkit-scrollbar-thumb:hover { background: #FF9900; }

[data-testid="column"] { padding: 0 0.3rem !important; }

/* ── Password field ── */
.stTextInput input[type="password"] {
    letter-spacing: 0.3em;
    font-size: 1.1rem !important;
}
</style>
"""

st.markdown(BLOOMBERG_CSS, unsafe_allow_html=True)


def section_header(text):
    st.markdown(
        f"""<div style='
            background:#0E1220;
            padding:8px 16px 7px 16px;
            margin:1.8rem 0 1rem 0;
            border-bottom:1px solid #FF9900;
        '>
            <span style='color:#FF9900;font-family:Consolas,monospace;
                         font-size:0.82rem;font-weight:700;letter-spacing:0.22em;'>
                {text}
            </span>
        </div>""",
        unsafe_allow_html=True,
    )


def form_section_label(text):
    st.markdown(
        f"""<div style='
            color:#00CCFF;
            font-family:Consolas,monospace;
            font-size:0.7rem;
            font-weight:700;
            letter-spacing:0.18em;
            margin:1rem 0 0.4rem 0;
            padding-bottom:3px;
            border-bottom:1px solid #3C4555;
        '>{text}</div>""",
        unsafe_allow_html=True,
    )


# ── Password gate ────────────────────────────────────────────────────────────
def check_password():
    def password_entered():
        if "auth" in st.secrets and st.session_state["password"] == st.secrets["auth"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("""
            <div style='text-align:center;padding:6rem 0 3rem 0;'>
                <div style='color:#FF9900;font-family:Consolas,monospace;
                            font-size:2.2rem;font-weight:700;letter-spacing:0.08em;'>
                    Gxpr Stats
                </div>
                <div style='color:#3C4555;font-size:0.8rem;letter-spacing:0.25em;
                            margin-top:0.6rem;font-family:Consolas,monospace;'>
                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                </div>
                <div style='color:#5A6A80;font-family:Consolas,monospace;
                            font-size:0.72rem;letter-spacing:0.2em;margin-top:0.6rem;'>
                    AUTHENTICATION REQUIRED
                </div>
            </div>
        """, unsafe_allow_html=True)
        _, col, _ = st.columns([1.5, 1, 1.5])
        with col:
            st.text_input("ACCESS CODE", type="password", on_change=password_entered, key="password")
        return False

    elif not st.session_state["password_correct"]:
        _, col, _ = st.columns([1.5, 1, 1.5])
        with col:
            st.text_input("ACCESS CODE", type="password", on_change=password_entered, key="password")
            st.markdown(
                "<div style='color:#CC2200;font-family:Consolas,monospace;font-size:0.75rem;"
                "font-weight:700;text-align:center;letter-spacing:0.12em;margin-top:0.4rem;'>"
                "ACCESS DENIED</div>",
                unsafe_allow_html=True,
            )
        return False

    return True


# ── Main app ─────────────────────────────────────────────────────────────────
if check_password():

    # Header bar
    st.markdown("""
        <div style='background:#0E1220;border-bottom:1px solid #FF9900;
                    padding:0.6rem 1rem 0.65rem 1rem;margin-bottom:0.5rem;
                    display:flex;justify-content:space-between;align-items:baseline;'>
            <span style='color:#FF9900;font-family:Consolas,monospace;
                         font-size:1.45rem;font-weight:700;letter-spacing:0.06em;'>
                Gxpr Stats
            </span>
            <span style='color:#5A6A80;font-family:Consolas,monospace;
                         font-size:0.65rem;font-weight:700;letter-spacing:0.2em;'>
                PERSONAL ANALYTICS SYSTEM
            </span>
        </div>
    """, unsafe_allow_html=True)

    # ── Data load ─────────────────────────────────────────────────────────────
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        df_raw = conn.read(ttl=0)
        for col in ["Cardio Type", "Comments", "Weight Band"]:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].fillna("N/A").astype(str)
        df_raw.columns = df_raw.columns.str.strip()
        df_raw = df_raw.dropna(how="all")
    except Exception as e:
        st.error(f"DATA LOAD ERROR: {e}")
        df_raw = pd.DataFrame()

    # ── Data processing ───────────────────────────────────────────────────────
    df = pd.DataFrame()
    chart_df = pd.DataFrame()

    if not df_raw.empty:
        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(), errors="coerce")
        df = df.dropna(subset=["Date"])
        df["Date_Only"] = df["Date"].dt.date

        for col in ["Pullups", "Pushups", "Squats", "Burpees", "Cardio Min/Reps", "Weight", "Fat_Pct", "Waist_cm"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        for col in ["Abs", "Weights", "Stretched"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().isin(["true", "1", "1.0", "yes", "y", "checked"])

        # Latest comment banner
        latest = df.sort_values("Date", ascending=False).iloc[0]
        comment = latest["Comments"]
        if comment and comment != "N/A":
            st.markdown(
                f"<div style='background:#0E1220;border-left:3px solid #FF9900;"
                f"padding:0.5rem 1rem;font-family:Consolas,monospace;"
                f"font-size:0.88rem;font-weight:500;margin-bottom:0.5rem;'>"
                f"<span style='color:#5A6A80;font-size:0.72rem;'>"
                f"[{latest['Date_Only'].strftime('%Y-%m-%d')}]</span>"
                f"&nbsp;&nbsp;<span style='color:#E0E0E0;'>{comment}</span></div>",
                unsafe_allow_html=True,
            )

    # ── Filtering ─────────────────────────────────────────────────────────────
    section_header("INSIGHTS")

    if not df.empty:
        view_opt = st.radio(
            "TIME RANGE",
            ["Full History", "Last 12 Months", "Last 3 Months", "Last Month", "Last Week"],
            horizontal=True,
        )
        st.caption(f"Latest entry: {df['Date_Only'].max().strftime('%Y-%m-%d')}")

        chart_df = df.copy()
        today = date.today()
        if view_opt == "Last Week":
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=7))]
        elif view_opt == "Last Month":
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=30))]
        elif view_opt == "Last 3 Months":
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=90))]
        elif view_opt == "Last 12 Months":
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=365))]

        p1, p2, p3, p4, p5 = st.columns(5)
        p1.metric("Kickboxing Sessions", len(chart_df[chart_df["Cardio Type"] == "Kickboxing"]))
        p2.metric("Weight Sessions", len(chart_df[chart_df["Weights"] == True]))
        p3.metric("Stretch Sessions", len(chart_df[chart_df["Stretched"] == True]))
        p4.metric("Pull-up Reps", int(chart_df["Pullups"].sum()) if "Pullups" in chart_df.columns else 0)
        p5.metric("Skip (min)", int(chart_df[chart_df["Cardio Type"] == "Skip"]["Cardio Min/Reps"].sum()))

    # ── Body progress trends ──────────────────────────────────────────────────
    if not chart_df.empty:
        section_header("BODY PROGRESS TRENDS")

        m1, m2, m3 = st.columns(3)

        def get_period_latest(col):
            valid = chart_df[chart_df[col] > 0].sort_values("Date", ascending=False)
            if not valid.empty:
                return str(valid.iloc[0][col]), valid.iloc[0]["Date_Only"].strftime("%Y-%m-%d")
            return "N/A", "—"

        v1, d1 = get_period_latest("Weight")
        v2, d2 = get_period_latest("Fat_Pct")
        v3, d3 = get_period_latest("Waist_cm")
        m1.metric("Weight", f"{v1} kg", help=f"As of {d1}")
        m2.metric("Fat %", f"{v2}%", help=f"As of {d2}")
        m3.metric("Waist", f"{v3} cm", help=f"As of {d3}")

        def make_chart(data, col, color, y_title, title):
            ax = dict(
                labelColor="#5A6A80",
                titleColor="#00CCFF",
                gridColor="#0E1220",
                domainColor="#3C4555",
                tickColor="#3C4555",
                labelFontSize=11,
                titleFontSize=11,
                labelFont="Consolas",
                titleFont="Consolas",
            )
            return (
                alt.Chart(data)
                .mark_line(
                    point=alt.OverlayMarkDef(color=color, size=40, filled=True),
                    color=color, strokeWidth=2,
                )
                .encode(
                    x=alt.X("Date_Only:T", title="DATE",
                             axis=alt.Axis(format="%b %Y", labelAngle=-30, **ax)),
                    y=alt.Y(f"{col}:Q", scale=alt.Scale(zero=False), title=y_title,
                             axis=alt.Axis(**ax)),
                    tooltip=[
                        alt.Tooltip("Date_Only:T", title="Date", format="%Y-%m-%d"),
                        alt.Tooltip(f"{col}:Q", title=y_title),
                    ],
                )
                .properties(
                    title=alt.TitleParams(
                        text=title, color="#00CCFF", fontSize=11,
                        font="Consolas", anchor="start", fontWeight=700,
                    ),
                    height=320, background="#0A0D14",
                )
                .configure_view(strokeOpacity=0)
            )

        tab1, tab2, tab3 = st.tabs(["WEIGHT", "BODY FAT %", "WAIST"])
        with tab1:
            w_data = chart_df[chart_df["Weight"] > 0]
            if not w_data.empty:
                st.altair_chart(make_chart(w_data, "Weight", "#FF9900", "WEIGHT (kg)", "WEIGHT"), use_container_width=True)
            else:
                st.info("No weight data in selected period.")
        with tab2:
            f_data = chart_df[chart_df["Fat_Pct"] > 0]
            if not f_data.empty:
                st.altair_chart(make_chart(f_data, "Fat_Pct", "#00CCFF", "BODY FAT %", "BODY FAT"), use_container_width=True)
            else:
                st.info("No body fat data in selected period.")
        with tab3:
            waist_data = chart_df[chart_df["Waist_cm"] > 0]
            if not waist_data.empty:
                st.altair_chart(make_chart(waist_data, "Waist_cm", "#FFD700", "WAIST (cm)", "WAIST"), use_container_width=True)
            else:
                st.info("No waist data in selected period.")

    # ── Data management ───────────────────────────────────────────────────────
    section_header("DATA MANAGEMENT")

    if not df_raw.empty:
        df_raw["__temp_id__"] = df_raw.index
        df_raw["Display_ID"] = (
            df_raw["Date"].astype(str) + "  —  " +
            df_raw["Comments"].fillna("").astype(str).str[:35]
        )

    col_form, col_right = st.columns([2, 1])

    with col_form:
        with st.expander("ADD NEW DAILY LOG", expanded=False):
            with st.form("workout_form", clear_on_submit=True):

                f_date = st.date_input("Date", date.today())

                form_section_label("EXERCISE")
                ex1, ex2, ex3, ex4 = st.columns([2, 1, 1, 1])
                with ex1:
                    f_pull = st.number_input("Pullups", min_value=0, step=1, value=0)
                with ex2:
                    f_abs = st.checkbox("Abs")
                with ex3:
                    f_weights = st.checkbox("Weights")
                with ex4:
                    f_stretch = st.checkbox("Stretched")

                form_section_label("CARDIO")
                kbc1, kbc2, skipc1, skipc2 = st.columns([1, 2, 1, 2])
                with kbc1:
                    f_kickboxing = st.checkbox("Kickboxing")
                with kbc2:
                    f_kb_min = st.number_input("KB Min", min_value=0, step=5, value=0)
                with skipc1:
                    f_skipping = st.checkbox("Skipping")
                with skipc2:
                    f_skip_min = st.number_input("Skip Min", min_value=0, step=5, value=0)

                form_section_label("BODY METRICS")
                bm1, bm2, bm3 = st.columns(3)
                with bm1:
                    f_wgt = st.number_input("Weight (kg)", min_value=0.0, step=0.1, value=0.0, format="%.1f")
                with bm2:
                    f_fat = st.number_input("Fat %", min_value=0.0, step=0.1, value=0.0, format="%.1f")
                with bm3:
                    f_waist = st.number_input("Waist (cm)", min_value=0.0, step=0.5, value=0.0, format="%.1f")

                f_comm = st.text_area("Comments", placeholder="Optional notes...", height=72)

                if st.form_submit_button("SUBMIT LOG ENTRY"):
                    if f_kickboxing:
                        cardio_type, cardio_min = "Kickboxing", f_kb_min
                    elif f_skipping:
                        cardio_type, cardio_min = "Skip", f_skip_min
                    else:
                        cardio_type, cardio_min = "None", 0

                    clean_df = df_raw.drop(columns=["__temp_id__", "Display_ID"], errors="ignore")
                    new_row = pd.DataFrame([{
                        "Date": f_date.strftime("%Y-%m-%d"),
                        "Pullups": f_pull,
                        "Pushups": 0, "Squats": 0, "Burpees": 0,
                        "Abs": f_abs, "Weights": f_weights,
                        "Cardio Type": cardio_type, "Cardio Min/Reps": cardio_min,
                        "Stretched": f_stretch,
                        "Weight": f_wgt if f_wgt > 0 else None,
                        "Fat_Pct": f_fat if f_fat > 0 else None,
                        "Waist_cm": f_waist if f_waist > 0 else None,
                        "Comments": f_comm,
                    }])
                    conn.update(data=pd.concat([clean_df, new_row], ignore_index=True))
                    st.success("LOG ENTRY SUBMITTED")
                    st.rerun()

    with col_right:
        with st.expander("EDIT / DELETE", expanded=False):
            if not df_raw.empty:
                display_df = df_raw.sort_values("Date", ascending=False)
                selected = st.selectbox(
                    "Select entry:",
                    options=display_df["Display_ID"],
                    index=0,
                    key="select_entry_to_delete",
                )
                if selected:
                    row = display_df[display_df["Display_ID"] == selected].iloc[0]
                    st.markdown(
                        f"<div style='font-family:Consolas,monospace;font-size:0.82rem;"
                        f"font-weight:600;line-height:1.9;margin:0.6rem 0;color:#AAAAAA;'>"
                        f"<span style='color:#00CCFF;'>DATE&nbsp;&nbsp;&nbsp;</span>{row['Date']}<br>"
                        f"<span style='color:#00CCFF;'>WEIGHT&nbsp;</span>"
                        f"<span style='color:#FF9900;'>{row['Weight']} kg</span>"
                        f"&nbsp;&nbsp;<span style='color:#00CCFF;'>FAT</span>&nbsp;&nbsp;"
                        f"<span style='color:#FF9900;'>{row['Fat_Pct']}%</span><br>" # Keep this orange
                        f"<span style='color:#00CCFF;'>NOTE&nbsp;&nbsp;&nbsp;</span>" # Keep this blue
                        f"<span style='color:#5A6A80;'>{row['Comments']}</span></div>", # Changed from 3A4A60 to 5A6A80
                        unsafe_allow_html=True,
                    )
                    st.warning("Delete is irreversible.")
                    if st.button(f"DELETE — {row['Date']}", key="confirm_delete"):
                        updated = df_raw[df_raw["__temp_id__"] != row["__temp_id__"]].drop(
                            columns=["__temp_id__", "Display_ID"]
                        )
                        conn.update(data=updated)
                        st.success("Entry deleted.")
                        st.rerun()
            else:
                st.info("No entries available.")

    # ── History log ───────────────────────────────────────────────────────────
    entry_count = len(chart_df) if not chart_df.empty else 0
    section_header(f"HISTORY LOG — {entry_count} ENTRIES")

    with st.expander("VIEW LOG", expanded=False):
        if not chart_df.empty:
            display_cols = [c for c in [
                "Date_Only", "Pullups", "Abs", "Weights",
                "Cardio Type", "Cardio Min/Reps", "Stretched",
                "Weight", "Fat_Pct", "Waist_cm", "Comments",
            ] if c in chart_df.columns]
            st.dataframe(
                chart_df[display_cols].sort_values("Date_Only", ascending=False),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("No data for selected period.")
