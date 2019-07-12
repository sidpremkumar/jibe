# Built In Modules
import logging

# 3rd Party Modules
import jira.client

# Local Modules
from jibe.intermediary import Issue, Comment

# Global Variables
log = logging.getLogger(__name__)
remote_link_title = "Upstream issue"


def get_jira_client(issue, config):
    """
    Function to match and create JIRA client
    Args:
        issue (jibe.intermediary.Issue): Issue object
        config (dict): Config dict
    Returns:
        client (jira.client.JIRA): Matching JIRA client
    """
    # The name of the jira instance to use is stored under the 'map'
    # key in the config where each upstream is mapped to jira projects.
    # It is conveniently added to the Issue object from intermediary.py
    # so we can use it here:

    if not isinstance(issue, Issue):
        log.error("passed in issue is not an Issue instance")
        log.error("It is a %s" % (type(issue).__name__))
        raise Exception

    # Use the Jira instance set in the issue config. If none then
    # use the configured default jira instance.
    jira_instance = issue.downstream.get('jira_instance', False)
    if not jira_instance:
        jira_instance = config['jibe'].get('default_jira_instance', False)
    if not jira_instance:
        log.error("   No jira_instance for issue and there is no default in the config")
        raise Exception
    client = jira.client.JIRA(**config['jibe']['jira'][jira_instance])
    return client


def matching_jira_issue_query(client, issue, config, free=False):
    """
    API calls that find matching JIRA tickets if any are present
    Args:
        client (jira.client.JIRA): JIRA client
        issue (sync2jira.intermediary.Issue): Issue object
        config (dict): Config dict
        free (Bool): Free tag to add 'statusCategory != Done' to query
    Returns:
        results (lst): Returns a list of matching JIRA issues if any are found
    """
    # Searches for any remote link to the issue.url
    query = 'issueFunction in linkedIssuesOfRemote("%s") and ' \
        'issueFunction in linkedIssuesOfRemote("%s")' % (
            remote_link_title, issue.url)
    if free:
        query += ' and statusCategory != Done'
    # Query the JIRA client and store the results
    results_of_query = client.search_issues(query)

    if len(results_of_query) > 1:
        # Sometimes if an issue gets dropped it is created with the url: pagure.com/something/issue/5
        # Then when that issue is dropped and another one is created is is created with the same
        # url : pagure.com/something/issue/5.
        # We need to ensure that we are not catching a dropped issue
        # Loop through the results of the query and make sure the ids match
        final_results = []
        for result in results_of_query:
            # If the queried JIRA issue has the id of the upstream issue or the same title
            if issue.id in result.fields.description or issue.title == result.fields.summary or \
                    issue.upstream_title == result.fields.summary:
                search = check_comments_for_duplicate(client, result,
                                                      find_username(issue, config))
                if search is True:
                    final_results.append(result)
                else:
                    # Else search returned a linked issue
                    final_results.append(search)
            # If that's not the case, check if they have the same upstream title
            # Upstream username/repo can change if repos are merged
            elif re.search(r"\[[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};':\\|,.<>\/?]*\] "
                           + issue.upstream_title,
                           result.fields.summary):
                search = check_comments_for_duplicate(client, result,
                                                      find_username(issue, config))
                if search is True:
                    # We went through all the comments and didn't find anything
                    # that indicated it was a duplicate
                    log.warning('   Matching downstream issue %s to upstream issue %s' %
                                (result.fields.summary, issue.title))
                    final_results.append(result)
                else:
                    # Else search returned a linked issue
                    final_results.append(search)
        if not final_results:
            # Just return the most updated issue
            results_of_query.sort(key=lambda x: datetime.strptime(
                x.fields.updated, '%Y-%m-%dT%H:%M:%S.%f+0000'))
            final_results.append(results_of_query[0])

        # Return the final_results
        log.debug("Found %i results for query %r", len(final_results), query)
        return final_results
    else:
        return results_of_query


def find_username(issue, config):
    """
    Finds JIRA username for an issue object
    Args:
        issue (sync2jira.intermediary.Issue): Issue object
        config (dict): Config dict
    Returns:
        return (str): Username string
    """
    jira_instance = issue.downstream.get('jira_instance', False)
    if not jira_instance:
        jira_instance = config['sync2jira'].get('default_jira_instance', False)
    if not jira_instance:
        log.error("   No jira_instance for issue and there is no default in the config")
        raise Exception
    return config['sync2jira']['jira'][jira_instance]['basic_auth'][0]


def check_comments_for_duplicate(client, result, username):
    """
    Checks comment of JIRA issue to see if it has been
    marked as a duplicate
    Args:
        client (jira.client.JIRA): JIRA client)
        result (jira.resource.Issue): JIRA issue
        username (str): Username of JIRA user
    Returns:
        return (bool): True if duplicate comment was not found
        *Or*
        return (jira.resource.Issue): JIRA issue if we were able to
                                      find it
    """
    for comment in client.comments(result):
        search = re.search(r'Marking as duplicate of (\w*)-(\d*)',
                           comment.body)
        if search and comment.author.name == username:
            issue_id = search.groups()[0] + '-' + search.groups()[1]
            return client.issue(issue_id)
    return True


