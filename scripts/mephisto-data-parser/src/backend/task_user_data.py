import os
import json
import pathlib
import pandas as pd

from .database_handle import GetStatusOfAgentId, ConnectDatabse
from pandas import DataFrame


# Get list of all tasks
def CreateTaskDirList(folder_link: pathlib.PurePath):
    task_dir_list = []
    for subdir, dirs, files in os.walk(folder_link):
        current_dir = pathlib.PurePath(subdir)
        current_folder = pathlib.PurePath(current_dir).name
        try:
            int(current_folder)
        except ValueError:
            continue
        if current_dir != folder_link and current_dir.parent not in task_dir_list:
            task_dir_list.append(current_dir)

    return task_dir_list


# Function finding a list of user directory for each assignment
def CreateUserDirList(assignment_dir):
    user_dir_list = []

    for subdir, dirs, files in os.walk(assignment_dir):
        current_dir = pathlib.PurePath(subdir)
        if current_dir == assignment_dir:
            for dir in dirs:
                if dir.isdigit():
                    user_dir_list.append(current_dir.joinpath(dir))
        else:
            continue

    return user_dir_list


def CountUserHaveOutputs(user_df: DataFrame):
    try:
        results = user_df["user_status"].value_counts()[True]
    except:
        results = 0
        return results

    return results


def CountUserDoNotHaveOutputs(user_df: DataFrame):
    try:
        results = user_df["user_status"].value_counts()[False]
    except:
        results = 0
        return results

    return results


def GetOutputsResults(json_dir):
    try:
        file_dir = pathlib.PurePath(json_dir).joinpath("agent_data.json")
        json_file = open(file_dir)
    except:
        return False
    data: dict = json.load(json_file)
    if data.get("outputs") != None:
        return True
    else:
        return False


def GetTaskOrUserNumber(user_or_task_dir):
    return pathlib.PurePath(user_or_task_dir).name


# Function for getting snapped User Number
def GetSnappedUser(user_list: list):
    maximum_user_number = 0
    snapped_user_arr = []

    for user in user_list:
        if user == "":
            continue
        if user > maximum_user_number:
            maximum_user_number = user

    for i in range(1, maximum_user_number + 1):
        if i not in user_list:
            snapped_user_arr.append(i)

    return snapped_user_arr


def CreateTaskDir(task_number, folder_link):
    return pathlib.PurePath.joinpath(folder_link, str(task_number))


# Create a data frame for user
def CreateUserDataFrame(folder_link, database_path):
    task_dir_list = CreateTaskDirList(folder_link)

    user_data = {
        "user_id": [],
        "assignment_id": [],
        "user_dir": [],
        "agent_data_dir": [],
        "agent_meta_dir": [],
        "assign_data_dir": [],
        "user_status": [],
        "data_base_status": [],
    }

    for assignment_dir in task_dir_list:
        user_dir_list = CreateUserDirList(assignment_dir)
        if len(user_dir_list) == 0:
            print(
                f"No user detected for assignment {GetTaskOrUserNumber(assignment_dir)}"
            )
            assign_data_file = pathlib.PurePath(assignment_dir).joinpath(
                "assign_data.json"
            )
            user_data["assign_data_dir"].append(assign_data_file)
            user_data["user_id"].append("")
            user_data["assignment_id"].append(int(GetTaskOrUserNumber(assignment_dir)))
            user_data["user_dir"].append("")
            user_data["agent_data_dir"].append("")
            user_data["agent_meta_dir"].append("")
            user_data["user_status"].append("")
            user_data["data_base_status"].append("")
        else:
            for user_dir in user_dir_list:
                assign_data_file = pathlib.PurePath(assignment_dir).joinpath(
                    "assign_data.json"
                )
                user_data["assign_data_dir"].append(assign_data_file)
                user_data["user_id"].append(int(GetTaskOrUserNumber(user_dir)))
                user_data["assignment_id"].append(
                    int(GetTaskOrUserNumber(assignment_dir))
                )
                user_data["user_dir"].append(user_dir)
                agent_data_file = pathlib.PurePath(user_dir).joinpath("agent_data.json")
                agent_meta_file = pathlib.PurePath(user_dir).joinpath("agent_meta.json")
                if os.path.isfile(agent_data_file):
                    user_data["agent_data_dir"].append(agent_data_file)
                else:
                    user_data["agent_data_dir"].append("")

                if os.path.isfile(agent_meta_file):
                    user_data["agent_meta_dir"].append(agent_meta_file)
                else:
                    user_data["agent_meta_dir"].append("")

                user_data["user_status"].append(GetOutputsResults(user_dir))
                user_data["data_base_status"].append(
                    GetStatusOfAgentId(
                        ConnectDatabse(database_path), GetTaskOrUserNumber(user_dir)
                    )
                )

    user_dataframe = pd.DataFrame(data=user_data)

    sorted_user_dataframe = user_dataframe.sort_values("assignment_id", ignore_index=True)

    return sorted_user_dataframe


def CountNumberOfUser(user_data_frame: DataFrame, assignment_id: int):
    count_user = 0
    for user_id in user_data_frame[user_data_frame["assignment_id"] == assignment_id][
        "user_id"
    ]:
        if user_id != "":
            count_user = count_user + 1

    return count_user


def PrintTaskInformation(user_dataframe: DataFrame):
    for assignment_id in list(user_dataframe["assignment_id"].unique()):
        print(f"Task:{assignment_id}")
        number_of_user = CountNumberOfUser(user_dataframe, assignment_id)
        user_did_assignment = list(
            user_dataframe.loc[
                (user_dataframe["assignment_id"] == assignment_id)
                & (user_dataframe["user_status"] == True)
            ]["user_id"]
        )

        user_did_not_do_assignment = list(
            user_dataframe.loc[
                (user_dataframe["assignment_id"] == assignment_id)
                & (user_dataframe["user_status"] == False)
            ]["user_id"]
        )
        print(
            f"Total agents: {number_of_user} - Agent did the assignment:{user_did_assignment}  - Agent did not do the assignment: {user_did_not_do_assignment} "
        )
    return


def CountTotalAssignments(user_dataframe: DataFrame):
    if all(item == "" for item in user_dataframe["assignment_id"]):
        return 0

    total_assignment = len(user_dataframe["assignment_id"].unique())

    return total_assignment


def CountTotalUser(user_dataframe: DataFrame):
    count_user = 0

    if all(item == "" for item in user_dataframe["user_id"]):
        return 0
    
    for agent_id in user_dataframe["user_id"]:
        if agent_id != "":
            count_user = count_user + 1

    return count_user
