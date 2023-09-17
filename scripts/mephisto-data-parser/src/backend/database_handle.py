import sqlite3
import pathlib

from sqlite3.dbapi2 import Cursor
from pandas import DataFrame
import numpy as np


def ConnectDatabse(data_base_path: str):
    database_path = pathlib.Path(data_base_path)

    con = sqlite3.connect(database_path)

    cur = con.cursor()

    return cur


def GetStatusOfAgentId(cursor: Cursor, agent_id):
    database_result = cursor.execute(
        f"SELECT status FROM agents WHERE agent_id={agent_id}"
    )

    result = database_result.fetchone()
    # Check if agent_id exists in database
    if result == None:
        return None

    return result[0]


def CompareFolderWithDatabase(user_dataframe: DataFrame):
    user_dataframe["compare_database_true"] = np.where(
        (user_dataframe["user_status"] == True)
        & (user_dataframe["data_base_status"] != "completed"),
        "Diff",
        np.NaN,
    )

    user_dataframe["compare_database_false"] = np.where(
        (user_dataframe["user_status"] == False)
        & (user_dataframe["data_base_status"] == "completed"),
        "Diff",
        np.NaN,
    )

    # Users that have outputs should have database status == complete
    # Create dictionary using zip with key equal to agent_id and value is status from database

    true_user_dict = dict(
        zip(
            user_dataframe.loc[user_dataframe["compare_database_true"] == "Diff"][
                "user_id"
            ].tolist(),
            user_dataframe.loc[user_dataframe["compare_database_true"] == "Diff"][
                "data_base_status"
            ].tolist(),
        )
    )

    # Users that have no output should have database status != complete
    # Create dictionary using zip with key equal to agent_id and value is status from database

    false_user_dict = dict(
        zip(
            user_dataframe.loc[user_dataframe["compare_database_false"] == "Diff"][
                "user_id"
            ].tolist(),
            user_dataframe.loc[user_dataframe["compare_database_false"] == "Diff"][
                "data_base_status"
            ].tolist(),
        )
    )

    print(
        f"Agents with mismatchd complete information: {true_user_dict} - Total: {len(true_user_dict)}"
    )

    print(f"Agents with mismatched incomplete information: {false_user_dict}")

    return user_dataframe
