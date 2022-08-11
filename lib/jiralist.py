import json
import os

from jira import JIRA


class JiraList():
    def __init__(self, server, user_name, api_token,default_file='./issues.json',clean_data=False):
        self.jira_conn = JIRA(server=server, basic_auth=(user_name,api_token))
        self.json_file = default_file
        
        if clean_data:
            self.remove_old_issues()

    def remove_old_issues(self):
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

    def load_previous_issues(self):
        if not os.path.exists(self.json_file):
            return []
        with open(self.json_file, 'r') as infile:
            data = json.load(infile)
        return data

    def save_issues(self,issues):
        data = [issue.key for issue in issues]
        with open(self.json_file, 'w') as outfile:
            json.dump(data, outfile)
            outfile.write("\n")

    def get_latest_sprint_for_board(self, board_id):
        return self.jira_conn.sprints(board_id)[-1]

    def get_unassigned_to_do_tasks_in_sprint(self, sprint_name):
        return self.jira_conn.search_issues(f'project = WORK AND status = "To Do" AND assignee in (EMPTY) AND sprint = "{sprint_name}" ORDER BY created DESC')
    
    def get_new_issues(self,board_id):
        sprint = self.get_latest_sprint_for_board(board_id)
        issues = self.get_unassigned_to_do_tasks_in_sprint(sprint.name)
        previous_issues = self.load_previous_issues()
        self.save_issues(issues)    
        new_issues = [issue for issue in issues if issue.key not in previous_issues]
        return new_issues
