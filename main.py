import json
import math
import os
import subprocess
import textwrap
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

PRINTING_EXECUTABLE = os.getenv('PRINTING_EXECUTABLE')
PAGE_WIDTH = int(os.getenv('PAGE_WIDTH', 70))
PAGE_HEIGHT = int(os.getenv('PAGE_HEIGHT', 30))
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_SERVER_URL = os.getenv('JIRA_SERVER_URL')
JIRA_BOARD_ID = int(os.getenv('JIRA_BOARD_ID'))


def connect_jira_api():
    return JIRA(server=JIRA_SERVER_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

def load_previous_issues():
    try:
        with open('issues.json', 'r') as infile:
            data = json.load(infile)
            return data
    except:
        return []

def save_issues(issues):
    data = [issue.key for issue in issues]
    with open('issues.json', 'w') as outfile:
        json.dump(data, outfile)
        outfile.write("\n")

def get_latest_sprint_for_board(jira, board_id):
    return jira.sprints(board_id)[-1]

def get_unassigned_to_do_tasks_in_sprint(jira, sprint_name):
    return jira.search_issues(f'project = WORK AND status = "To Do" AND assignee in (EMPTY) AND sprint = "{sprint_name}" ORDER BY created DESC')

def get_new_issues(jira):
    sprint = get_latest_sprint_for_board(jira, JIRA_BOARD_ID)
    issues = get_unassigned_to_do_tasks_in_sprint(jira, sprint.name)

    previous_issues_keys = load_previous_issues()
    save_issues(issues)    

    new_issues = [issue for issue in issues if issue.key not in previous_issues_keys]

    return new_issues

def prepare_text_for_print(issue):
    header = "~~~ TASK ENTERED SPRINT ~~~".center(PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=PAGE_WIDTH)
    details = textwrap.fill(f"Reporter: {issue.fields.creator}", width=PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=PAGE_WIDTH)

    full_text = "\n".join([header, task, details])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def print_text(text):
    process = subprocess.run(
        PRINTING_EXECUTABLE,
        stdout=subprocess.DEVNULL,
        input=text,
        encoding='ascii'
    )

    if process.returncode != 0:
        print("Error while printing")

def print_issues(issues):
    for issue in issues:
        text = prepare_text_for_print(issue)
        print_text(text)


if __name__ == "__main__":
    jira = connect_jira_api()
    issues = get_new_issues(jira)
    if len(issues):
        list_of_issue_keys = [issue.key for issue in issues]
        print(f"New issues entered the sprint. Now printing: {', '.join(list_of_issue_keys)}.")
        print_issues(issues)
    else:
        print("No new issues found.")

