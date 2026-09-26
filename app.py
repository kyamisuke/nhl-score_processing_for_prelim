# app.py

import pandas as pd
import streamlit as st

from main import process, getJusteDebuoutSelection

# グローバル変数
uploaded_files = []

# init session state: num_entry
if "num_entry" not in st.session_state:
    st.session_state["num_entry"] = 200

# 新しいentrylistがアップロードされたら、その行数をTotal entry numberに反映
entrylist_file = st.session_state.get("entrylist_file")
if entrylist_file is not None and (
    st.session_state.get("entrylist_file_id") != entrylist_file.file_id
):
    st.session_state["entrylist_file_id"] = entrylist_file.file_id
    st.session_state["num_entry"] = len(pd.read_csv(entrylist_file, header=None))
    entrylist_file.seek(0)

st.title("Processing 1st prelim")

# input total entry number to session state
st.write("### Input total entry number")
st.number_input("Total entry number", min_value=0, key="num_entry")
st.caption(
    "Automatically updated to the number of rows when an entrylist is uploaded."
)

st.write("## Upload files to start ")

# upload entrylist
enterylist_uploaded = st.file_uploader(
    "Upload entrylist", type="csv", key="entrylist_file"
)
if enterylist_uploaded:
    entrylist = pd.read_csv(
        enterylist_uploaded, header=None, nrows=st.session_state["num_entry"]
    )
    # set column names
    col_names = ["audition_number", "name", "represent"]
    entrylist.columns = col_names

    # dtype of audition_number -> int
    # entrylist["audition_number"] = entrylist["audition_number"].astype(int)

# upload score sheets
uploaded_file = st.file_uploader(
    "Upload score sheets from judges", type="csv", accept_multiple_files=True
)
if uploaded_file:
    if enterylist_uploaded is None:
        st.error("Upload entrylist first. Restart the app.")
        st.stop()
    uploaded_files = uploaded_file

    scores_list = []
    name_list = entrylist.columns.tolist()
    st.write("### Raw scores")
    for i, file in enumerate(uploaded_files):
        df = pd.read_csv(
            file, header=None, index_col=0, nrows=st.session_state["num_entry"]
        )
        scores_list.append(df)

        # get file name for column name
        file_name = file.name
        file_name = file_name[:-4]  # drop .csv
        name_list.append(file_name)

    scores = pd.concat(scores_list, axis=1, ignore_index=True)
    scores.index = range(len(scores))  # give index from 0 to n

    scores = pd.concat([entrylist, scores], axis=1, ignore_index=True)
    scores.columns = name_list
    st.dataframe(scores)


if uploaded_files:
    name_list = name_list[len(entrylist.columns):]  # judges name

    # processing
    scores_processed = process(scores, name_list)

    # display complete ranking
    getJusteDebuoutSelection(scores_processed)
