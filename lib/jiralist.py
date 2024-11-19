import json
import os

from jira import JIRA


class JiraList():
    def __init__(self, server, user_name, api_token, jira_project_prefix, default_file='./issues.json', clean_data=False):
        self.jira_conn = JIRA(server=server, basic_auth=(user_name, api_token))
        self.json_file = default_file
        self.jira_project_prefix = jira_project_prefix

        if clean_data:
            self.remove_old_issues()

    def remove_old_issues(self):
        if os.path.exists(self.json_file):
            os.remove(self.json_file)

    def load_state(self):
        if not os.path.exists(self.json_file):
            return []
        with open(self.json_file, 'r') as infile:
            data = json.load(infile)
        return data

    def save_state(self, issues):
        data = [{"key": issue.key, "has_open_pr": self.get_issue_has_open_pr(issue)} for issue in issues]
        with open('issues.json', 'w') as outfile:
            json.dump(data, outfile)
            outfile.write("\n")

    def get_latest_sprint_for_board(self, board_id):
        return self.jira_conn.sprints(board_id)[-1]

    def get_tasks_in_sprint(self, sprint_name):
        return self.jira_conn.search_issues(f'project = {self.jira_project_prefix} AND sprint = "{sprint_name}" ORDER BY created DESC')

    def get_issues(self, jira_board_id):
            sprint = self.get_latest_sprint_for_board(jira_board_id)
            return self.get_tasks_in_sprint(sprint.name)

    def get_issue_has_open_pr(self, issue):
        try:
            customfield_10000 = json.loads(issue.fields.customfield_10000.split(', json=')[1][0:-1])
            pull_request_state = customfield_10000['cachedValue']['summary']['pullrequest']['overall']['state']
            return pull_request_state == 'OPEN'
        except:
            return False

    def filter_unassigned_to_do_tasks(self, issues):
        return list(filter(lambda issue: issue.fields.assignee == None and issue.fields.status.name == 'To Do', issues))

    def filter_new_issues(self, issues):
        new_issues = self.filter_unassigned_to_do_tasks(issues)
        previous_state = self.load_state()
        previous_issues = [issue['key'] for issue in previous_state]
        unseen_new_issues = [
            issue
            for issue in new_issues
            if issue.key not in previous_issues
        ]
        return unseen_new_issues

    def filter_issues_with_new_pull_requests(self, issues):
        previous_state = self.load_state()
        issues_with_new_open_pr = []
        for issue in issues:
            if self.get_issue_has_open_pr(issue):
                list_issue_on_previous_state = list(filter(lambda x: x['key'] == issue.key and x['has_open_pr'], previous_state))[:1]
                if len(list_issue_on_previous_state) == 0:
                    issues_with_new_open_pr += [issue]
        return issues_with_new_open_pr
