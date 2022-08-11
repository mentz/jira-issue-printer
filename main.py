import json
import math
import os
import subprocess
import textwrap
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()

PRINTING_EXECUTABLE = os.getenv('PRINTING_EXECUTABLE')
PRINTING_ARGUMENTS = os.getenv('PRINTING_ARGUMENTS')
PAGE_WIDTH = int(os.getenv('PAGE_WIDTH', 70))
PAGE_HEIGHT = int(os.getenv('PAGE_HEIGHT', 30))
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
JIRA_SERVER_URL = os.getenv('JIRA_SERVER_URL')
JIRA_BOARD_ID = int(os.getenv('JIRA_BOARD_ID'))
JIRA_PROJECT_PREFIX = os.getenv('JIRA_PROJECT_PREFIX')


def connect_jira_api():
    return JIRA(server=JIRA_SERVER_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

def load_previous_state():
    try:
        with open('issues.json', 'r') as infile:
            data = json.load(infile)
            return data
    except:
        return []

def get_issue_has_open_pr(issue):
    try:
        customfield_10000 = json.loads(issue.fields.customfield_10000.split(', json=')[1][0:-1])
        pull_request_state = customfield_10000['cachedValue']['summary']['pullrequest']['overall']['state']

        return pull_request_state == 'OPEN'
    except:
        return False

def save_state(issues):
    data = [
        {
            "key": issue.key,
            "has_open_pr": get_issue_has_open_pr(issue)
        } for issue in issues
    ]

    with open('issues.json', 'w') as outfile:
        json.dump(data, outfile)
        outfile.write("\n")

def get_latest_sprint_for_board(jira, board_id):
    return jira.sprints(board_id)[-1]

def filter_unassigned_to_do_tasks(issues):
    return list(filter(lambda issue: issue.fields.assignee == None and issue.fields.status.name == 'To Do', issues))

def get_tasks_in_sprint(jira, sprint_name):
    return jira.search_issues(f'project = {JIRA_PROJECT_PREFIX} AND sprint = "{sprint_name}" ORDER BY created DESC')

def get_issues(jira):
    sprint = get_latest_sprint_for_board(jira, JIRA_BOARD_ID)
    return get_tasks_in_sprint(jira, sprint.name)

def filter_new_issues(issues):
    new_issues = filter_unassigned_to_do_tasks(issues)
    previous_state = load_previous_state()
    
    previous_issues = [issue['key'] for issue in previous_state]
    unseen_new_issues = [
        issue
        for issue in new_issues
        if issue.key not in previous_issues
    ]

    return unseen_new_issues

def filter_issues_with_new_pull_requests(issues):
    previous_state = load_previous_state()

    issues_with_new_open_pr = []

    for issue in issues:
        if get_issue_has_open_pr(issue):
            list_issue_on_previous_state = filter(lambda x: x['key'] == issue.key and x['has_open_pr'], previous_state)[:1]

            if len(list_issue_on_previous_state) == 0:
                issues_with_new_open_pr += [issue]

    return issues_with_new_open_pr

def prepare_text_for_new_issues(issue):
    header = "~~~ TASK ENTERED SPRINT ~~~".center(PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=PAGE_WIDTH)
    details = textwrap.fill(f"Reporter: {issue.fields.creator}", width=PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=PAGE_WIDTH)
    footer = "~~~ DO IT NOW ~~~".center(PAGE_WIDTH)

    full_text = "\n".join([header, task, details, footer])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def prepare_text_for_issues_with_new_prs(issue):
    header = "~~~ TASK HAS NEW PR ~~~".center(PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=PAGE_WIDTH)
    details = textwrap.fill(f"Assignee: {issue.fields.assignee}", width=PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Reporter: {issue.fields.creator}", width=PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=PAGE_WIDTH)
    footer = "~~~ REVIEW IMMEDIATELY ~~~".center(PAGE_WIDTH)

    full_text = "\n".join([header, task, details, footer])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def print_text(text):
    cmd_list = [PRINTING_EXECUTABLE]
    if PRINTING_ARGUMENTS:
        cmd_list += PRINTING_ARGUMENTS.split()

    process = subprocess.run(
        cmd_list,
        stdout=subprocess.DEVNULL,
        input=text,
        encoding='ascii'
    )

    if process.returncode != 0:
        print("Error while printing")

def print_issues(issues, text_generator):
    for issue in issues:
        text = text_generator(issue)
        print_text(text)


if __name__ == "__main__":
    jira = connect_jira_api()
    issues = get_issues(jira)

    new_issues = filter_new_issues(issues)
    if len(new_issues):
        list_of_issue_keys = ", ".join([issue.key for issue in new_issues])
        print(f"New issues entered the sprint: {list_of_issue_keys}.")
        print_issues(new_issues, prepare_text_for_new_issues)
    else:
        print("No issues entered the sprint.")

    issues_with_new_prs = filter_issues_with_new_pull_requests(issues)
    if len(issues_with_new_prs):
        list_of_issue_keys = ", ".join([issue.key for issue in issues_with_new_prs])
        print(f"Some issues have new open PRs: {list_of_issue_keys}.")
        print_issues(new_issues, prepare_text_for_issues_with_new_prs)
    else:
        print("No issues have new PRs.")

    save_state(issues)