def get_existing_jira_issue(client, issue, config):
    """
    Get a jira issue by the linked remote issue.
    This is the new supported way of doing this.
    Args:
        client (jira.client.JIRA): JIRA client
        issue (jibe.intermediary.Issue): Issue object
        config (dict): Config dict
    Returns:
        response (lst): Returns a list of matching JIRA issues if any are found
    """
    results = matching_jira_issue_query(client, issue, config)
    if results:
        return results[0]
    else:
        return None


def comment_matching(issue_comments, comments):
    """
    Function to match comments that have already been added
    Args:
         issue_comments dict: Upstream issue comments
         comments dict: JIRA comments
    Returns:
        updated_comments dict: Updated Upstream issue comments
    """
    found = False
    final_comments = []
    # Loop through all comments, if we find a match, set found to True
    # And move onto the next comment. Otherwise it was not found and
    # Append to final comments
    for comment_upstream in issue_comments:
        for comment_jira in comments:
            if comment_upstream['body'] in comment_jira.body:
                found = True
                break
        if not found:
            found = True
            final_comments.append(comment_upstream)
        else:
            found = False
    return final_comments


def check_comments(existing, issue, client):
    """
    Updates comments in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
        client (jira.client.JIRA): JIRA client
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    # Get all existing comments
    comments = client.comments(existing)
    # Remove any comments that have already been added
    comments_d = comment_matching(issue.comments, comments)
    updated_comments = []
    for comment in comments_d:
        # Loop through any comments returned
        # and format
        updated_comments.append(Comment(
            author=comment['author'],
            body=comment['body'],
            date_created=comment['date_created']
        ))
    # Update and return issue
    if len(updated_comments) == 0:
        issue.out_of_sync['comments'] = 'in-sync'
    else:
        issue.out_of_sync['comments'] = updated_comments
    return issue


def check_tags(existing, issue):
    """
    Updates tags in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    # If they're the same just return
    if sorted(existing.fields.labels) == sorted(issue.tags):
        return issue
    # Else they are different
    upstream = issue.tags
    downstream = existing.fields.labels
    difference = [i for i in existing.fields.labels if i not in issue.tags] + \
                 [j for j in issue.tags if j not in existing.fields.labels]
    issue.out_of_sync['tags'] = {'upstream': upstream, 'downstream': downstream, 'difference': difference}
    return issue


def check_fixVersion(existing, issue):
    """
    Updates tags in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    # First convert existing fixVersion to list
    jira_fixVersion = []
    for version in existing.fields.fixVersions:
        jira_fixVersion.append(version.name)

    # If they're the same just return
    if jira_fixVersion == issue.fixVersion:
        return issue
    # Else they are different
    upstream = issue.fixVersion
    downstream = jira_fixVersion
    difference = [i for i in jira_fixVersion if i not in issue.fixVersion] + \
                 [j for j in issue.fixVersion if j not in jira_fixVersion]
    issue.out_of_sync['fixVersions'] = {'upstream': upstream, 'downstream': downstream, 'difference': difference}
    return issue


def check_assignee(existing, issue):
    """
    Updates assignee in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    if existing.fields.assignee:
        if existing.fields.assignee.displayName == issue.assignee[0]['fullname']:
            # If they're the same return
            return issue
    elif not issue.assignee:
        # If they are both unassigned
        return issue
    # Else they are different
    upstream = issue.assignee[0]['fullname']
    downstream = existing.fields.assignee
    issue.out_of_sync['assignee'] = {'upstream': upstream, 'downstream': downstream}
    return issue


