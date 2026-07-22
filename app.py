import streamlit as st
from streamlit_gsheets import GSheetsConnection
from gspread.exceptions import WorksheetNotFound
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go

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
.stInfo     > div { background-color: #080C16 !important; border-left: 3px solid #00CCFF !important; }
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
                    Gxpr
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
WORKOUTS_WORKSHEET = "Workouts"
WORKOUTS_COLUMNS = ["id", "date", "exercise_name", "set_number", "weight_or_bands", "reps", "rpe_or_notes"]


def load_workouts_df(gs_conn):
    try:
        w_df = gs_conn.read(worksheet=WORKOUTS_WORKSHEET, ttl=30)
        w_df = w_df.dropna(how="all")
    except WorksheetNotFound:
        w_df = pd.DataFrame(columns=WORKOUTS_COLUMNS)
        gs_conn.create(worksheet=WORKOUTS_WORKSHEET, data=pd.DataFrame([{c: "" for c in WORKOUTS_COLUMNS}]))
        gs_conn.update(worksheet=WORKOUTS_WORKSHEET, data=w_df)
    except Exception as e:
        st.error(f"WORKOUTS SHEET LOAD ERROR: {e}")
        return pd.DataFrame(columns=WORKOUTS_COLUMNS)

    for col in WORKOUTS_COLUMNS:
        if col not in w_df.columns:
            w_df[col] = None

    w_df["id"] = pd.to_numeric(w_df["id"], errors="coerce")
    w_df["set_number"] = pd.to_numeric(w_df["set_number"], errors="coerce").fillna(0).astype(int)
    w_df["reps"] = pd.to_numeric(w_df["reps"], errors="coerce").fillna(0).astype(int)
    w_df["date"] = w_df["date"].astype(str)
    w_df["exercise_name"] = w_df["exercise_name"].fillna("").astype(str)
    w_df["weight_or_bands"] = w_df["weight_or_bands"].fillna("").astype(str)
    w_df["rpe_or_notes"] = w_df["rpe_or_notes"].fillna("").astype(str)
    return w_df[WORKOUTS_COLUMNS]


if check_password():
    # Header bar
    st.markdown("""
        <div style='background:#0E1220;border-bottom:1px solid #FF9900;
                    padding:0.6rem 1rem 0.65rem 1rem;margin-bottom:0.5rem;
                    display:flex;justify-content:space-between;align-items:baseline;'>
            <span style='color:#FF9900;font-family:Consolas,monospace;
                         font-size:1.45rem;font-weight:700;letter-spacing:0.06em;'>
                Gxpr
            </span>
            <span style='color:#5A6A80;font-family:Consolas,monospace;
                         font-size:0.65rem;font-weight:700;letter-spacing:0.2em;'>
                PERSONAL ANALYTICS
            </span>
        </div>
    """, unsafe_allow_html=True)

    # ── Data load ─────────────────────────────────────────────────────────────
    gs_conn = st.connection("gsheets", type=GSheetsConnection)
    workouts_df = load_workouts_df(gs_conn)
    try:
        df_raw = gs_conn.read(ttl=30)
        for col in ["Cardio Type", "Comments", "Weight Band"]:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].fillna("N/A").astype(str)
        df_raw.columns = df_raw.columns.str.strip()
        if "Stretched" in df_raw.columns:
            df_raw = df_raw.rename(columns={"Stretched": "Stretch"})
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

        for col in ["Abs", "Weights", "Stretch"]:
            if col not in df.columns:
                df[col] = False
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
            index=2,
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

        # Calculate Pull-up total from the Workouts sheet to supplement GSheets daily-metrics history
        start_iso = chart_df["Date_Only"].min().strftime("%Y-%m-%d") if not chart_df.empty else "1900-01-01"
        end_iso = chart_df["Date_Only"].max().strftime("%Y-%m-%d") if not chart_df.empty else "9999-12-31"
        pu_mask = (
            (workouts_df["exercise_name"] == "Assisted Pull-Ups")
            & (workouts_df["date"] >= start_iso)
            & (workouts_df["date"] <= end_iso)
        )
        resistance_pullups = int(workouts_df.loc[pu_mask, "reps"].sum())

        unit_lbl = "<div style='color:#00CCFF; font-size:0.72rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; margin-top:0.8rem; margin-bottom:0.4rem;'>{}</div>"

        st.markdown(unit_lbl.format("SESSIONS"), unsafe_allow_html=True)
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("KICKBOX", len(chart_df[chart_df["Cardio Type"] == "Kickboxing"]))
        s2.metric("WEIGHTS", len(chart_df[chart_df["Weights"] == True]))
        s3.metric("ABS", len(chart_df[chart_df["Abs"] == True]))
        s4.metric("STRETCH", len(chart_df[chart_df["Stretch"] == True]))

        r_col, m_col = st.columns(2)
        with r_col:
            st.markdown(unit_lbl.format("REPS"), unsafe_allow_html=True)
            gs_pullups = int(chart_df["Pullups"].sum()) if "Pullups" in chart_df.columns else 0
            st.metric("PULL-UPS", gs_pullups + resistance_pullups)
        with m_col:
            st.markdown(unit_lbl.format("MINUTES"), unsafe_allow_html=True)
            st.metric("SKIP", int(chart_df[chart_df["Cardio Type"] == "Skip"]["Cardio Min/Reps"].sum()))

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
        v2, d2 = get_period_latest("Waist_cm")
        v3, d3 = get_period_latest("Fat_Pct")
        m1.metric("Weight", f"{v1} kg", help=f"As of {d1}")
        m2.metric("Waist", f"{v2} cm", help=f"As of {d2}")
        m3.metric("Fat %", f"{v3}%", help=f"As of {d3}")

        def make_chart(data, col, color, y_title, title,
                       target_low=None, target_high=None, target_unit="",
                       inflection_point=None, inflection_label="",
                       upper_limit=None, upper_limit_label="", y_ticks=None,
                       ultimate_low=None, ultimate_high=None, ultimate_unit="",
                       y_domain_min=None):
            data = data.sort_values("Date_Only")
            span_days = (data["Date_Only"].max() - data["Date_Only"].min()).days if len(data) > 1 else 0
            if span_days <= 14:
                x_dtick, x_format = 24 * 3600 * 1000, "%b %d"
            elif span_days <= 120:
                x_dtick, x_format = 7 * 24 * 3600 * 1000, "%b %d"
            else:
                x_dtick, x_format = "M1", "%b %Y"

            min_date = data["Date_Only"].min()

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=data["Date_Only"], y=data[col],
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(color=color, size=8),
                name=y_title,
                hovertemplate=f"<b>%{{x|%Y-%m-%d}}</b><br>{y_title}: %{{y}}<extra></extra>",
            ))

            shapes = []
            annotations = []
            all_vals = list(data[col].dropna().astype(float))

            def add_band(y1, y2, hue):
                shapes.append(dict(
                    type="rect", xref="paper", x0=0, x1=1, y0=y1, y1=y2,
                    fillcolor=hue, opacity=0.10, line=dict(width=0), layer="below",
                ))

            def add_rule(y, hue, dash, width, opacity=1.0):
                shapes.append(dict(
                    type="line", xref="paper", x0=0, x1=1, y0=y, y1=y,
                    line=dict(color=hue, width=width, dash=dash), opacity=opacity,
                ))

            def add_label(y, text, hue):
                annotations.append(dict(
                    x=min_date, y=y, xref="x", yref="y",
                    text=f"<b>{text}</b>", showarrow=False,
                    font=dict(color=hue, size=10, family="Consolas"),
                    xanchor="left", yanchor="bottom", yshift=5,
                ))

            if ultimate_low is not None and ultimate_high is not None:
                UC = "#00CCFF"  # ultimate light blue
                add_band(float(ultimate_low), float(ultimate_high), UC)
                add_rule(float(ultimate_low), UC, "dot", 1.5)
                add_label(float(ultimate_low), f"ULTIMATE  {ultimate_low}–{ultimate_high} {ultimate_unit}", UC)
                all_vals += [float(ultimate_low), float(ultimate_high)]

            if target_low is not None and target_high is not None:
                TC = "#2ECC71"  # target green
                add_band(float(target_low), float(target_high), TC)
                add_rule(float(target_low), TC, "dash", 1, opacity=0.55)
                add_rule(float(target_high), TC, "dash", 1, opacity=0.55)
                add_label(float(target_high), f"TARGET  {target_low}–{target_high} {target_unit}", TC)
                all_vals += [float(target_low), float(target_high)]

            if inflection_point is not None:
                IC = "#FF9900"  # Orange
                add_rule(float(inflection_point), IC, "dot", 1.5)
                add_label(float(inflection_point), inflection_label, IC)
                all_vals += [float(inflection_point)]

            if upper_limit is not None:
                ULC = "#8B0000"  # Dark Red
                add_rule(float(upper_limit), ULC, "dot", 1.5)
                add_label(float(upper_limit), upper_limit_label, ULC)
                all_vals += [float(upper_limit)]

            y_lo = y_domain_min if y_domain_min is not None else (min(all_vals) - (max(all_vals) - min(all_vals)) * 0.1 if all_vals else None)
            y_hi = max(all_vals) + (max(all_vals) - (y_lo or min(all_vals))) * 0.12 if all_vals else None
            yaxis_range = [y_lo, y_hi] if y_lo is not None and y_hi is not None else None

            ax_common = dict(
                gridcolor="#0E1220", linecolor="#3C4555", tickcolor="#3C4555",
                tickfont=dict(color="#5A6A80", size=11, family="Consolas"),
                title_font=dict(color="#00CCFF", size=11, family="Consolas"),
                showline=True, zeroline=False,
            )

            fig.update_layout(
                title=dict(text=title, font=dict(color="#00CCFF", size=11, family="Consolas"), x=0, xanchor="left"),
                height=520,
                paper_bgcolor="#0A0D14",
                plot_bgcolor="#0A0D14",
                font=dict(family="Consolas", color="#5A6A80"),
                showlegend=False,
                margin=dict(l=60, r=30, t=50, b=50),
                shapes=shapes,
                annotations=annotations,
                xaxis=dict(title="DATE", tickformat=x_format, dtick=x_dtick, tickangle=0, **ax_common),
                yaxis=dict(
                    title=y_title, range=yaxis_range,
                    tickvals=y_ticks if y_ticks else None,
                    **ax_common,
                ),
                hovermode="closest",
            )
            return fig

        tab1, tab2, tab3 = st.tabs(["WEIGHT", "WAIST", "BODY FAT %"])
        with tab1:
            w_data = chart_df[chart_df["Weight"] > 0]
            if not w_data.empty:
                st.plotly_chart(
                    make_chart(w_data, "Weight", "#FF9900", "WEIGHT (kg)", "WEIGHT",
                               target_low=67, target_high=69, target_unit="kg",
                               inflection_point=70.0, inflection_label="INFLECTION POINT 70 kg",
                               ultimate_low=65, ultimate_high=67, ultimate_unit="kg",
                               y_ticks=list(range(65, 91, 2)), y_domain_min=64),
                    width="stretch",
                )
            else:
                st.info("No weight data in selected period.")
        with tab2:
            waist_data = chart_df[chart_df["Waist_cm"] > 0]
            if not waist_data.empty:
                st.plotly_chart(
                    make_chart(waist_data, "Waist_cm", "#FFD700", "WAIST (cm)", "WAIST",
                               target_low=83, target_high=86, target_unit="cm"),
                    width="stretch",
                )
            else:
                st.info("No waist data in selected period.")
        with tab3:
            f_data = chart_df[chart_df["Fat_Pct"] > 0]
            if not f_data.empty:
                st.plotly_chart(
                    make_chart(f_data, "Fat_Pct", "#00CCFF", "BODY FAT %", "BODY FAT"),
                    width="stretch",
                )
            else:
                st.info("No body fat data in selected period.")

    # ── Resistance Training ───────────────────────────────────────────────────
    section_header("RESISTANCE TRAINING")

    w_tab1, w_tab2 = st.tabs(["LOG SESSION", "PROGRESSION HISTORY"])
    
    # ── FLEXIBLE PROGRESSION TARGET RULES ENGINE ──
    PROGRESSION_TARGETS = {
        "Assisted Pull-Ups": {"target": "3x10-12 (3 Bands)", "notes": "Build to 3x15, then drop a band."},
        "Dumbbell Rows":     {"target": "3x10-12 (7.5 kg)", "notes": "Relatively easy. Aim for 3x15, then up weight."},
        "Lateral Dumbbell Raises": {"target": "3x12 (7.5 kg)", "notes": "Close to failure. Control 3-sec eccentric phase."},
    }
    default_exercises = list(PROGRESSION_TARGETS.keys())

    # Helper function to extract last session's performance from the Workouts sheet
    def get_last_session_performance(exercise, set_num, before_date=None):
        mask = (
            (workouts_df["exercise_name"].str.lower() == exercise.lower())
            & (workouts_df["set_number"] == set_num)
        )
        if before_date:
            mask &= workouts_df["date"] < before_date
        matches = workouts_df[mask].sort_values(["date", "id"], ascending=[False, False])
        if not matches.empty:
            row = matches.iloc[0]
            notes = row["rpe_or_notes"] if row["rpe_or_notes"] and str(row["rpe_or_notes"]).lower() != "none" else "no notes"
            return f"Last: {row['weight_or_bands']} x{row['reps']} ({notes})", row["date"]
        return "No history", "—"

    # Fetch all unique exercises from the Workouts sheet for the dropdown
    db_ex_list = sorted(e for e in workouts_df["exercise_name"].unique().tolist() if e)

    all_options = sorted(list(set(default_exercises + db_ex_list)))

    with w_tab1:
        # --- UNIFIED DAILY INPUT BLOCK ---
        col_d, col_w, col_f, col_wa = st.columns([1.2, 1, 1, 1])
        with col_d:
            w_date = st.date_input("Session Date", date.today(), key="workout_date_input")
        with col_w:
            f_wgt = st.number_input("Weight (kg)", min_value=0.0, step=0.1, format="%.1f")
        with col_f:
            f_fat = st.number_input("Fat %", min_value=0.0, step=0.1, format="%.1f")
        with col_wa:
            f_waist = st.number_input("Waist (cm)", min_value=0.0, step=0.5, format="%.1f")

        form_section_label("ACTIVITY & CARDIO")
        c1, c2, c3, c4, c5, c6 = st.columns([1.5, 1, 1, 1, 1, 1.5])
        with c1:
            f_kickboxing = st.checkbox("KICKBOX")
            f_kb_min = st.number_input("KICKBOX Min", min_value=0, step=5, label_visibility="collapsed")
        with c2: f_weights = st.checkbox("Weights")
        with c3: f_abs = st.checkbox("Abs")
        with c4: f_stretch = st.checkbox("Stretch")
        with c5: f_pullups = st.checkbox("Pullups")
        with c6:
            f_skipping = st.checkbox("Skip")
            f_skip_min = st.number_input("Skip Min", min_value=0, step=5, label_visibility="collapsed")

        f_comm = st.text_input("Daily Comments", placeholder="How was the recovery/sleep?")

        # --- WORKOUT SECTION ---
        form_section_label("RESISTANCE LOG")
        col_sel, col_new = st.columns([1, 1])
        with col_sel:
            # Searchable dropdown for exercises already in the database
            selected_ex = st.selectbox(
                "Quick Add Existing",
                options=all_options,
                index=None,
                placeholder="Search database...",
                key="add_existing_ex_select"
            )
        with col_new:
            # Text input to add an entirely new exercise name
            new_ex_input = st.text_input("...or Add New Name", placeholder="e.g. Incline Bench", key="add_custom_ex_input")

        # Logic to determine which input to process for the log
        new_ex_name = selected_ex if selected_ex else new_ex_input

        # Initialize session log with benchmarks and targets
        if "current_workout_log" not in st.session_state:
            initial_log = []
            for ex in default_exercises:
                target_rule = PROGRESSION_TARGETS.get(ex, {"target": "N/A", "notes": ""})
                for s in range(1, 4):
                    perf, last_date = get_last_session_performance(ex, s, w_date.strftime("%Y-%m-%d"))
                    initial_log.append({
                        "Session Date": w_date.strftime("%Y-%m-%d"),
                        "Exercise": ex,
                        "Set": s,
                        "Weight/Bands": "7.5 kg" if "Dumbbell" in ex or "Lateral" in ex else "3 Bands",
                        "Reps": 0,
                        "Target Rule": target_rule["target"],
                        "Benchmark History": perf,
                        "Last Date": last_date,
                        "Notes": ""
                    })
            st.session_state.current_workout_log = initial_log

        if new_ex_name:
            existing_in_session = [r["Exercise"] for r in st.session_state.current_workout_log]
            if new_ex_name not in existing_in_session:
                for s in range(1, 4):
                    perf, last_date = get_last_session_performance(new_ex_name, s, w_date.strftime("%Y-%m-%d"))
                    st.session_state.current_workout_log.append({
                        "Session Date": w_date.strftime("%Y-%m-%d"),
                        "Exercise": new_ex_name, 
                        "Set": s, 
                        "Weight/Bands": "", 
                        "Reps": 0, 
                        "Target Rule": "Custom",
                        "Benchmark History": perf,
                        "Last Date": last_date,
                        "Notes": ""
                    })
                if new_ex_name not in all_options:
                    all_options.append(new_ex_name)
                    all_options.sort()
                st.rerun()
        
        # Sync Session Date and refresh benchmarks if the date picker changes
        if "current_workout_log" in st.session_state:
            # Track the date used to populate the log to detect changes
            if "last_synced_date" not in st.session_state:
                st.session_state.last_synced_date = w_date
            
            if st.session_state.last_synced_date != w_date:
                st.session_state.last_synced_date = w_date
                for row in st.session_state.current_workout_log:
                    row["Session Date"] = w_date.strftime("%Y-%m-%d")
                    # Refresh benchmarks based on the new date context (everything BEFORE the selected date)
                    perf, last_d = get_last_session_performance(row["Exercise"], row["Set"], w_date.strftime("%Y-%m-%d"))
                    row["Benchmark History"] = perf
                    row["Last Date"] = last_d

        # Interactive entry layout
        edited_log = st.data_editor(
            st.session_state.current_workout_log,
            num_rows="dynamic",
            column_config={
                "Session Date": st.column_config.TextColumn("Session Date", disabled=True),
                "Exercise": st.column_config.SelectboxColumn("Exercise", options=all_options, required=True, disabled=True),
                "Set": st.column_config.NumberColumn("Set", min_value=1, step=1, required=True, disabled=True),
                "Target Rule": st.column_config.TextColumn("Target Protocol", disabled=True),
                "Benchmark History": st.column_config.TextColumn("Last Session", disabled=True),
                "Last Date": st.column_config.TextColumn("Last Date", disabled=True),
                "Weight/Bands": st.column_config.TextColumn("Weight/Bands"),
                "Reps": st.column_config.NumberColumn("Reps", min_value=0, step=1),
                "Notes": st.column_config.TextColumn("RPE / Notes"),
            },
            width="stretch",
            key="workout_data_editor"
        )

        with st.expander("📝 LOGGING RUBRIC & KEYWORDS", expanded=False):
            st.markdown("""
            **Tip:** Ensure you press **Enter** or click out of the table after your last entry to ensure it's saved!
            **Core Keywords for System Audit:**
            *   **`easy`**: Triggers **Overload Authorization**. Use when you have significant Reps in Reserve (RIR).
            *   **`medium`**: System recommends maintaining current load and refining form.
            *   **`hard`**: Signals high intensity. Triggers **Tempo/Technical Focus** (3s eccentric/pauses).
            
            **RPE Reference (Tracking Only):**
            *   **RPE 10**: 0 Reps left. Absolute physical limit.
            *   **RPE 9**: 1 Rep left. Form stayed clean, but barely.
            *   **RPE 8**: 2 Reps left. *The Hypertrophy Sweet Spot.*
            
            **Progression Triggers:**
            *   **Pull-Ups**: 12+ reps → Remove 1 assistance band.
            *   **Rows/Raises**: 15+ reps → Increase weight to 10kg.
            """)

        if st.button("SAVE SESSION & SYNC TO CLOUD", width="stretch"):
            # 1. Logic for GSheets (Daily Metrics)
            if f_kickboxing:
                cardio_type, cardio_min = "Kickboxing", f_kb_min
            elif f_skipping:
                cardio_type, cardio_min = "Skip", f_skip_min
            else:
                cardio_type, cardio_min = "None", 0

            clean_df = df_raw.drop(columns=["__temp_id__", "Display_ID"], errors="ignore")
            new_gs_row = pd.DataFrame([{
                "Date": w_date.strftime("%Y-%m-%d"),
                "Pullups": 1 if f_pullups else 0, "Pushups": 0, "Squats": 0, "Burpees": 0,
                "Abs": f_abs, "Weights": f_weights,
                "Cardio Type": cardio_type, "Cardio Min/Reps": cardio_min,
                "Stretch": f_stretch,
                "Weight": f_wgt if f_wgt > 0 else None,
                "Fat_Pct": f_fat if f_fat > 0 else None,
                "Waist_cm": f_waist if f_waist > 0 else None,
                "Comments": f_comm,
            }])
            gs_conn.update(data=pd.concat([clean_df, new_gs_row], ignore_index=True))
            
            # 2. Logic for GSheets (Resistance Training)
            valid_entries = [row for row in edited_log if row.get("Reps", 0) > 0]
            if valid_entries:
                next_id = int(workouts_df["id"].max()) + 1 if workouts_df["id"].notna().any() else 1
                new_rows = []
                for row in valid_entries:
                    new_rows.append({
                        "id": next_id,
                        "date": w_date.strftime("%Y-%m-%d"),
                        "exercise_name": row["Exercise"],
                        "set_number": row["Set"],
                        "weight_or_bands": row["Weight/Bands"],
                        "reps": row["Reps"],
                        "rpe_or_notes": row["Notes"],
                    })
                    next_id += 1
                updated_workouts_df = pd.concat([workouts_df, pd.DataFrame(new_rows)], ignore_index=True)
                gs_conn.update(worksheet=WORKOUTS_WORKSHEET, data=updated_workouts_df[WORKOUTS_COLUMNS])
                st.toast(f"✅ Saved {len(valid_entries)} resistance sets.", icon="💪")

            st.success(f"Daily metrics synced to GSheets for {w_date}")
            if "current_workout_log" in st.session_state:
                del st.session_state.current_workout_log
            st.cache_data.clear()
            st.rerun()

    with w_tab2:
        h_df = workouts_df.sort_values(
            ["date", "exercise_name", "set_number"], ascending=[False, True, True]
        ).reset_index(drop=True)

        if not h_df.empty:
            sel_ex = st.selectbox("View Exercise Progress", ["All"] + sorted(db_ex_list))
            view_df = h_df if sel_ex == "All" else h_df[h_df["exercise_name"] == sel_ex]

            edited_h_df = st.data_editor(
                view_df,
                width="stretch",
                hide_index=True,
                num_rows="dynamic",
                column_config={
                    "id": None,  # Keep the internal ID hidden from the UI
                    "exercise_name": st.column_config.SelectboxColumn("Exercise", options=all_options),
                },
                key="history_editor"
            )

            if st.button("SAVE CHANGES TO HISTORY", width="stretch"):
                orig_ids = set(view_df["id"].dropna().tolist())
                curr_ids = set(edited_h_df["id"].dropna().tolist())
                del_ids = orig_ids - curr_ids

                full_df = workouts_df[~workouts_df["id"].isin(del_ids)].copy()

                next_id = int(full_df["id"].max()) + 1 if full_df["id"].notna().any() else 1
                for _, row in edited_h_df.iterrows():
                    if pd.notna(row.get("id")):
                        edit_cols = ["date", "exercise_name", "set_number", "weight_or_bands", "reps", "rpe_or_notes"]
                        full_df.loc[full_df["id"] == row["id"], edit_cols] = [row[c] for c in edit_cols]
                    elif row["exercise_name"] and row["reps"] > 0:
                        # Support adding entries directly into the history log
                        new_row = {c: row[c] for c in ["date", "exercise_name", "set_number", "weight_or_bands", "reps", "rpe_or_notes"]}
                        new_row["id"] = next_id
                        full_df = pd.concat([full_df, pd.DataFrame([new_row])], ignore_index=True)
                        next_id += 1

                gs_conn.update(worksheet=WORKOUTS_WORKSHEET, data=full_df[WORKOUTS_COLUMNS])
                st.success("Progression history updated.")
                st.cache_data.clear()
                st.rerun()
            
            if sel_ex != "All":
                chart_data = view_df.groupby("date")["reps"].sum().reset_index()
                chart_data["date"] = pd.to_datetime(chart_data["date"])
                chart_data = chart_data.sort_values("date")
                
                ax_cfg = dict(
                    gridcolor="#0E1220", linecolor="#3C4555", tickcolor="#3C4555",
                    tickfont=dict(color="#5A6A80", size=10, family="Consolas"),
                    title_font=dict(color="#00CCFF", size=10, family="Consolas"),
                    showline=True, zeroline=False,
                )

                c = go.Figure()
                c.add_trace(go.Scatter(
                    x=chart_data["date"], y=chart_data["reps"],
                    mode="lines+markers",
                    line=dict(color="#FF9900", width=2),
                    marker=dict(color="#FF9900", size=7),
                    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Reps: %{y}<extra></extra>",
                ))
                c.update_layout(
                    height=200,
                    paper_bgcolor="#0A0D14", plot_bgcolor="#0A0D14",
                    font=dict(family="Consolas", color="#5A6A80"),
                    showlegend=False,
                    margin=dict(l=50, r=20, t=20, b=50),
                    xaxis=dict(title="DATE", tickformat="%b %d", tickangle=-30, **ax_cfg),
                    yaxis=dict(title="TOTAL REPS", **ax_cfg),
                )

                st.plotly_chart(c, width="stretch")

            # ── PERFORMANCE FEEDBACK LOOP ENGINE ──
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("RUN PERFORMANCE REVIEW REPORT", width="stretch"):
                st.markdown("""
                    <div style='background:#111625; padding:15px; border-left:3px solid #00CCFF; margin-bottom:15px;'>
                        <span style='color:#00CCFF; font-family:Consolas,monospace; font-size:0.9rem; font-weight:700; letter-spacing:0.1em;'>
                            SYSTEM AUDIT: METABOLIC & PERFORMANCE FEEDBACK LOOP
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Report Sub-section A: RPE Explainer Core
                st.markdown("""
                ### ## Understanding RPE (Rate of Perceived Exertion)
                **RPE** measures structural intensity based on your **Reps in Reserve (RIR)**. Use these precise values in your log to inform target recalibration:
                * **RPE 10 (Maximal Effort):** 0 Reps left. Absolute physical limit reached.
                * **RPE 9 (Heavy Effort):** 1 Rep left. Form could only sustain one more clean completion.
                * **RPE 8 (Significant Effort):** 2 Reps left. *The Hypertrophy Sweet Spot.* (Lateral raises baseline).
                * **RPE 7 (Moderate Effort):** 3 Reps left. Speed was fluid. Load is currently comfortable. (Dumbbell rows baseline).
                ---
                """, unsafe_allow_html=True)

                # Report Sub-section B: Body Comp Analysis
                if not chart_df.empty:
                    valid_w = chart_df[chart_df["Weight"] > 0].sort_values("Date", ascending=False)
                    valid_f = chart_df[chart_df["Fat_Pct"] > 0].sort_values("Date", ascending=False)
                    
                    current_w = valid_w.iloc[0]["Weight"] if not valid_w.empty else 73.1
                    current_f = valid_f.iloc[0]["Fat_Pct"] if not valid_f.empty else 22.6
                    
                    st.markdown(f"**Current Structural Mass:** {current_w} kg | **Body Fat Boundary:** {current_f}%")
                    
                    if current_w > 72.0:
                        st.info(f"💡 **Weight Target Delta:** You are +{round(current_w - 72.0, 2)} kg above your 72.0 kg inflection ceiling. Subcutaneous fat extraction is highly active. Keep Rest-Day calories strictly suppressed.")
                    else:
                        st.success("🎯 **Target Reached:** Inflection point cleared. System ready to pivot from deficit to lean muscular capitalization.")
                
                # Report Sub-section C: Progressive Overload Triggers
                st.markdown("---")
                st.markdown("**Strength Progression Trajectory:**")
                
                def latest_peak(exercise):
                    sub = workouts_df[workouts_df["exercise_name"] == exercise].sort_values(
                        ["date", "reps", "set_number"], ascending=[False, False, False]
                    )
                    if sub.empty:
                        return None
                    top = sub.iloc[0]
                    return (top["reps"], top["rpe_or_notes"], top["date"])

                pu_max = latest_peak("Assisted Pull-Ups")
                if pu_max:
                    pu_notes = str(pu_max[1]).lower()
                    st.markdown(f"• **Assisted Pull-Ups Peak Volume:** {pu_max[0]} reps logged on {pu_max[2]} (Notes: {pu_max[1]})")
                    if "easy" in pu_notes or pu_max[0] >= 12:
                        st.warning("⚠️ **Progression Target Triggered:** You are consistently hitting the upper threshold of the 12-rep protocol. **Action:** Unclip exactly 1 resistance band for your next session to force neural adaptation.")
                    elif "hard" in pu_notes:
                        st.markdown("  *Status:* High effort detected. Prioritize full range of motion and chin-over-bar clearance before reducing assistance.")
                    elif "medium" in pu_notes:
                        st.markdown("  *Status:* Intensity is optimal. Focus on accumulating volume toward the 12-rep threshold.")
                    else:
                        st.markdown("  *Status:* Maintain current 3-band configuration. Focus on pushing the third set from 10 reps to a clean 12 reps before dropping assistance.")

                row_max = latest_peak("Dumbbell Rows")
                if row_max:
                    notes_lower = str(row_max[1]).lower()
                    if "easy" in notes_lower or row_max[0] >= 15:
                        st.success(f"🔥 **Overload Authorization:** Dumbbell rows are printing below your structural limit (Last: {row_max[0]} reps). **Action:** Increase physical dumbbell weight to 10 kg.")
                    elif "hard" in notes_lower:
                        st.markdown("• **Dumbbell Rows:** Intensity is high. Focus on a 1-second static pause at the peak compression point to maximize lat engagement.")
                    else:
                        st.markdown("• **Dumbbell Rows:** Retain 7.5 kg load. Focus on a 1-second static pause at the peak compression point to protect the elbow joints.")

                lat_max = latest_peak("Lateral Dumbbell Raises")
                if lat_max:
                    lat_notes_lower = str(lat_max[1]).lower()
                    if "easy" in lat_notes_lower or lat_max[0] >= 15:
                        st.success(f"🔥 **Overload Authorization:** Lateral Raises are currently under-taxing your capacity (Last: {lat_max[0]} reps). **Action:** Transition to 10 kg or push for 15 reps if structural integrity remains high.")
                    elif "hard" in lat_notes_lower:
                        st.markdown(f"• **Lateral Dumbbell Raises:** Ceilings fully engaged at 7.5 kg (Last: {lat_max[2]}). **Do not increase raw weight.** Maintain load and prioritize a strict 3-second lowering phase (eccentric focus) to maximize shoulder capping without risking elbow inflammation.")
                    elif "medium" in lat_notes_lower:
                        st.markdown(f"• **Lateral Dumbbell Raises:** Loading is appropriate. Focus on minimizing trap involvement and maintaining strict vertical paths.")
                    else:
                        st.markdown(f"• **Lateral Dumbbell Raises:** Last logged on {lat_max[2]}. Maintain current load and focus on a strict 3-second eccentric phase to increase intensity.")
        else:
            st.info("No history found in the Workouts sheet.")

    # ── Data management ───────────────────────────────────────────────────────
    section_header("DATA MANAGEMENT")

    if not df_raw.empty:
        df_raw["__temp_id__"] = df_raw.index
        df_raw["Display_ID"] = (
            df_raw["Date"].astype(str) + "  —  " +
            df_raw["Comments"].fillna("").astype(str).str[:35]
        )

    col_edit, _ = st.columns([1.5, 2])

    with col_edit:
        with st.expander("EDIT / DELETE G-SHEETS ENTRIES", expanded=False):
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
                        f"<span style='color:#FF9900;'>{row['Fat_Pct']}%</span><br>"
                        f"<span style='color:#00CCFF;'>NOTE&nbsp;&nbsp;&nbsp;</span>"
                        f"<span style='color:#5A6A80;'>{row['Comments']}</span></div>",
                        unsafe_allow_html=True,
                    )
                    st.warning("Delete is irreversible.")
                    if st.button(f"DELETE — {row['Date']}", key="confirm_delete"):
                        updated = df_raw[df_raw["__temp_id__"] != row["__temp_id__"]].drop(
                            columns=["__temp_id__", "Display_ID"]
                        )
                        gs_conn.update(data=updated)
                        st.success("Entry deleted.")
                        st.cache_data.clear()
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
                "Cardio Type", "Cardio Min/Reps", "Stretch",
                "Weight", "Fat_Pct", "Waist_cm", "Comments",
            ] if c in chart_df.columns]
            st.dataframe(
                chart_df[display_cols].sort_values("Date_Only", ascending=False),
                hide_index=True,
                width="stretch",
            )
        else:
            st.info("No data for selected period.")