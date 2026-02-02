import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import altair as alt

# 1. Page Configuration
st.set_page_config(page_title="Sparta Fitness Dashboard", layout="wide", page_icon="💪")

# --- PASSWORD PROTECTION SECTION ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        # Check if the password exists in secrets before comparing
        if "auth" in st.secrets and st.session_state["password"] == st.secrets["auth"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Remove password from state
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.info("Please enter the password to access the Sparta Dashboard.")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

# --- MAIN APP LOGIC ---
if check_password():
    # 1. Page Configuration
    st.set_page_config(page_title="Sparta Fitness", layout="wide", page_icon="💪")
    st.title("🏋️ Sparta Fitness Dashboard")

    # 2. Connection
    conn = st.connection("gsheets", type=GSheetsConnection)
    try:
        df_raw = conn.read(ttl=0)
        
        # Fix types immediately for Arrow stability
        for col in ["Cardio Type", "Comments", "Weight Band"]:
            if col in df_raw.columns:
                df_raw[col] = df_raw[col].fillna("N/A").astype(str)
                
        df_raw.columns = df_raw.columns.str.strip()
        df_raw = df_raw.dropna(how='all')
    except Exception as e:
        st.error(f"Error loading data: {e}")
        df_raw = pd.DataFrame()

    # 3. Data Processing
    if not df_raw.empty:
        df = df_raw.copy()
        df["Date"] = pd.to_datetime(df["Date"].astype(str).str.strip(), errors='coerce')
        df = df.dropna(subset=["Date"])
        df["Date_Only"] = df["Date"].dt.date
        
        # Numeric Conversion
        num_cols = ["Pullups", "Pushups", "Squats", "Burpees", "Cardio Min/Reps", "Weight", "Fat_Pct", "Waist_cm"]
        for col in num_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Boolean Fix
        bool_cols = ["Abs", "Weights", "Stretched"]
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower().isin(['true', '1', '1.0', 'yes', 'y', 'checked'])

        # --- RECENT COMMENT BANNER ---
        latest_entry = df.sort_values("Date", ascending=False).iloc[0]
        latest_date = latest_entry["Date_Only"].strftime("%B %d, %Y")
        latest_comment = latest_entry["Comments"]
        
        if latest_comment and latest_comment != "N/A":
            st.info(f"**Latest Entry ({latest_date}):** {latest_comment}")

    # 4. Lifetime Stats Dashboard
        if not df.empty:
            st.subheader("🏆 Lifetime Totals")
            s1, s2, s3, s4 = st.columns(4)
            
            def get_sum(col): return int(df[col].sum()) if col in df.columns else 0
            def get_count(col): return len(df[df[col] == True]) if col in df.columns else 0
            
            # New helper to count cardio sessions (ignoring "None")
            def get_cardio_sessions():
                if "Cardio Type" in df.columns:
                    return len(df[df["Cardio Type"] != "None"])
                return 0

            with s1:
                st.metric("Total Pullups", get_sum("Pullups"))
                st.metric("Abs Sessions", get_count("Abs"))
            with s2:
                st.metric("Total Squats", get_sum("Squats"))
                st.metric("Weight Sessions", get_count("Weights"))
            with s3:
                st.metric("Total Pushups", get_sum("Pushups"))
                st.metric("Stretch Sessions", get_count("Stretched"))
            with s4:
                st.metric("Total Burpees", get_sum("Burpees"))
                # Displaying both Number of Sessions and Total Units
                st.metric("Cardio Sessions", f"{get_cardio_sessions()}")
                st.write(f"⏱️ Total: {get_sum('Cardio Min/Reps')} minutes")
            st.markdown("---")

    # 5. FILTERING LOGIC
    st.subheader("📅 Insights & Filtering")
    if not df_raw.empty:
        t1, t2, t3 = st.columns([1, 1, 2])
        with t1:
            # UPDATED LABELS AS REQUESTED
            view_opt = st.radio("Time View", ["Full History", "Last Year", "Last Month", "Last Week"], horizontal=True)
        with t2:
            cardio_options = ["All"] + sorted([x for x in df["Cardio Type"].unique() if x not in ["N/A", "0", "0.0", "None"]])
            selected_type = st.selectbox("Drill into Cardio Type", cardio_options)
        with t3:
            abs_min_date = df["Date_Only"].min()
            abs_max_date = df["Date_Only"].max()
            sel_range = st.slider("Filter Date Range", abs_min_date, abs_max_date, (abs_min_date, abs_max_date))
        
        chart_df = df[(df["Date_Only"] >= sel_range[0]) & (df["Date_Only"] <= sel_range[1])]
        
        today = date.today()
        if view_opt == "Last Week": 
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=7))]
        elif view_opt == "Last Month": 
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=30))]
        elif view_opt == "Last Year": 
            chart_df = chart_df[chart_df["Date_Only"] >= (today - timedelta(days=365))]

        activity_df = chart_df.copy()
        if selected_type != "All":
            activity_df = activity_df[activity_df["Cardio Type"] == selected_type]

