import math
import subprocess
import textwrap

import lib.config as cfg
from lib.jiralist import JiraList


def prepare_text_for_print(issue):
    header = "~~~ TASK ENTERED SPRINT ~~~".center(cfg.PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=cfg.PAGE_WIDTH)
    details = textwrap.fill(f"Reporter: {issue.fields.creator}", width=cfg.PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=cfg.PAGE_WIDTH)

    full_text = "\n".join([header, task, details])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((cfg.PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def print_text(text):
    process = subprocess.run(
        cfg.PRINTING_EXECUTABLE,
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
    jira = JiraList(cfg.JIRA_SERVER_URL, cfg.JIRA_USERNAME, cfg.JIRA_API_TOKEN, cfg.JSON_FILE, cfg.CLEAN_DATA)
    issues = jira.get_new_issues(cfg.JIRA_BOARD_ID)
    if len(issues):
        list_of_issue_keys = [issue.key for issue in issues]
        print(f"New issues entered the sprint. Now printing: {', '.join(list_of_issue_keys)}.")
        #print_issues(issues)
    else:
        print("No new issues found.")

