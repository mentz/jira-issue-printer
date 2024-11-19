import math
import subprocess
import textwrap

import lib.config as cfg
from lib.jiralist import JiraList

def prepare_text_for_new_issue(issue):
    header = "~~~ TASK ENTERED SPRINT ~~~".center(cfg.PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=cfg.PAGE_WIDTH)
    details = textwrap.fill(f"Reporter: {issue.fields.creator}", width=cfg.PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=cfg.PAGE_WIDTH)

    footer = "~~~ DO IT NOW ~~~".center(cfg.PAGE_WIDTH)
    full_text = "\n".join([header, task, details, footer])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((cfg.PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def prepare_text_for_issue_with_new_pr(issue):
    header = "~~~ TASK HAS NEW PR ~~~".center(cfg.PAGE_WIDTH)
    task = textwrap.fill(f"{issue.key} {issue.fields.summary}", width=cfg.PAGE_WIDTH)
    details = textwrap.fill(f"Assignee: {issue.fields.assignee}", width=cfg.PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Reporter: {issue.fields.creator}", width=cfg.PAGE_WIDTH) + "\n" + \
              textwrap.fill(f"Priority: {issue.fields.priority}", width=cfg.PAGE_WIDTH)

    footer = "~~~ REVIEW IMMEDIATELY ~~~".center(cfg.PAGE_WIDTH)
    full_text = "\n".join([header, task, details, footer])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((cfg.PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def print_text(text):
    cmd_list = [cfg.PRINTING_EXECUTABLE]
    if cfg.PRINTING_ARGUMENTS:
        cmd_list += cfg.PRINTING_ARGUMENTS.split()

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
    jira = JiraList(cfg.JIRA_SERVER_URL, cfg.JIRA_USERNAME, cfg.JIRA_API_TOKEN, cfg.JIRA_PROJECT_PREFIX, cfg.JSON_FILE, cfg.CLEAN_DATA)
    issues = jira.get_issues(cfg.JIRA_BOARD_ID)

    new_issues = jira.filter_new_issues(issues)
    if len(new_issues):
        list_of_issue_keys = [issue.key for issue in new_issues]
        print(f"New issues entered the sprint. Now printing: {', '.join(list_of_issue_keys)}.")
        print_issues(new_issues, prepare_text_for_new_issue)
    else:
        print("No new issues found.")

    issues_with_new_prs = jira.filter_issues_with_new_pull_requests(issues)
    if len(issues_with_new_prs):
        list_of_issue_keys = ", ".join([issue.key for issue in issues_with_new_prs])
        print(f"Some issues have new open PRs: {list_of_issue_keys}.")
        print_issues(issues_with_new_prs, prepare_text_for_issue_with_new_pr)
    else:
        print("No issues have new PRs.")

    jira.save_state(issues)