# ... (existing code above)

        st.markdown(f"#### Summary for Selected Period")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Pullups", int(chart_df["Pullups"].sum()))
        s2.metric("Squats", int(chart_df["Squats"].sum()))
        s3.metric("Pushups", int(chart_df["Pushups"].sum()))
        
        # --- UPDATED CARDIO SUMMARY SECTION ---
        cardio_val = int(activity_df['Cardio Min/Reps'].sum())
        # Count sessions in the filtered activity_df that aren't "None"
        cardio_sessions = len(activity_df[activity_df["Cardio Type"] != "None"])
        
        with s4:
            st.metric(f"{selected_type} Sessions", f"{cardio_sessions}")
            st.write(f"⏱️ Total: {cardio_val} Min")

    st.markdown("---")

# ... (rest of the existing code below)

    # 6. PROGRESS TRENDS
    if not chart_df.empty:
        st.subheader("📈 Body Progress Trends")
        tab1, tab2, tab3 = st.tabs(["Weight Trend", "Body Fat %", "Waist Size"])
        with tab1:
            w_data = chart_df[chart_df["Weight"] > 0]
            if not w_data.empty:
                w_chart = alt.Chart(w_data).mark_line(point=True, color="#ff4b4b").encode(
                    x='Date_Only:T', y=alt.Y('Weight:Q', scale=alt.Scale(zero=False))
                ).properties(height=400)
                st.altair_chart(w_chart, width='stretch')
        with tab2:
            f_data = chart_df[chart_df["Fat_Pct"] > 0]
            if not f_data.empty:
                f_chart = alt.Chart(f_data).mark_line(point=True, color="#00d4ff").encode(
                    x='Date_Only:T', y=alt.Y('Fat_Pct:Q', scale=alt.Scale(zero=False))
                ).properties(height=400)
                st.altair_chart(f_chart, width='stretch')
        with tab3:
            waist_data = chart_df[chart_df["Waist_cm"] > 0]
            if not waist_data.empty:
                waist_chart = alt.Chart(waist_data).mark_line(point=True, color="#00ff8d").encode(
                    x='Date_Only:T', y=alt.Y('Waist_cm:Q', scale=alt.Scale(zero=False))
                ).properties(height=400)
                st.altair_chart(waist_chart, width='stretch')

    st.markdown("---")

    # 7. LOG NEW ENTRY & DELETE ENTRY
    st.subheader("📝 Data Management")
    col_form, col_del = st.columns([3, 1])

    with col_form:
        with st.expander("➕ Add New Daily Log"):
            with st.form("workout_form", clear_on_submit=True):
                f_date = st.date_input("Date", date.today())
                c1, c2, c3 = st.columns(3)
                with c1:
                    f_pull = st.number_input("Pullups", 0)
                    f_push = st.number_input("Pushups", 0)
                    f_abs = st.checkbox("Abs")
                with c2:
                    f_squat = st.number_input("Squats", 0)
                    f_burp = st.number_input("Burpees", 0)
                    f_weights = st.checkbox("Weights")
                with c3:
                    f_ctype = st.selectbox("Cardio Type", ["None", "Kickboxing", "Run", "Skip", "Other"])
                    f_cmin = st.number_input("Cardio Min/Reps", 0)
                    f_stretch = st.checkbox("Stretched")
                
                st.write("---")
                c4, c5, c6 = st.columns(3)
                with c4: f_wgt = st.number_input("Weight (kg)", 0.0)
                with c5: f_fat = st.number_input("Fat %", 0.0)
                with c6: f_waist = st.number_input("Waist (cm)", 0.0)
                
                f_comm = st.text_area("Comments")
                
                if st.form_submit_button("Submit Entry"):
                    new_data = pd.DataFrame([{
                        "Date": f_date.strftime("%Y-%m-%d"), "Pullups": f_pull, "Pushups": f_push,
                        "Squats": f_squat, "Burpees": f_burp, "Abs": f_abs, "Weights": f_weights,
                        "Cardio Type": f_ctype, "Cardio Min/Reps": f_cmin, "Stretched": f_stretch,
                        "Weight": f_wgt, "Fat_Pct": f_fat, "Waist_cm": f_waist, "Comments": f_comm
                    }])
                    updated_df = pd.concat([df_raw, new_data], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success("Log added successfully!")
                    st.rerun()

    with col_del:
        with st.expander("🗑️ Danger Zone"):
            st.warning("This will remove the most recent entry.")
            if st.button("Delete Last Entry"):
                if not df_raw.empty:
                    updated_df = df_raw.iloc[:-1]
                    conn.update(data=updated_df)
                    st.success("Last entry deleted.")
                    st.rerun()

    st.markdown("---")
    st.subheader(f"📋 History Log ({selected_type}) - Showing {len(activity_df)} entries")
    st.dataframe(activity_df.sort_values("Date_Only", ascending=False), hide_index=True, width='stretch')