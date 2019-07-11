# Built in Modules
import logging
from datetime import datetime

# 3rd Party Modules
import jinja2
import requests

# Local Modules
import config
import jibe.upstream as u
import jibe.downstream as d
import jibe.mailer as m

# Global Variables
log = logging.getLogger(__name__)


def load_config():
    """
    Generates and validates the config file
    Args:
    Returns:
        config (dict): The config dict to be used
                        later in the program
    """
    return config.config


def create_html(out_of_sync_issues, missing_issues, joke):
    """
    Generates HTML from out-of-sync data
    Args:
        out_of_sync_issues ([jibe.intermediary.Issue]): Out of sync issues
                                                      that have updated out_of_sync
                                                      lists
        missing_issues ([jib.intermediary.Issues]): Issues that have no matching downstream
                                                  issue
        joke (str): Optional joke string
    Returns:
        outputText (str): Generated HTML text
    """
    templateLoader = jinja2.FileSystemLoader(searchpath="./jibe/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "html_template.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    if joke:
        templatevars = {"now": datetime.now().strftime('%Y-%m-%d'),
                        "out_of_sync_issues": out_of_sync_issues,
                        "missing_issues": missing_issues,
                        "joke": joke}
    else:
        templatevars = {"now": datetime.now().strftime('%Y-%m-%d'),
                        "out_of_sync_issues": out_of_sync_issues,
                        "missing_issues": missing_issues}
    return template.render(templatevars)


def format_check(out_of_sync_issues):
    """
    Formats the check array per issue to be used by
    JINJA template
    Args:
        out_of_sync_issues (dict): Out of sync issues
    Returns:
        Nothing
    """
    for issue in out_of_sync_issues:
        # Get check array from config file
        old_check = issue.downstream['check']
        new_check = []
        for check in old_check:
            try:
                if 'transition' in check.keys():
                    new_check.append('transition')
            except AttributeError:
                if 'comments' in check:
                    new_check.append('comments')
                elif 'tags' in check:
                    new_check.append('tags')
                elif 'fixVersion' in check:
                    new_check.append('fixVersion')
                elif 'assignee' in check:
                    new_check.append('assignee')
                elif 'title' in check:
                    new_check.append('title')
        issue.check = new_check

def get_dad_joke():
    """
    A function to get a dad joke
    Args:
        Nothing
    Returns:
        Dad joke
    """
    # All joke credit goes here: icanhazdadjoke.com
    headers = {'Accept': 'application/json'}
    res = requests.get('https://icanhazdadjoke.com/', headers=headers)
    return res.json()['joke']


def main():
    """
    Main function to start sync
    Args:
    Returns:
        Nothing
    """
    # Load in config file
    config = load_config()

    # Loop through all groups
    for group in config['jibe']['send-to']:
        # Get all upstream issues
        issues = u.get_upstream_issues(config, group)

        # Compare them with downstream issues
        out_of_sync_issues, missing_issues = d.sync_with_downstream(issues, config)

        # Return differences to the user
        # First format the check array for each issue
        format_check(out_of_sync_issues)

        # Do we want jokes?
        if config['jibe']['send-to'][group].get('fun', {}):
            joke = get_dad_joke()
        else:
            joke = ''

        # Then generate the HTML
        html = create_html(out_of_sync_issues, missing_issues, joke)

        # Create mailer object and send email
        Mailer = m.Mailer()
        Mailer.send(config['jibe']['send-to'][group]['email-to'],
                    'Jibe Report for ' + group, html)
        log.info('   Finished sending report for %s' % group)