def check_title(existing, issue):
    """
    Updates title in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    if existing.fields.summary == issue.title or existing.fields.summary == issue.upstream_title:
        # If they're the same return
        return issue
    # Else they are different
    upstream = issue.title
    downstream = existing.fields.summary
    issue.out_of_sync['title'] = {'upstream': upstream, 'downstream': downstream}
    return issue


def check_transition(existing, issue):
    """
    Updates transition in issue.out_of_sync list
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
    Returns:
        response (jibe.intermediary.Issue): Issue object with updated
                                            out-of-sync updated
    """
    # First get the closed status from the config file
    try:
        # For python 3 >
        closed_status = list(filter(lambda d: "transition" in d, issue.downstream.get('check')))[0]['transition']
    except ValueError:
        # for python 2.7
        closed_status = (filter(lambda d: "transition" in d, issue.downstream.get('check')))[0]['transition']
    if issue.status == 'Closed' and existing.fields.status.name.upper() == closed_status.upper() or \
            issue.status == 'Open' and existing.fields.status.name.upper() != closed_status.upper():
        # They are in sync just return
        return issue

    # Else they are different
    upstream = issue.status
    downstream = existing.fields.status.name
    out_of_sync = {'transition': {'upstream': upstream, 'downstream': downstream}}
    if issue.status == 'Closed' and existing.fields.status.name.upper() != closed_status.upper():
        # Upstream issue is closed while downstream issue is open
        out_of_sync = {'upstream-close-downstream-open': {'upstream': upstream, 'downstream': downstream}}
    elif issue.status == 'Open' and existing.fields.status.name.upper() == closed_status.upper():
        # Upstream issue is open while downstream issue is closed
        out_of_sync = {'upstream-open-downstream-close': {'upstream': upstream, 'downstream': downstream}}
    issue.out_of_sync['transition'] = out_of_sync
    return issue


def update_out_of_sync(existing, issue, client, config):
    """
    Updates the 'out-of-sync' list to indicate fields that are out of sync
    Args:
        existing (jira.resource.Issue): JIRA client
        issue (jibe.intermediary.Issue): Issue object
        client (jira.client.JIRA): JIRA client
        config (dict): Config dict
    Returns:
        response (lst): Returns a list of matching JIRA issues if any are found
    """
    # Get the list of what to check
    check = issue.downstream.get('check', {})

    # Update basic information
    # Update issue key (i.e. FACTORY-XXX)
    issue.downstream_id = existing.key

    # Update downstream URL
    jira_instance = issue.downstream.get('jira_instance', False)
    if not jira_instance:
        jira_instance = config['jibe'].get('default_jira_instance', False)
    if not jira_instance:
        log.warning("No JIRA instance selected for %s" % issue.upstream)
        return
    url = config['jibe']['jira'][jira_instance]['options']['server'] + '/browse/' + existing.key
    issue.downstream_url = url

    # Update priority
    if existing.fields.priority:
        issue.priority = existing.fields.priority.name
        issue.priority_icon = existing.fields.priority.iconUrl
    else:
        issue.priority = 'Unknown'
        issue.priority_icon = 'Unknown'

    if not check:
        # Something might be up if check returns {}
        log.warning('   Nothing to check for issue %s' % issue.title)
        return issue

    total_done = 0

    if 'comments' in check:
        log.info('   Looking for out of sync comment(s)')
        issue = check_comments(existing, issue, client)
        if issue.out_of_sync['comments'] == 'in-sync':
            total_done += 1

    if 'tags' in check:
        log.info('   Looking for out of sync tags')
        issue = check_tags(existing, issue)
        if issue.out_of_sync['tags'] == 'in-sync':
            total_done += 1

    if 'fixVersion' in check:
        log.info('   Looking for out of sync fixVersion(s)')
        issue = check_fixVersion(existing, issue)
        if issue.out_of_sync['fixVersion'] == 'in-sync':
            total_done += 1

    if 'assignee' in check:
        log.info('   Looking for out of sync assignee(s)')
        issue = check_assignee(existing, issue)
        if issue.out_of_sync['assignee'] == 'in-sync':
            total_done += 1

    if 'title' in check:
        log.info('   Looking for out of sync title')
        issue = check_title(existing, issue)
        if issue.out_of_sync['title'] == 'in-sync':
            total_done += 1

    if any('transition' in item for item in check):
        log.info('   Looking for out of sync transition state')
        issue = check_transition(existing, issue)
        if issue.out_of_sync['transition'] == 'in-sync':
            total_done += 1

    # Update percent done
    issue.total = len(check)
    issue.done = total_done
    issue.percent_done = int(100 * float(issue.done) / float(issue.total))
    return issue


def sync_with_downstream(issues, config):
    """
    Function to clean up upstream issues that are already in sync
    Args:
        issues ([jibe.intermediary.Issue]): All upstream issues
        config (dict): Config dict
    Returns:
        out_of_sync_issues ([jibe.intermediary.Issues]): List of issues that are out of sync
        missing_issues ([jibe.intermediary.Issues]): List of issues where no matching
                                                   JIRA issue could be found
    """
    out_of_sync_issues = []
    missing_issues = []
    # Loop through all issues and find out if their out of sync
    for issue in issues:
        log.info("   Considering upstream %s, %s", issue.url, issue.title)
        # Create a client connection for this issue
        client = get_jira_client(issue, config)

        # Try to find
        existing = get_existing_jira_issue(client, issue, config)
        if existing:
            # If we found an existing JIRA issue already
            log.info("   Found existing, matching downstream %r.", existing.key)
            # Update relevant metadata (i.e. tags, assignee, etc)
            updated_issue = update_out_of_sync(existing, issue, client, config)
            out_of_sync_issues.append(updated_issue)
        else:
            log.warning("   Could not find existing issue for %s", issue.title)
            missing_issues.append(issue)

    return out_of_sync_issues, missing_issues
