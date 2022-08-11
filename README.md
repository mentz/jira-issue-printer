# jira-issue-printer
Have you ever wanted to feel pressured to work on a task as soon as it enters your team's Jira board? Well, fret no more!

## Dependencies
- `python3` (> 3.6) with `pip`
- Python modules:
  - `jira`, `dotenv` (install with `pip install jira python-dotenv`)
- A printer configured as the default printer.

## How to run

1. Copy `.env.example` to `.env`, fill-in the missing information and change the rest according to your needs.
2. Run the script with `python main.py`. Your printer should now spit out the full collection of unassigned tasks on your Jira board. This will happen only once, as the script saves the previous list of issues and won't print repeated issues, unless the issue is removed, the script runs, and the issue is added back before the next execution.
3. (if you are a manager) Take the printed ticket to your developer of choice.
   (if you are a developer) Rejoice in your new objective!

## Disclaimer

This script is provided as-is and might be full of bugs.

