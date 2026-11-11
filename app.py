# app.py

import pandas as pd
import streamlit as st

from main import process, process_simple_sum, getJusteDebuoutSelection

FOREVER = "forever"
JUSTE_DEBOUT = "juste_debout"


def render(mode):
    """
    1つの計算機 (forever / juste debout) を描画する。
    タブごとに独立して動くよう、session_state のキーには mode を prefix として付ける
    """
    key_num_entry = f"{mode}_num_entry"
    key_entrylist_file = f"{mode}_entrylist_file"
    key_entrylist_file_id = f"{mode}_entrylist_file_id"

    # init session state: num_entry
    if key_num_entry not in st.session_state:
        st.session_state[key_num_entry] = 200

    # 新しいentrylistがアップロードされたら、その行数をTotal entry numberに反映
    entrylist_file = st.session_state.get(key_entrylist_file)
    if entrylist_file is not None and (
        st.session_state.get(key_entrylist_file_id) != entrylist_file.file_id
    ):
        st.session_state[key_entrylist_file_id] = entrylist_file.file_id
        st.session_state[key_num_entry] = len(
            pd.read_csv(entrylist_file, header=None)
        )
        entrylist_file.seek(0)

    # どちらの計算機か一目でわかるように表示
    if mode == JUSTE_DEBOUT:
        st.header("JUSTE DEBOUT")
        st.success(
            "**Simple sum** of raw scores. "
            "Same-genre judges' scores are **doubled**."
        )
    else:
        st.header("FOREVER")
        st.info("Sum of **z-score normalized** scores per judge.")

    # input total entry number to session state
    st.write("### Input total entry number")
    st.number_input("Total entry number", min_value=0, key=key_num_entry)
    st.caption(
        "Automatically updated to the number of rows when an entrylist is uploaded."
    )

    st.write("## Upload files to start ")

    # upload entrylist
    enterylist_uploaded = st.file_uploader(
        "Upload entrylist", type="csv", key=key_entrylist_file
    )
    if enterylist_uploaded:
        entrylist = pd.read_csv(
            enterylist_uploaded, header=None, nrows=st.session_state[key_num_entry]
        )
        # set column names
        col_names = ["audition_number", "name", "represent"]
        entrylist.columns = col_names

        # dtype of audition_number -> int
        # entrylist["audition_number"] = entrylist["audition_number"].astype(int)

    # upload score sheets
    uploaded_files = st.file_uploader(
        "Upload score sheets from judges",
        type="csv",
        accept_multiple_files=True,
        key=f"{mode}_score_files",
    )
    if not uploaded_files:
        return
    if enterylist_uploaded is None:
        st.error("Upload entrylist first. Restart the app.")
        return

    scores_list = []
    name_list = entrylist.columns.tolist()
    st.write("### Raw scores")
    for i, file in enumerate(uploaded_files):
        df = pd.read_csv(
            file, header=None, index_col=0, nrows=st.session_state[key_num_entry]
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

    name_list = name_list[len(entrylist.columns):]  # judges name

    # processing
    if mode == JUSTE_DEBOUT:
        double_judges = st.multiselect(
            "同一ジャンルのジャッジ (得点2倍)", name_list, key=f"{mode}_double_judges"
        )
        scores_processed = process_simple_sum(scores, name_list, double_judges)
    else:
        scores_processed = process(scores, name_list)

    # display complete ranking
    getJusteDebuoutSelection(scores_processed)


st.title("Processing 1st prelim")

tab_forever, tab_juste_debout = st.tabs(["FOREVER", "JUSTE DEBOUT"])
with tab_forever:
    render(FOREVER)
with tab_juste_debout:
    render(JUSTE_DEBOUT)
