# app.py

import numpy as np
import pandas as pd
import streamlit as st

from main import process, getJusteDebuoutSelection

# ジャンル定義
GENRES = ["House", "Locking", "Popping", "Hiphop"]

# ジャンルごとの特別ジャッジのデフォルト値
DEFAULT_SPECIAL_JUDGES = {
    "House": "KWAME_House",
    "Locking": "MASATO_Lockin",
    "Popping": "HYA_Poppin",
    "Hiphop": "BOUBOO_Hiphop",
}

# init session state for each genre
for genre in GENRES:
    if f"{genre}_num_entry" not in st.session_state:
        st.session_state[f"{genre}_num_entry"] = 0
    if f"{genre}_entrylist" not in st.session_state:
        st.session_state[f"{genre}_entrylist"] = None
    if f"{genre}_scores" not in st.session_state:
        st.session_state[f"{genre}_scores"] = None
    if f"{genre}_processed" not in st.session_state:
        st.session_state[f"{genre}_processed"] = False
    if f"{genre}_special_judge" not in st.session_state:
        st.session_state[f"{genre}_special_judge"] = DEFAULT_SPECIAL_JUDGES.get(genre, "")

st.title("Juste Debout - 4 Genres Score Processing")

# タブを作成
tabs = st.tabs(GENRES)

for i, genre in enumerate(GENRES):
    with tabs[i]:
        st.header(f"{genre}")

        # 設定セクション
        st.write("### Settings")
        col1, col2 = st.columns(2)

        with col1:
            st.session_state[f"{genre}_num_entry"] = st.number_input(
                f"Total entry number",
                min_value=0,
                value=200,
                key=f"{genre}_entry_input"
            )

        with col2:
            st.session_state[f"{genre}_special_judge"] = st.text_input(
                "2x weight judge name",
                value=st.session_state[f"{genre}_special_judge"],
                key=f"{genre}_special_judge_input",
                help="Enter judge name to apply 2x score multiplier (leave empty for no multiplier)"
            )

        st.write("## Upload files to start")

        # エントリーリストアップロード
        entrylist_uploaded = st.file_uploader(
            f"Upload entrylist ({genre})",
            type="csv",
            key=f"{genre}_entrylist_upload"
        )

        entrylist = None
        if entrylist_uploaded:
            entrylist = pd.read_csv(
                entrylist_uploaded,
                header=None,
                nrows=st.session_state[f"{genre}_num_entry"]
            )
            col_names = ["audition_number", "name", "represent"]
            entrylist.columns = col_names
            st.session_state[f"{genre}_entrylist"] = entrylist

        # スコアシートアップロード
        uploaded_files = st.file_uploader(
            f"Upload score sheets from judges ({genre})",
            type="csv",
            accept_multiple_files=True,
            key=f"{genre}_scores_upload"
        )

        if uploaded_files:
            if entrylist is None and st.session_state[f"{genre}_entrylist"] is None:
                st.error("Upload entrylist first.")
            else:
                if entrylist is None:
                    entrylist = st.session_state[f"{genre}_entrylist"]

                scores_list = []
                name_list = entrylist.columns.tolist()

                st.write("### Raw scores")
                for file in uploaded_files:
                    df = pd.read_csv(
                        file,
                        header=None,
                        index_col=0,
                        nrows=st.session_state[f"{genre}_num_entry"]
                    )
                    scores_list.append(df)

                    file_name = file.name[:-4]  # drop .csv
                    name_list.append(file_name)

                scores = pd.concat(scores_list, axis=1, ignore_index=True)
                scores.index = range(len(scores))

                scores = pd.concat([entrylist, scores], axis=1, ignore_index=True)
                scores.columns = name_list
                st.dataframe(scores)

                # ジャッジ名リスト（最後の4列）
                judges_list = name_list[-len(uploaded_files):]

                # スコア処理（UIで設定した特別ジャッジを使用）
                special_judge = st.session_state[f"{genre}_special_judge"]
                if special_judge == "":
                    special_judge = None
                scores_processed = process(scores, judges_list, special_judge)

                # 結果表示
                getJusteDebuoutSelection(scores_processed)

                st.session_state[f"{genre}_scores"] = scores
                st.session_state[f"{genre}_processed"] = True

# サマリーセクション
st.write("---")
st.write("## Summary")

completed_genres = []
for genre in GENRES:
    if st.session_state[f"{genre}_processed"]:
        completed_genres.append(genre)

if completed_genres:
    st.success(f"Completed genres: {', '.join(completed_genres)}")
else:
    st.info("No genres processed yet. Upload files in each tab.")
