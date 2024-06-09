import io
import os
import zipfile

import pandas as pd
import streamlit as st


def readcsv(folder_path, file_names):
    exp = ".csv"
    for i, file_name in enumerate(file_names):
        file_name += exp
        file_path = os.path.join(folder_path, file_name)
        data_one = pd.read_csv(file_path)

        if i == 0:
            scores = data_one
        else:
            scores = pd.concat((scores, data_one.iloc[:, 3]), axis=1)

    """
    scores.columns = scores.iloc[0]
    scores = scores.drop(0)"""

    return scores


def process(scores, judges):
    """
    (score - mean) / deviation
    """
    scores_processed = scores[
        ["audition_number", "entry_number", "name", "Represent"]
    ].copy()

    scores_mean = scores[judges].mean(axis=0)
    scores_std = scores[judges].std(axis=0)

    # st.write(judges)
    # st.write(scores_mean)
    # st.write(scores_std)

    for judge in judges:
        scores_processed.loc[:, judge] = (
            scores.loc[:, judge] - scores_mean.loc[judge]
        ) / scores_std.loc[judge]

    scores_processed["sum"] = scores_processed[judges].sum(axis=1)

    return scores_processed


def top36(scores_processed):
    scores_des = scores_processed.sort_values(by="sum", ascending=False)

    st.write("### Results of 1st prelim")
    st.write(scores_des)

    # players_top36 = scores_des[['No', 'name', 'Represent']].iloc[:36]
    players_top36 = scores_des.iloc[:36]
    st.write("### Top 36")
    st.write(players_top36)

    players_top4 = (
        scores_des[["entry_number", "name", "Represent"]]
        .iloc[:4]
        .sort_values(by="entry_number", ascending=True)
    )

    players_top5to36 = (
        scores_des[["entry_number", "name", "Represent"]].iloc[4:36]
        # .sort_values(by="No", ascending=True)
    )
    players_top5to36_sorted = players_top5to36.copy().sort_values(
        by="entry_number", ascending=True
    )

    # print(players_top36)

    return players_top4, players_top5to36, players_top5to36_sorted


def outputfiles_local(
    folder_path, players_top4, players_top5to36, players_top5to36_sorted
):
    players_top4[["entry_number", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top4.csv"), index=False
    )
    players_top5to36[["entry_number", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top5to36.csv"), index=False
    )
    players_top5to36_sorted[["entry_number", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top5to36_sorted.csv"), index=False
    )


def outputfiles(players_top4, players_top5to36, players_top5to36_sorted):
    # dataframes to csv
    top4_csv = players_top4[["entry_number", "name", "Represent"]].to_csv(index=False)
    # top5to36_csv = players_top5to36[["No", "name", "Represent"]].to_csv(index=False)
    top5to36_sorted_csv = players_top5to36_sorted[
        ["entry_number", "name", "Represent"]
    ].to_csv(index=False)

    # make ZipFile
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("top4.csv", top4_csv)
            # z.writestr("top5to36.csv", top5to36_csv)
            z.writestr("top5to36_sorted.csv", top5to36_sorted_csv)

        buffer.seek(0)

        # st.write("### file name list")
        # st.write(z.namelist())

        # download button
        st.download_button(
            label="Download top4.csv, top5to36.csv",
            data=buffer.getvalue(),  # buffer.getvalue()でzipファイルのバイナリデータを取得
            file_name="top36.zip",
            mime="application/zip",
        )


def get_zip(groups):
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            for i, group in enumerate(groups):
                # group_csv = group.to_csv(index=False)
                group_csv = group.to_csv(index=False)
                z.writestr(f"group_{i+1}.csv", group_csv)

        buffer.seek(0)

        # download button
        st.download_button(
            label="Download groups csv files",
            data=buffer.getvalue(),
            file_name="groups.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    folder_path = "/Users/te_keiero/PycharmProjects/NHL-score-prelim"

    # file_names = ['entry_list', 'judge-1.csv', 'judge-2.csv', 'judge-3.csv', 'judge-4.csv']
    # file_names = ['judge-1.csv', 'judge-2.csv', 'judge-3.csv', 'judge-4.csv']
    judge_names = ["Judge1", "Judge2", "Judge3", "Judge4"]

    scores = readcsv(folder_path, judge_names)

    scores_processed = process(scores, judge_names)

    players_top4, players_top5to36, players_top5to36_sorted = top36(scores_processed)

    outputfiles_local(
        folder_path, players_top4, players_top5to36, players_top5to36_sorted
    )
