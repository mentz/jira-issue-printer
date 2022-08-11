import os
import math
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

jira = JIRA(server=JIRA_SERVER_URL, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))
#tasks_in_board = get_jira_tasks()

def get_latest_sprint(board_id):
    return jira.sprints(board_id)[-1]

def format_text(task_name, task_description):
    header = "~~~ NEW TASK ~~~".center(PAGE_WIDTH)
    title = textwrap.fill(f"{task_name} - {task_description}", width=PAGE_WIDTH)
    action = textwrap.fill("Note from boss: 'Dev, please work on this immediately!'", width=PAGE_WIDTH)

    full_text = "\n".join([header, title, action])
    line_count = full_text.count("\n")

    top_pad = "\n" * math.floor((PAGE_HEIGHT - line_count) / 2.0)
    padded_text = top_pad + full_text

    return padded_text

def print_text(text):
    printer = subprocess.Popen(PRINTING_EXECUTABLE, stdin=subprocess.PIPE, stdout=None)
    printer.stdin.write(bytes(text, "ASCII"))
    printer.stdin.close

task_name = "WORK-3144"
task_description = "Investigate UKG Worker API"

text = format_text(task_name, task_description)
print_text(text)

