import pandas as pd
import pathlib
from pandas import DataFrame
import json


def CreateCSVDataFrame(user_dataframe: DataFrame):
    agent_data = {
        "assignment_id": [],
        "agent_id": [],
        "agent_data_dir": [],
        "agent_meta_dir": [],
        "assign_data_dir": [],
    }

    if all(item == "" for item in user_dataframe["user_id"]):
        cleaned_data = {"assign_data_dir": []}

        for asignment_dir in user_dataframe["assign_data_dir"]:
            cleaned_data["assign_data_dir"].append(asignment_dir)

        cleaned_dataframe = pd.DataFrame(data=cleaned_data)
        remained_columns = cleaned_dataframe.columns
        return cleaned_dataframe, remained_columns

    for i in range(user_dataframe.shape[0]):
        agent_data["assignment_id"].append(int(user_dataframe["assignment_id"][i]))
        if user_dataframe["user_id"][i] != "":
            agent_data["agent_id"].append(int(user_dataframe["user_id"][i]))
        else:
            agent_data["agent_id"].append(user_dataframe["user_id"][i])
        agent_data["agent_data_dir"].append(user_dataframe["agent_data_dir"][i])
        agent_data["agent_meta_dir"].append(user_dataframe["agent_meta_dir"][i])
        agent_data["assign_data_dir"].append(user_dataframe["assign_data_dir"][i])

    agent_data_dataframe = pd.DataFrame(data=agent_data)
    agent_data_dataframe.sort_values(
        ["assignment_id", "agent_id"], ascending=[True, True], inplace=True
    )

    cleaned_dataframe, remained_columns = HandleCSVDataFrame(agent_data_dataframe)

    return cleaned_dataframe, remained_columns


def HandleCSVDataFrame(csv_dataframe: DataFrame):
    """
    Takes in a Pandas DataFrame of CSV data and processes it to remove empty columns and rows with missing
    agent_id values. Returns a new DataFrame with the remaining columns and the list of remaining column
    names.

    Args:
        csv_dataframe (DataFrame): The input DataFrame containing CSV data.

    Returns:
        (DataFrame): A new DataFrame with the remaining columns and rows with missing agent_id values removed.
        (list): A list of the remaining column names.
    """
    remaining_columns = []
    outputs_df = pd.DataFrame.assign(csv_dataframe)
    list_of_row = []
    row_index = 0

    # Loop through each column of the DataFrame
    for column in csv_dataframe.columns:
        # Check if the column has any null or empty values
        is_column_empty = all(item == "" for item in csv_dataframe[column])
        if is_column_empty:
            # If the column is entirely empty, drop it
            outputs_df.drop(column, axis=1, inplace=True)
            continue

        remaining_columns.append(column)

    for agent_id in outputs_df["agent_id"]:
        if agent_id == "":
            list_of_row.append(row_index)
        row_index = row_index + 1

    return outputs_df, remaining_columns


def PrintCSVFile(csv_dataframe: DataFrame, dataframe_columns: list, folder_link):
    data_frame_for_csv = pd.DataFrame.assign(csv_dataframe)
    csv_names = []

    if "agent_data_dir" in dataframe_columns:
        data_frame_for_agent_data_csv = GetAgentsInput(data_frame_for_csv)
        data_frame_for_agent_data_csv = GetAgentsOutput(data_frame_for_agent_data_csv)
        csv_names.append("agent_data")
    if "agent_meta_dir" in dataframe_columns:
        data_frame_for_agent_meta_csv = GetAgentMetaData(data_frame_for_csv)
        csv_names.append("agent_meta")
    if "assign_data_dir" in dataframe_columns:
        data_frame_for_assign_data_csv = GetAssignData(data_frame_for_csv)
        csv_names.append("assign_data")
    for csv_name in csv_names:
        if csv_name == "agent_data":
            data_frame_for_csv = data_frame_for_agent_data_csv
        elif csv_name == "agent_meta":
            data_frame_for_csv = data_frame_for_agent_meta_csv
        elif csv_name == "assign_data":
            data_frame_for_csv = data_frame_for_assign_data_csv
        CreateCSVFile(data_frame_for_csv, folder_link, csv_name)

    return


def GetAgentsInput(csv_dataframe: DataFrame):
    agent_data_list = list(csv_dataframe["agent_data_dir"])
    agent_inputs_list = list()
    output_df = pd.DataFrame.assign(csv_dataframe)

    for file in agent_data_list:
        try:
            json_file = open(file)
        except:
            agent_inputs_list.append(None)
            continue
        data: dict = json.load(json_file)
        # Currently leave as string
        agent_inputs_list.append(str(data.get("inputs")))

    output_df["agent_inputs"] = agent_inputs_list

    return output_df


def GetAgentsOutput(csv_dataframe: DataFrame):
    """
    Extracts output data from a CSV file containing agent data directories and returns a DataFrame
    with the output data, joined with the original DataFrame.

    :param csv_dataframe: A pandas DataFrame containing a column named "agent_data_dir" with
    the file paths to the agent data directories.
    :type csv_dataframe: pandas.DataFrame

    :return: A pandas DataFrame with the output data joined with the original DataFrame.
    :rtype: pandas.DataFrame
    """
    agent_data_list = csv_dataframe["agent_data_dir"]

    outputs = []
    indices = []
    for index, file in agent_data_list.items():
        try:
            json_file = open(file)
        except:
            continue
        data: dict = json.load(json_file)
        outputs_dict: dict = data.get("outputs")
        if outputs_dict == None:
            continue
        else:
            unnested_dict = {}
            for key, value in outputs_dict.items():
                if isinstance(value, dict):
                    for k, v in value:
                        unnested_dict[f"{key}.{k}"] = v
                else:
                    unnested_dict[f"outputs.{key}"] = value
            outputs.append(unnested_dict)
            indices.append(index)

    if not outputs:
        return csv_dataframe
    output_df = pd.DataFrame.from_records(outputs, index=indices)
    csv_dataframe = csv_dataframe.join(output_df)

    return csv_dataframe


def GetAgentMetaData(csv_dataframe: DataFrame):
    agent_meta_list = list(csv_dataframe["agent_meta_dir"])
    outputs = []

    for file in agent_meta_list:
        try:
            json_file = open(file)
        except:
            continue
        data: dict = json.load(json_file)
        for k, v in data.items():
            if isinstance(v, list):
                data[k] = str(v)

        outputs.append(data)

    outputs_df = pd.DataFrame.from_records(outputs)

    return csv_dataframe.join(outputs_df)


def GetAssignData(csv_dataframe: DataFrame):
    assign_data_list = list(csv_dataframe["assign_data_dir"])
    outputs = []

    for file in assign_data_list:
        try:
            json_file = open(file)
        except:
            continue
        data: dict = json.load(json_file)
        for k, v in data.items():
            if isinstance(v, list):
                data[k] = str(v)

        outputs.append(data)

    outputs_df = pd.DataFrame.from_records(outputs)

    return csv_dataframe.join(outputs_df)


def CreateCSVFile(dataframe: DataFrame, folder_link, type):
    # Check if csv_dir exists if not create new folder
    if not pathlib.Path(folder_link).exists():
        pathlib.Path(folder_link).mkdir(parents=True, exist_ok=True)

    csv_dir = pathlib.PurePath(folder_link).joinpath(f"{type}.csv")
    dataframe.to_csv(csv_dir)
    return
