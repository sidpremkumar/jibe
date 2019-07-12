# Built in Modules
import logging
from datetime import datetime
import argparse

# 3rd Party Modules
import jinja2
import requests
import jira.client

# Local Modules
import config
import jibe.upstream as u
import jibe.downstream as d
import jibe.mailer as m

# Global Variables
log = logging.getLogger(__name__)
remote_link_title = "Upstream issue"


def load_config():
    """
    Generates and validates the config file
    Args:
    Returns:
        config (dict): The config dict to be used
                        later in the program
    """
    return config.config


def load_sync2jira_config():
    """
    Generates and validates the config file from a sync2jira file
    Args:
    Returns:
        config (dict): The config dict to be used
                        later in the program
    """
    # Import out config files
    import sync2jira_config
    import config_sync2jira

    # Extract relevant data
    old_config = config_sync2jira.config
    sync2jira_config = sync2jira_config.config

    # Start building our new config file
    new_config = {'jibe': {}}

    # Get Github Token
    new_config['jibe']['github_token'] = sync2jira_config['sync2jira']['github_token']

    # Get Jira and default Jira information
    new_config['jibe']['default_jira_instance'] = sync2jira_config['sync2jira']['default_jira_instance']
    new_config['jibe']['jira'] = sync2jira_config['sync2jira']['jira']

    # Go group by group and add information
    new_config['jibe']['send-to'] = {}
    for group in old_config['jibe']['send-to']:
        new_config['jibe']['send-to'][group] = {'upstream': {'pagure': {}, 'github': {}}}
        projects = old_config['jibe']['send-to'][group]['projects']
        check = old_config['jibe']['send-to'][group]['check']
        email_to = old_config['jibe']['send-to'][group]['email-to']
        fun = old_config['jibe']['send-to'][group].get('fun', {})
        # Start with pagure
        for project in sync2jira_config['sync2jira']['map']['pagure'].keys():
            if project in projects:
                new_config['jibe']['send-to'][group]['upstream']['pagure'][project] =\
                    {'project': sync2jira_config['sync2jira']['map']['pagure'][project]['project'],
                     'component': sync2jira_config['sync2jira']['map']['pagure'][project]['component'],
                     'check': check}
        # Then do Github
        for project in sync2jira_config['sync2jira']['map']['github'].keys():
            if project in projects:
                new_config['jibe']['send-to'][group]['upstream']['github'][project] =\
                    {'project': sync2jira_config['sync2jira']['map']['github'][project]['project'],
                     'component': sync2jira_config['sync2jira']['map']['github'][project]['component'],
                     'check': check}
        # Then add relevant information
        new_config['jibe']['send-to'][group]['email-to'] = email_to
        new_config['jibe']['send-to'][group]['fun'] = fun

    return new_config


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


def attach_link_helper(client, downstream, remote_link):
    """
    Attaches the upstream link to the JIRA ticket
    Args:
        client (jira.client.JIRA): JIRA client
        downstream (jira.resources.Issue): Response from
                                           creating the
                                           JIRA ticket
        remote_link():
    Returns:
        downstream (jira.resources.Issue): Response from
                                           creating the
                                           JIRA ticket
    """
    log.info("   Attaching tracking link %r to %r", remote_link, downstream.key)
    modified_desc = downstream.fields.description + " "

    # This is crazy.  Querying for application links requires admin perms which
    # we don't have, so duckpunch the client to think it has already made the
    # query.
    client._applicationlinks = []  # pylint: disable=protected-access

    # Add the link.
    client.add_remote_link(downstream.id, remote_link)

    # Finally, after we've added the link we have to edit the issue so that it
    # gets re-indexed, otherwise our searches won't work. Also, Handle some
    # weird API changes here...
    log.debug("    Modifying desc of %r to trigger re-index.", downstream.key)
    downstream.update({'description': modified_desc})

    return downstream


def attach_link(issue_id, url, config):
    """
    Function to attach remote links to JIRA issues
    Args:
        issue_id (str): Jira issue id (i.e. FACTORY-1245)
        url (str): Upstream URL we want to attach
        config (dict): Config dict
    Returns:
        Nothing
    """
    # Get default client
    default_instance = config['jibe']['default_jira_instance']
    client = jira.client.JIRA(**config['jibe']['jira'][default_instance])

    # Get downstream issue
    downstream = client.issue(issue_id)

    # Attach link
    remote_link = dict(url=url, title=remote_link_title)
    ret = attach_link_helper(client, downstream, remote_link)
    if not ret:
        log.warning('   Unable to attach remote link for %s' % issue_id)
    return


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
    # Build out argparser
    usage = "CLI for generating reports on upstream/downstream issues " \
            "that are out of sync"
    argparser = argparse.ArgumentParser(usage=usage)
    argparser.add_argument('--sync2jira', default=False, action='store_true',
                           help='Parse sync2jira config file instead ')
    argparser.add_argument('--link-issue', nargs=2, type=str,
                           metavar=('FACTORY-XXX', 'some_url.com'),
                           help='Add remote link to downstream issue')
    argparser.add_argument('--ignore-in-sync', default=False, action='store_true',
                           help='Omit issues that are in sync from report')
    args = argparser.parse_args()

    # Load in config file
    if args.sync2jira:
        config = load_sync2jira_config()
    else:
        config = load_config()

    if args.link_issue:
        # Call link function and return
        attach_link(args.link_issue[0], args.link_issue[1], config)
        return

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

        # Remove in sync items if requested
        if args.ignore_in_sync:
            new_out_of_sync_issues = []
            for issue in out_of_sync_issues:
                if issue.total != issue.done:
                    new_out_of_sync_issues.append(issue)
            out_of_sync_issues = new_out_of_sync_issues

        # Then generate the HTML
        html = create_html(out_of_sync_issues, missing_issues, joke)

        # Create mailer object and send email
        if not config['jibe']['send-to'][group]['email-to']:
            log.warning('   Email list is empty. No one was emailed.')
            return

        Mailer = m.Mailer()
        Mailer.send(config['jibe']['send-to'][group]['email-to'],
                    'Jibe Report for ' + group, html)
        log.info('   Finished sending report for %s' % group)

