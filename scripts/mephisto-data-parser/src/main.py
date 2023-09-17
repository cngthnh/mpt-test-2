import pathlib
from backend.task_user_data import *
from backend.database_handle import *
from backend.csv_handle import *
import os
import sys
if __name__ == "__main__":
    args = sys.argv[1:]
    # validate args
    if len(args) != 3:
        print("Please provide 3 arguments: folder_link, database_folder_path, csv_folder_path")
        exit(1)

    # Folder link for tracking
    user_input_path = args[0]

    # Path to database
    database_folder_path = args[1]

    # Path to export CSV
    csv_folder_path = args[2]

    folder_link = pathlib.PurePath(user_input_path)
    csv_folder = pathlib.Path(csv_folder_path)

    # Create a user data frame (5 columns: user_id, task_id, user_dir, agent_data_dir, user_status, user_status in database)

    user_dataframe = CreateUserDataFrame(folder_link, database_folder_path)

    total_assigment = CountTotalAssignments(user_dataframe)

    total_user = CountTotalUser(user_dataframe)

    user_have_outputs = CountUserHaveOutputs(user_dataframe)

    user_do_not_have_outputs = CountUserDoNotHaveOutputs(user_dataframe)

    # Create a dataframe for csv file include task_id, agent_id, agent_data_dir, agent_meta_dir
    csv_dataframe, remaining_columns = CreateCSVDataFrame(user_dataframe)

    print(f"Total assignment: {total_assigment}")

    if total_user != 0:
        PrintTaskInformation(user_dataframe)

        print(f"Total user: {total_user}")

        print(f"User that is snapped {GetSnappedUser(list(user_dataframe['user_id']))}")

        print(
            f"Number of user did the assignment: {user_have_outputs} - Account for: {round(user_have_outputs/total_user*100,2)}%"
        )
        print(
            f"Number of user did not do the assignment: {user_do_not_have_outputs} - Account for: {round(user_do_not_have_outputs/total_user*100,2)}%"
        )
        CompareFolderWithDatabase(user_dataframe)
    else:
        print("No user detected")

    PrintCSVFile(csv_dataframe, remaining_columns, csv_folder)

    print("CSV File Created !!!!")
