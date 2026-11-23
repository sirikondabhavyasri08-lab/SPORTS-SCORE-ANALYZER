import streamlit as st
import pandas as pd
from pathlib import Path
from storage import load_json, save_all, import_csv
from validation import validate_match, REQUIRED_FIELDS
from analytics import summary, match_result, search_matches, warnings
from export import export_csv, export_summary, create_charts

st.set_page_config(page_title="Sports Score Analyzer", page_icon="🏆", layout="wide")
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg,#071426 0%,#0c1d33 55%,#102b46 100%); color:#eef5ff;}
[data-testid="stSidebar"] {background:#09182b;}
.block-container {padding-top:2rem;}
div[data-testid="stMetric"] {background:#142b45;border:1px solid #244765;padding:18px;border-radius:14px;}
.stButton>button {border-radius:10px;font-weight:600;}
h1,h2,h3 {color:#f3f7ff;}
</style>
""", unsafe_allow_html=True)

if "matches" not in st.session_state:
    st.session_state.matches = load_json()
matches = st.session_state.matches

def persist():
    save_all(st.session_state.matches)

st.sidebar.title("🏆 Sports Analyzer")
st.sidebar.caption("Match data • Performance • Reports")
page = st.sidebar.radio("NAVIGATION", ["Dashboard","Add Match","All Matches","Search & Filter","Analytics","Import CSV","Export Reports","Warnings"])
st.sidebar.divider()
st.sidebar.caption(f"{len(matches)} records loaded")

st.title("Sports Score Analyzer")
st.caption("A local-first workspace for match records, team performance and clear reporting.")

if page == "Dashboard":
    s = summary(matches)
    c = st.columns(4)
    c[0].metric("Total matches", s["total_matches"])
    c[1].metric("Completed", s["completed"])
    c[2].metric("Scheduled", s["scheduled"])
    c[3].metric("Average score", s["average_score"])
    left, right = st.columns([1.5,1])
    with left:
        st.subheader("Recent matches")
        if matches:
            df = pd.DataFrame([{**m,"Winner":match_result(m)} for m in matches[-8:][::-1]])
            st.dataframe(df[["match_id","date","team_a","score_a","team_b","score_b","Winner","status"]], use_container_width=True, hide_index=True)
        else: st.info("No matches yet. Add a match or load the included sample dataset.")
    with right:
        st.subheader("Quick insights")
        st.metric("Draws", s["draws"])
        st.metric("Highest score", s["highest_score"])
        if s["ranking"]:
            st.write("**Current leader**")
            st.success(f"{s['ranking'][0][0]} · {s['ranking'][0][1]['wins']} wins")
        else: st.info("Team rankings appear after completed matches.")

elif page == "Add Match":
    st.subheader("Record a match")
    with st.form("add_match_form", clear_on_submit=True):
        a,b = st.columns(2)
        with a:
            match_id = st.text_input("Match ID", placeholder="M041")
            match_date = st.date_input("Match date")
            tournament = st.text_input("Tournament", "Friendly Series")
            sport = st.selectbox("Sport", ["Cricket","Football","Basketball","Tennis","Other"])
            team_a = st.text_input("Team A")
            score_a = st.number_input("Team A score", min_value=0, max_value=10000, step=1)
        with b:
            venue = st.text_input("Venue", "Main Stadium")
            status = st.selectbox("Status", ["Completed","Scheduled","Abandoned"])
            team_b = st.text_input("Team B")
            score_b = st.number_input("Team B score", min_value=0, max_value=10000, step=1)
        submitted = st.form_submit_button("Save match", type="primary", use_container_width=True)
    if submitted:
        raw = {"match_id":match_id,"date":match_date.isoformat(),"tournament":tournament,"sport":sport,
               "team_a":team_a,"team_b":team_b,"score_a":score_a,"score_b":score_b,"venue":venue,"status":status}
        item, errors = validate_match(raw, {m["match_id"] for m in matches})
        if errors:
            for error in errors: st.error(error)
        else:
            matches.append(item); persist(); st.success("Match saved successfully.")

elif page == "All Matches":
    st.subheader("Match records")
    if matches:
        df = pd.DataFrame([{**m,"winner":match_result(m)} for m in matches])
        st.dataframe(df, use_container_width=True, hide_index=True)
        ids = [m["match_id"] for m in matches]
        selected = st.selectbox("Select a match to delete", ["—"] + ids)
        if st.button("Delete selected match", disabled=selected=="—"):
            st.session_state.matches = [m for m in matches if m["match_id"] != selected]
            persist(); st.rerun()
    else: st.info("No records found.")

elif page == "Search & Filter":
    st.subheader("Find a match")
    q = st.text_input("Search team, tournament, venue or match ID")
    status_filter = st.selectbox("Match status", ["All","Completed","Scheduled","Abandoned"])
    found = search_matches(matches, q, status_filter)
    st.caption(f"{len(found)} result(s)")
    if found: st.dataframe(pd.DataFrame([{**m,"winner":match_result(m)} for m in found]), use_container_width=True, hide_index=True)
    else: st.info("No matching records.")

elif page == "Analytics":
    st.subheader("Performance analytics")
    s = summary(matches)
    c = st.columns(3)
    c[0].metric("Completed matches",s["completed"])
    c[1].metric("Average score",s["average_score"])
    c[2].metric("Draws",s["draws"])
    if s["ranking"]:
        rank_df = pd.DataFrame([{"Team":t,"Played":d["played"],"Wins":d["wins"],"Draws":d["draws"],"Runs":d["runs"],"Run difference":d["runs"]-d["against"]} for t,d in s["ranking"]])
        st.dataframe(rank_df, use_container_width=True, hide_index=True)
        st.bar_chart(rank_df.set_index("Team")[["Wins","Played"]])
    paths = create_charts(matches)
    for p in paths: st.image(str(p), caption=p.name, use_container_width=True)
    if not s["ranking"]: st.info("Complete some matches to see rankings and charts.")

elif page == "Import CSV":
    st.subheader("Bulk dataset import")
    st.write("Required columns: " + ", ".join(REQUIRED_FIELDS))
    upload = st.file_uploader("Choose a CSV file", type=["csv"])
    if upload is not None and st.button("Validate and import", type="primary"):
        temp = Path("data") / "_uploaded_import.csv"
        temp.parent.mkdir(exist_ok=True)
        temp.write_bytes(upload.getvalue())
        new, errors = import_csv(temp, matches)
        temp.unlink(missing_ok=True)
        st.session_state.matches.extend(new); persist()
        st.success(f"Imported {len(new)} valid record(s).")
        if errors:
            st.warning(f"{len(errors)} row(s) need attention.")
            for err in errors: st.write("• " + err)

elif page == "Export Reports":
    st.subheader("Reports and downloads")
    if st.button("Generate all reports and charts", type="primary"):
        p1 = export_csv(matches); p2,p3 = export_summary(matches); charts = create_charts(matches)
        st.success("Reports generated in the project reports/ and charts/ folders.")
        for p in [p1,p2,p3,*charts]:
            if p.exists():
                st.write(f"**{p.name}**")
                st.download_button(f"Download {p.name}", p.read_bytes(), file_name=p.name, key=str(p))
    st.caption("CSV report, Markdown summary, plain-text summary, and PNG charts.")

elif page == "Warnings":
    st.subheader("Data quality alerts")
    notes = warnings(matches)
    if notes:
        for note in notes: st.warning(note)
    else: st.success("No threshold warnings. Your current dataset passed the configured checks.")
    st.caption("Warnings flag past scheduled dates, unusually high scores and unusually large score margins.")
