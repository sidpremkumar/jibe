# 3rd Party Modules
import requests
from github import Github

# Local Modules
import jibe.intermediary as i

def get_upstream_issues(config):
    """
    Gets all upstream issues in question
    Args:
         config (dict): The config dict to be used
                        later in the program
    Returns:
        Issues list(jibe.intermediary.Issues): List of issues
                                               that need to be
                                               checked
    """
    all_issues = []
    # Get all Github Issues
    # First get a list of upstream names
    github_repo_names = config['jibe']['upstream']['github'].keys()
    for repo in github_repo_names:
        # Loop through all repos and get issue data
        for issue in github_issues(repo, config):
            all_issues.append(issue)

    # Return all Issues
    return all_issues



def github_issues(upstream, config):
    """
    Gets all issues related to upstream Repo
    Args:
        upstream str: Upstream repo name
        config dict: Config dict
    Returns:
        Issues jibe.intermediary.Issues: List of issues and their metadata
    """

    token = config['jibe'].get('github_token')
    if not token:
        headers = {}
        log.warning('No github_token found.  We will be rate-limited...')
    else:
        headers = {'Authorization': 'token ' + token}

    _filter = config['jibe']\
        .get('filters', {})\
        .get('github', {})\
        .get(upstream, {})

    url = 'https://api.github.com/repos/%s/issues' % upstream
    if _filter:
        url += '?' + urlencode(_filter)

    issues = _get_all_github_issues(url, headers)

    # Initialize Github object so we can get their full name (instead of their username)
    # And get comments if needed
    github_client = Github(config['jibe']['github_token'])

    # We need to format everything to a standard to we can create an issue object
    final_issues = []
    for issue in issues:
        # Update comments:
        # If there are no comments just make an empty array
        if issue['comments'] == 0:
            issue['comments'] = []
        else:
            # We have multiple comments and need to make api call to get them
            repo = github_client.get_repo(upstream)
            comments = []
            github_issue = repo.get_issue(number=issue['number'])
            for comment in github_issue.get_comments():
                # First make API call to get the users name
                comments.append({
                    'author': comment.user.name,
                    'name': comment.user.login,
                    'body': comment.body,
                    'id': comment.id,
                    'date_created': comment.created_at,
                    'changed': None
                })
            # Assign the message with the newly formatted comments :)
            issue['comments'] = comments

        # Update reporter:
        # Search for the user
        reporter = github_client.get_user(issue['user']['login'])
        # Update the reporter field in the message (to match Pagure format)
        issue['user']['fullname'] = reporter.name

        # Update assignee(s):
        assignees = []
        for person in issue['assignees']:
            assignee = github_client.get_user(person['login'])
            assignees.append({'fullname': assignee.name})
        # Update the assignee field in the message (to match Pagure format)
        issue['assignees'] = assignees

        # Update label(s):
        if issue['labels']:
            # loop through all the labels on Github and add them
            # to the new label list and then reassign the message
            new_label = []
            for label in issue['labels']:
                new_label.append(label['name'])
            issue['labels'] = new_label

        # Update milestone:
        if issue['milestone']:
            issue['milestone'] = issue['milestone']['title']

        final_issues.append(issue)

    final_issues = list((
        i.Issue.from_github(upstream, issue, config) for issue in final_issues
        if 'pull_request' not in issue  # We don't want to copy these around
    ))

    for issue in final_issues:
        yield issue


def _get_all_github_issues(url, headers):
    """ Pagination utility.  Obnoxious. """
    link = dict(next=url)
    while 'next' in link:
        response = _fetch_github_data(link['next'], headers)
        for issue in response.json():
            comments = _fetch_github_data(issue['comments_url'], headers)
            issue['comments'] = comments.json()
            yield issue
        link = _github_link_field_to_dict(response.headers.get('link', None))


def _github_link_field_to_dict(field):
    """ Utility for ripping apart github's Link header field.
    It's kind of ugly.
    """

    if not field:
        return dict()
    return dict([
        (
            part.split('; ')[1][5:-1],
            part.split('; ')[0][1:-1],
        ) for part in field.split(', ')
    ])


def _fetch_github_data(url, headers):
    response = requests.get(url, headers=headers)
    if not bool(response):
        try:
            reason = response.json()
        except Exception:
            reason = response.text
        raise IOError("response: %r %r %r" % (response, reason, response.request.url))
    return response
