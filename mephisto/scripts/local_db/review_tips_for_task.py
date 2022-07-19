"""
Script that allows for tips to be approved or rejected.
Tips are collected by retrieving all units and then getting the agent of each unit.
The agent state has the tip data.

Approving a tip sets the accept property of the tip to be True.
This prevents it from appearing again when running this script.
It is stored in the agent state's metadata and in the assets/tips.csv file
in your task's directory.

Rejecting a tip deletes the tip from the tips list in the AgentState's metadata.
It also removed the row in the assets/tips.csv file in your task's directory.
"""

import csv
from genericpath import exists
from pathlib import Path
from typing import Any, List, Dict, Optional
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.agent import Agent
from mephisto.data_model.task_run import TaskRun
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser


def get_index_of_value(lst: List[str], property: str) -> int:
    for i in range(len(lst)):
        if lst[i] == property:
            return i
    return 0


def is_number(s) -> bool:
    """Validates the input to make sure that it is a number"""
    if s == "NaN":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def add_row_to_tips_file(task_run: TaskRun, item_to_add: Dict[str, Any]):
    """Adds a row the tips csv file"""
    blueprint_task_run_args = task_run.args["blueprint"]
    if "tips_location" in blueprint_task_run_args:
        tips_location = blueprint_task_run_args["tips_location"]
        does_file_exist = exists(tips_location)
        if does_file_exist == False:
            # Creates the file
            create_tips_file = Path(tips_location)
            create_tips_file.touch(exist_ok=True)
        with open(tips_location, "r") as inp, open(tips_location, "a+") as tips_file:
            field_names = list(item_to_add.keys())
            writer = csv.DictWriter(tips_file, fieldnames=field_names)
            reader = csv.reader(inp)
            # Add header if the file is newly created or empty
            if does_file_exist == False or len(list(reader)) == 0:
                writer.writeheader()
            writer.writerow(item_to_add)


def remove_tip_from_metadata(
    tips: List[Dict[str, Any]], tips_copy: List[Dict[str, Any]], i: int, unit: Unit
):
    """Removes a tip from metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    index_to_remove = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent: Optional[Agent] = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy.pop(index_to_remove)
        assigned_agent.state.update_metadata(
            property_name="tips", property_value=tips_copy
        )


def accept_tip(tips: List, tips_copy: List, i: int, unit: Unit) -> None:
    """Accepts a tip in metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    # gets the index of the tip in the tip_copy list
    index_to_update = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy[index_to_update]["accepted"] = True
        assigned_agent.state.update_metadata(
            property_name="tips", property_value=tips_copy
        )
        add_row_to_tips_file(unit.get_task_run(), tips_copy[index_to_update])


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    acceptable_responses = set(
        ["a", "accept", "ACCEPT", "Accept", "r", "reject", "REJECT", "Reject"]
    )
    accept_response = set(["a", "accept", "ACCEPT", "Accept"])
    reject_response = set(["r", "reject", "REJECT", "Reject"])
    yes_no_responses = set(["yes", "y", "YES", "Yes", "no", "n", "NO", "No"])
    yes_response = set(["yes", "y", "YES", "Yes"])
    no_response = set(["no", "n", "NO", "No"])

    print("\nTask Names:")
    for task_name in task_names:
        print(task_name)
    print("")
    task_name = input(
        "Enter the name of the task that you want to review the tips of: \n"
    )
    print("")
    while task_name not in task_names:
        print("That task name is not valid\n")
        task_name = input(
            "Enter the name of the task that you want to review the tips of: \n"
        )
        print("")
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("No units were received")
        quit()
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)
            tips = unit_data["tips"]

            if tips is not None and len(tips) > 0:
                tips_copy = tips.copy()
                for i in range(len(tips)):
                    if tips[i]["accepted"] == False:
                        print("Current Tip Id: " + tips[i]["id"] + "\n")
                        print("Current Tip Header: " + tips[i]["header"] + "\n")
                        print("Current Tip Text: " + tips[i]["text"] + "\n")
                        tip_response = input(
                            "Do you want to accept or reject this tip? accept(a)/reject(r): \n"
                        )
                        print("")
                        while tip_response not in acceptable_responses:
                            print("That response is not valid\n")
                            tip_response = input(
                                "Do you want to accept or reject this tip? accept(a)/reject(r): \n"
                            )
                            print("")
                        if tip_response in accept_response:
                            # persists the tip in the db as it is accepted
                            accept_tip(tips, tips_copy, i, unit)
                            print("Tip Accepted\n")
                            # given the option to pay a bonus to the worker who wrote the tip
                            is_bonus = input(
                                "Do you want to pay a bonus to this worker for their tip? yes(y)/no(n): "
                            )
                            while is_bonus not in yes_no_responses:
                                print("That response is not valid\n")
                                is_bonus = input(
                                    "Do you want to pay a bonus to this worker for their tip? yes(y)/no(n): \n"
                                )
                                print("")
                            if is_bonus in yes_response:
                                bonus_amount = input(
                                    "How much money do you want to give: "
                                )
                                while is_number(bonus_amount) is False:
                                    print("That is not a number\n")
                                    bonus_amount = input(
                                        "How much money do you want to give: "
                                    )
                                    print("")

                                reason = input("What is your reason for the bonus: ")
                                worker_id = float(unit_data["worker_id"])
                                worker = Worker.get(db, worker_id)
                                if worker is not None:
                                    bonus_successfully_paid = worker.bonus_worker(
                                        bonus_amount, reason, unit
                                    )
                                    if bonus_successfully_paid:
                                        print("Bonus Successfully Paid!\n")
                                    else:
                                        print(
                                            "There was an error when paying out your bonus\n"
                                        )
                            elif is_bonus in no_response:
                                print("No bonus paid\n")

                        elif tip_response in reject_response:
                            remove_tip_from_metadata(tips, tips_copy, i, unit)
                            print("Tip Rejected\n\n")

    print("There are no more tips to review\n")


if __name__ == "__main__":
    main()