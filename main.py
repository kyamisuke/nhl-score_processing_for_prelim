import os

import pandas as pd


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
    scores_processed = scores[["No", "name", "Represent"]].copy()

    scores_mean = scores[judges].mean(axis=0)
    scores_std = scores[judges].std(axis=0)

    # breakpoint()

    for judge in judges:
        scores_processed.loc[:, judge] = (
            scores.loc[:, judge] - scores_mean.loc[judge]
        ) / scores_std.loc[judge]

    scores_processed["sum"] = scores_processed[judges].sum(axis=1)

    return scores_processed


def top36(scores_processed):
    scores_des = scores_processed.sort_values(by="sum", ascending=False)

    # players_top36 = scores_des[['No', 'name', 'Represent']].iloc[:36]
    players_top36 = scores_des.iloc[:36]
    players_top4 = (
        scores_des[["No", "name", "Represent"]]
        .iloc[:4]
        .sort_values(by="No", ascending=True)
    )

    players_top5to36 = (
        scores_des[["No", "name", "Represent"]]
        .iloc[4:36]
        .sort_values(by="No", ascending=True)
    )
    players_top5to36_sorted = players_top5to36.copy().sort_values(
        by="No", ascending=True
    )

    print(players_top36)

    return players_top4, players_top5to36, players_top5to36_sorted


def outputfiles(folder_path, players_top4, players_top5to36, players_top5to36_sorted):
    players_top4[["No", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top4.csv"), index=False
    )
    players_top5to36[["No", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top5to36.csv"), index=False
    )
    players_top5to36_sorted[["No", "name", "Represent"]].to_csv(
        os.path.join(folder_path, "top5to36_sorted.csv"), index=False
    )


if __name__ == "__main__":
    folder_path = "/Users/te_keiero/PycharmProjects/NHL-score-prelim"

    # file_names = ['entry_list', 'judge-1.csv', 'judge-2.csv', 'judge-3.csv', 'judge-4.csv']
    # file_names = ['judge-1.csv', 'judge-2.csv', 'judge-3.csv', 'judge-4.csv']
    judge_names = ["Judge1", "Judge2", "Judge3", "Judge4"]

    scores = readcsv(folder_path, judge_names)

    scores_processed = process(scores, judge_names)

    players_top4, players_top5to36, players_top5to36_sorted = top36(scores_processed)

    outputfiles(folder_path, players_top4, players_top5to36, players_top5to36_sorted)
