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


def process(scores, judges, special_judge=None):
    """
    Process scores with optional 2x multiplier for special judge.

    Args:
        scores: DataFrame with participant info and scores
        judges: List of judge column names
        special_judge: Judge name to apply 2x multiplier (optional)
    """
    scores_processed = scores[["audition_number", "name", "represent"]].copy()

    for judge in judges:
        if special_judge and judge == special_judge:
            # Apply 2x multiplier for special judge
            scores_processed.loc[:, judge] = scores.loc[:, judge] * 2
        else:
            scores_processed.loc[:, judge] = scores.loc[:, judge]

    scores_processed["sum"] = scores_processed[judges].sum(axis=1)

    return scores_processed

def top36(scores_processed):
    scores_des = scores_processed.sort_values(by="sum", ascending=False)

    col_names = ["audition_number", "name", "represent"]
    st.write("### Results of 1st prelim")
    st.write(scores_des)

    # players_top36 = scores_des[['No', 'name', 'Represent']].iloc[:36]
    # players_top36 = scores_des.iloc[:36]
    # st.write("### Top 36")
    # st.write(players_top36)

    players_top4 = (
        scores_des[col_names].iloc[:4].sort_values(by="audition_number", ascending=True)
    )

    players_top5to36 = (
        scores_des[col_names].iloc[4:36]
        # .sort_values(by="No", ascending=True)
    )
    players_top5to36_sorted = players_top5to36.copy().sort_values(
        by="audition_number", ascending=True
    )

    # download button for score_des.csv
    st.download_button(
        label="Download result on 1stprelim.csv",
        data=scores_des.to_csv(index=False, sep=","),
        file_name="result-1stprelim.csv",
        mime="text/csv",
    )

    return players_top4, players_top5to36, players_top5to36_sorted

def getJusteDebuoutSelection(scores_processed):
    scores_des = scores_processed.sort_values(by="sum", ascending=False).copy()

    # 順位を追加（同点は同じ順位）
    scores_des.insert(0, "rank", scores_des["sum"].rank(ascending=False, method="min").astype(int))

    st.write("### Results (sorted by score)")

    # 8位のスコアを取得
    eighth_place_score = scores_des.iloc[7]["sum"]

    # 8位以内（rank <= 8）の人数をカウント
    count_in_top8 = (scores_des["rank"] <= 8).sum()

    # 8人を超える場合のみTie状態（未確定）
    has_unconfirmed_tie = count_in_top8 > 8

    # ハイライト用のスタイル関数
    def highlight_rows(row):
        rank = row["rank"]
        score = row["sum"]

        if has_unconfirmed_tie and score == eighth_place_score:
            # 8位タイが9人以上 = 未確定
            return ["background-color: #fff59d"] * len(row)  # yellow
        elif rank <= 8:
            # 上位8名確定
            return ["background-color: #a5d6a7"] * len(row)  # green
        else:
            return [""] * len(row)

    styled_df = scores_des.style.apply(highlight_rows, axis=1)
    st.dataframe(styled_df, use_container_width=True)

    # 注釈（Tie状態がある場合のみ黄色の説明を表示）
    if has_unconfirmed_tie:
        st.markdown("""
**Legend:**
- 🟩 **Green**: Confirmed Top 8
- 🟨 **Yellow**: Tied at 8th place (not yet confirmed - more than 8 people in top 8 ranks)
""")
    else:
        st.markdown("""
**Legend:**
- 🟩 **Green**: Confirmed Top 8
""")

def outputfiles_local(
    folder_path, players_top4, players_top5to36, players_top5to36_sorted
):
    col_names = ["audition_number", "name", "represent"]
    players_top4[col_names].to_csv(
        os.path.join(folder_path, "top4.csv"), index=False, sep=", "
    )
    players_top5to36[col_names].to_csv(
        os.path.join(folder_path, "top5to36.csv"), index=False, sep=", "
    )
    players_top5to36_sorted[col_names].to_csv(
        os.path.join(folder_path, "top5to36_sorted.csv"), index=False, sep=","
    )


def outputfiles(players_top4, players_top5to36, players_top5to36_sorted):
    col_names = ["audition_number", "name", "represent"]
    # dataframes to csv
    top4_csv = players_top4[col_names].to_csv(index=False, sep=", ")
    # top5to36_csv = players_top5to36[["No", "name", "Represent"]].to_csv(index=False)
    top5to36_sorted_csv = players_top5to36_sorted[col_names].to_csv(
        index=False, sep=", "
    )

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
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            ""  # output in each group
            for i, group in enumerate(groups):
                group = group.drop(columns=1)  # drop " " column
                group_csv = group.to_csv(index=False, header=False, sep=" ")

                """
                with open(f"group_{i+1}.txt", "w") as f:
                    for i, row in enumerate(group):
                        if i > 1 and int(row[0]) < 100:
                            f.write(f"{row[0]}  {row[1]}\n")
                        else:
                            f.write(f"{row[0]} {row[1]}\n")

                # z.write(f"group_{i+1}.txt")
                # z.writestr(f"group_{i+1}.txt", open(f"group_{i+1}.txt").read())
                """

                z.writestr(f"group_{group_names[i]}.csv", group_csv)

            # output altogether
            with open("groups.txt", "w") as f_all:
                for i, group in enumerate(groups):
                    f_all.write(f"Group {group_names[i]}\n")

                    group = group.drop(columns=1).values.tolist()
                    # group_txt = group.to_string(index=False, header=False)
                    # format "audition_number name represent"
                    for i, row in enumerate(group):
                        if i > 1 and int(row[0]) < 100:
                            f_all.write(f"{row[0]}  {row[1]}\n")
                        else:
                            f_all.write(f"{row[0]} {row[1]}\n")

                    f_all.write("\n")
            # add to zip
            z.write("groups.txt")

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
