"""
Script that allows for tips to be approved or rejected.
Tips are collected by retrieving all units and then getting the agent of each unit.
The agent state has the tip data.

Approving a tip sets the accept property of the tip to be True.
This prevents it from appearing again when running this script.

Rejecting a tip deletes the tip from the tips list in the AgentState metadata.
"""
try:
    from rich import print
except ImportError:
    print(
        "\nYou need to have rich installed to use this script. For example: pip install rich\n"
    )
    exit(1)

from typing import List
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.data_model.unit import Unit
from mephisto.data_model.worker import Worker
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from rich.markdown import Markdown
from rich import box
from rich.prompt import Prompt
from rich.prompt import Confirm, FloatPrompt
from rich.table import Table
from mephisto.utils.rich import console


def get_index_of_value(lst: List[str], property: str):
    for i in range(len(lst)):
        if lst[i] == property:
            return i


def remove_tip_from_metadata(tips, tips_copy, i, unit):
    """Removes a tip from metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    index_to_remove = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy.pop(index_to_remove)
        assigned_agent.state.update_metadata({"tips": tips_copy})
    else:
        print("[red]An assigned agent was not able to be found for this tip[/red]")
        exit()


def accept_tip(tips: List, tips_copy: List, i: int, unit: Unit):
    """Accepts a tip in metadata"""
    tips_id = [tip_obj["id"] for tip_obj in tips_copy]
    # gets the index of the tip in the tip_copy list
    index_to_update = get_index_of_value(tips_id, tips[i]["id"])
    assigned_agent = unit.get_assigned_agent()

    if assigned_agent is not None:
        tips_copy[index_to_update]["accepted"] = True
        assigned_agent.state.update_metadata({"tips": tips_copy})


def main():
    db = LocalMephistoDB()
    mephisto_data_browser = MephistoDataBrowser(db)
    task_names = mephisto_data_browser.get_task_name_list()
    task_names_text = """# Tips Review \n ## Task Names:"""
    for task_name in task_names:
        task_names_text += "\n* " + task_name

    task_names_markdown = Markdown(task_names_text)
    console.print(task_names_markdown)
    print("")
    task_name = Prompt.ask(
        "\nEnter the name of the task that you want to review the tips of",
        choices=task_names,
        show_choices=False,
    ).strip()
    print("")
    units = mephisto_data_browser.get_all_units_for_task_name(task_name)
    if len(units) == 0:
        print("[red]No units were received[/red]")
        quit()
    for unit in units:
        if unit.agent_id is not None:
            unit_data = mephisto_data_browser.get_data_from_unit(unit)

            metadata = unit_data["data"]["metadata"]
            tips = metadata["tips"]
            if len(tips) > 0:
                tips_copy = tips.copy()
                for i in range(len(tips)):
                    if tips[i]["accepted"] == False:
                        current_tip_table = Table(
                            "Property",
                            "Value",
                            title="Tip {current_tip} of {total_number_of_tips}".format(
                                current_tip=i + 1, total_number_of_tips=len(tips)
                            ),
                            box=box.ROUNDED,
                            expand=True,
                            show_lines=True,
                        )
                        current_tip_table.add_row("Tip Id", tips[i]["id"])
                        current_tip_table.add_row("Tip Header", tips[i]["header"])
                        current_tip_table.add_row("Tip Text", tips[i]["text"])
                        console.print(current_tip_table)

                        tip_response = Prompt.ask(
                            "\nDo you want to accept, reject, or skip this tip",
                            choices=["a", "r", "s"],
                        ).strip()

                        print("")
                        if tip_response == "a":
                            # persists the tip in the db as it is accepted
                            accept_tip(tips, tips_copy, i, unit)
                            print("[green]Tip Accepted[/green]")
                            # given the option to pay a bonus to the worker who wrote the tip
                            is_bonus = Prompt.ask(
                                "\nDo you want to pay a bonus to this worker for their tip",
                                choices=["y", "n"],
                            ).strip()

                            if is_bonus == "y":
                                bonus_amount = FloatPrompt.ask(
                                    "\nHow much money do you want to give"
                                )

                                reason = Confirm.get_input(
                                    console,
                                    "\nWhat is your reason for the bonus: ",
                                    False,
                                )
                                worker_id = float(unit_data["worker_id"])
                                worker = Worker.get(db, worker_id)
                                if worker is not None:
                                    bonus_successfully_paid = worker.bonus_worker(
                                        bonus_amount, reason, unit
                                    )
                                    if bonus_successfully_paid:
                                        print(
                                            "\n[green]Bonus Successfully Paid![/green]\n"
                                        )
                                    else:
                                        print(
                                            "\n[red]There was an error when paying out your bonus[/red]\n"
                                        )
                            elif is_bonus == "n":
                                print("No bonus paid\n")

                        elif tip_response == "r":
                            remove_tip_from_metadata(tips, tips_copy, i, unit)
                            print("Tip Rejected\n")
                        elif tip_response == "s":
                            print("Tip Skipped\n")

    print("There are no more tips to review\n")


if __name__ == "__main__":
    main()
