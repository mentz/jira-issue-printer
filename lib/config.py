import os

from decouple import config

PRINTING_EXECUTABLE = config('PRINTING_EXECUTABLE')
PRINTING_ARGUMENTS = config('PRINTING_ARGUMENTS')
PAGE_WIDTH = config('PAGE_WIDTH', default=70,cast=int)
PAGE_HEIGHT = config('PAGE_HEIGHT', default=30,cast=int)
JIRA_USERNAME = config('JIRA_USERNAME')
JIRA_API_TOKEN = config('JIRA_API_TOKEN')
JSON_FILE = os.path.abspath(config('JSON_FILE', default='./issues.json'))
JIRA_SERVER_URL = config('JIRA_SERVER_URL')
JIRA_BOARD_ID = config('JIRA_BOARD_ID',cast=int)
JIRA_PROJECT_PREFIX = config('JIRA_PROJECT_PREFIX')
CLEAN_DATA = config('CLEAN_DATA', default=True, cast=bool)
