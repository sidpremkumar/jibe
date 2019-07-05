# Built in Modules
import logging
from datetime import datetime

# 3rd Party Modules
import jinja2

# Local Modules
import config
import jibe.upstream as u
import jibe.downstream as d
import jibe.mailer as m

def load_config():
    """
    Generates and validates the config file
    Args:
    Returns:
        config (dict): The config dict to be used
                        later in the program
    """
    return config.config


def create_html(out_of_sync_issues, missing_issues, check):
    """
    Generates HTML from out-of-sync data
    Args:
        out_of_sync_issues ([jibe.intermediary.Issue]): Out of sync issues
                                                      that have updated out_of_sync
                                                      lists
        missing_issues ([jib.intermediary.Issues]): Issues that have no matching downstream
                                                  issue
    Returns:
        outputText (str): Generated HTML text
    """
    templateLoader = jinja2.FileSystemLoader(searchpath="./jibe/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    TEMPLATE_FILE = "html_template.jinja"
    template = templateEnv.get_template(TEMPLATE_FILE)
    import pdb; pdb.set_trace()
    templatevars = {"now": datetime.now().strftime('%Y-%m-%d'),
                    "check": check,
                    "out_of_sync_issues": out_of_sync_issues,
                    "missing_issues": missing_issues}
    return template.render(templatevars)


def main():
    """
    Main function to start sync
    Args:
    Returns:
        Nothing
    """
    # Load in config file
    config = load_config()
    check = ['comments', 'tags', 'fixVersion', 'assignee', 'title',
                                           {'transition': 'CUSTOM_CLOSED_STATUS'}]
    # Get all upstream issues
    issues = u.get_upstream_issues(config)

    # Compare them with downstream issues
    out_of_sync_issues, missing_issues = d.sync_with_downstream(issues, config)

    # Return differences to the user
    # First generate the HTML
    html = create_html(out_of_sync_issues, missing_issues, check)

    # Create mailer object and send email
    Mailer = m.Mailer()
    Mailer.send(['sid.premkumar@gmail.com', 'srieger256@redhat.com'], 'test', html)