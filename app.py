# app.py
import os

import numpy as np
import pandas as pd
import streamlit as st
from main import outputfiles, process, top36
from makegroup import split_even, split_random

# グローバル変数
uploaded_files = []

# init session state: history, groups
if "history" not in st.session_state:
    st.session_state["history"] = []
if "groups" not in st.session_state:
    st.session_state["groups"] = []

# make folder to save files
current_dir = os.getcwd()
folder_path = os.path.join(current_dir, "outputs")
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# set random seed randomly
random_seed = np.random.randint(1000)

st.title("Grouping App")

# upload entrylist
enterylist_uploaded = st.file_uploader("Upload entrylist", type="csv")
if enterylist_uploaded:
    entrylist = pd.read_csv(enterylist_uploaded)
    # st.write("### Entrylist")
    # st.write(entrylist.head())

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
    st.write("### Scores")
    for i, file in enumerate(uploaded_files):
        df = pd.read_csv(file)
        scores_list.append(df)

        # get file name for column name
        file_name = file.name
        file_name = file_name[:-4]  # drop .csv
        name_list.append(file_name)

    scores = pd.concat(scores_list, axis=1, ignore_index=True)
    scores = pd.concat([entrylist, scores], axis=1, ignore_index=True)
    scores.columns = name_list
    st.write(scores.head())


if uploaded_files:
    name_list = name_list[3:]  # drop "No", "name", "Represent" from name_list

    # processing
    scores_processed = process(scores, name_list)

    # get top36
    players_top4, players_top5to36, players_top5to36_sorted = top36(scores_processed)

    # display top4
    st.write("### Top 4")
    st.write(players_top4)

    # display top5to36
    st.write("### Top 5 to 36")
    st.write(players_top5to36)

    # output files
    outputfiles(folder_path, players_top4, players_top5to36, players_top5to36_sorted)


# グループ分けの実行
if st.button("Random 8 groups"):
    groups = split_random(players_top5to36, random_seed)
    # display groups
    for i, group in enumerate(groups):
        st.write(f"### Group {i+1}")
        st.write(group)

    # 履歴に追加
    history = st.session_state.get("history", [])
    history.append(groups)

    # save to session state
    st.session_state["groups"] = groups
    st.session_state["history"] = history

if st.button("Even 8 groups (two top half and bottom half each)"):
    groups = split_even(players_top5to36_sorted, random_seed)

    # show groups
    for i, group in enumerate(groups):
        st.write(f"### Group {i+1}")
        st.write(group)

    # 履歴に追加
    history = st.session_state.get("history", [])

    history.append(groups)

    st.session_state["groups"] = groups
    st.session_state["history"] = history

# output files
if st.button("Output files"):
    if not st.session_state["groups"]:
        st.error("Do grouping first.")
        st.stop()

    # load groups from session state
    groups = st.session_state["groups"]
    for i, group in enumerate(groups):
        group.to_csv(os.path.join(folder_path, f"equal_group_{i+1}.csv"), index=False)

if len(st.session_state["history"]) > 1:
    # display history
    st.write("Display history")
    history = st.session_state["history"]
    st.write(f"{len(history)} logs found")
    # st.write(len(history[0]))

    index = st.slider("Select history", 0, len(history) - 1, 0)
    st.session_state["index"] = index
    st.write(history[index])

    if st.button("output files"):
        groups = history[index]
        for i, group in enumerate(groups):
            group.to_csv(
                os.path.join(folder_path, f"group_{i+1}_history.csv"), index=False
            )
        st.success("Successfully output files.")
