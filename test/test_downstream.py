# Built In Modules
import mock
import unittest
try:
    # Python 3.3 >
    from unittest.mock import MagicMock  # noqa: F401
except ImportError:
    from mock import MagicMock  # noqa: F401

# Local Modules
import jibe.downstream as d
from jibe.intermediary import Issue, Comment

# 3rd Party Modules
from nose.tools import eq_

# Global Variables
PATH = 'jibe.downstream.'


class TestDownstream(unittest.TestCase):
    """
    This class tests main.py under jibe
    """
    def setUp(self):
        """
        Setting up the testing environment
        """
        # Mock Config dict
        self.mock_config = {
            'jibe': {
                'default_jira_instance': 'another_jira_instance',
                'jira': {
                    'mock_jira_instance': {'mock_jira': 'mock_jira'},
                    'another_jira_instance': {'basic_auth': ['mock_user'],
                                              'options': {'server': 'mock_server'}}
                },
                'testing': {},
                'legacy_matching': False,
                'admins': ['mock_admin']
            },
        }

        # Mock jibe.intermediary.Issue
        self.mock_issue = MagicMock()
        self.mock_issue.assignee = [{'fullname': 'mock_user'}]
        self.mock_issue.downstream = {
            'project': 'mock_project',
            'custom_fields': {'somecustumfield': 'somecustumvalue'},
            'type': 'Fix',
            'updates': [
                'comments',
                {'tags': {'overwrite': False}},
                {'fixVersion': {'overwrite': False}},
                'assignee', 'description', 'title',
                {'transition': 'CUSTOM TRANSITION'}
            ],
            'owner': 'mock_owner'
        }
        self.mock_issue.content = 'mock_content'
        self.mock_issue.reporter = {'fullname': 'mock_user'}
        self.mock_issue.url = 'mock_url'
        self.mock_issue.title = 'mock_title'
        self.mock_issue.comments = 'mock_comments'
        self.mock_issue.tags = ['tag1', 'tag2']
        self.mock_issue.fixVersion = ['fixVersion3', 'fixVersion4']
        self.mock_issue.fixVersion = ['fixVersion3', 'fixVersion4']
        self.mock_issue.assignee = [{'fullname': 'mock_assignee'}]
        self.mock_issue.status = 'Open'
        self.mock_issue.id = '1234'

        # Mock jira.resources.Issue
        self.mock_downstream = MagicMock()
        self.mock_downstream.id = 1234
        self.mock_downstream.fields.labels = ['tag3', 'tag4']
        mock_version1 = MagicMock()
        mock_version1.name = 'fixVersion3'
        mock_version2 = MagicMock()
        mock_version2.name = 'fixVersion4'
        self.mock_downstream.fields.fixVersions = [mock_version1, mock_version2]
        self.mock_downstream.update.return_value = True
        self.mock_downstream.fields.description = "This is an existing description"

    @mock.patch('jira.client.JIRA')
    def test_get_jira_client_not_issue(self,
                                       mock_client):
        """
        This tests '_get_jira_client' function where the passed in
        argument is not an Issue instance
        """
        # Call the function
        with self.assertRaises(Exception):
            d.get_jira_client(
                issue='string',
                config=self.mock_config
            )

        # Assert everything was called correctly
        mock_client.assert_not_called()

    @mock.patch('jira.client.JIRA')
    def test_get_jira_client_not_instance(self,
                                          mock_client):
        """
        This tests '_get_jira_client' function there is no JIRA instance
        """
        # Set up return values
        self.mock_issue.downstream = {}
        self.mock_config['jibe']['default_jira_instance'] = {}

        # Call the function
        with self.assertRaises(Exception):
            d.get_jira_client(
                issue=self.mock_issue,
                config=self.mock_config
            )

        # Assert everything was called correctly
        mock_client.assert_not_called()

    @mock.patch('jira.client.JIRA')
    def test_get_jira_client(self,
                             mock_client):
        """
        This tests '_get_jira_client' function where everything goes smoothly
        """
        # Set up return values
        mock_issue = MagicMock(spec=Issue)
        mock_issue.downstream = {'jira_instance': 'mock_jira_instance'}
        mock_client.return_value = 'Successful call!'

        # Call the function

        response = d.get_jira_client(
            issue=mock_issue,
            config=self.mock_config
        )

        # Assert everything was called correctly
        mock_client.assert_called_with(mock_jira='mock_jira')
        self.assertEqual('Successful call!', response)

    @mock.patch(PATH + 'find_username')
    @mock.patch(PATH + 'check_comments_for_duplicate')
    @mock.patch('jira.client.JIRA')
    def test_matching_jira_issue_query(self,
                                       mock_client,
                                       mock_check_comments_for_duplicates,
                                       mock_find_username):
        """
        This tests '_matching_jira_query' function
        """
        # Set up return values
        mock_downstream_issue = MagicMock()
        self.mock_issue.upstream_title = 'mock_upstream_title'
        mock_downstream_issue.fields.description = self.mock_issue.id
        bad_downstream_issue = MagicMock()
        bad_downstream_issue.fields.description = 'bad'
        bad_downstream_issue.fields.summary = 'bad'
        mock_client.search_issues.return_value = [mock_downstream_issue, bad_downstream_issue]
        mock_check_comments_for_duplicates.return_value = True
        mock_find_username.return_value = 'mock_username'

        # Call the function
        response = d.matching_jira_issue_query(
            client=mock_client,
            issue=self.mock_issue,
            config=self.mock_config
        )

        # Assert everything was called correctly
        self.assertEqual(response, [mock_downstream_issue])
        mock_client.search_issues.assert_called_with(
            'issueFunction in linkedIssuesOfRemote("Upstream issue")'
            ' and issueFunction in linkedIssuesOfRemote("mock_url")')
        mock_check_comments_for_duplicates.assert_called_with(
            mock_client,
            mock_downstream_issue,
            'mock_username'
        )
        mock_find_username.assert_called_with(
            self.mock_issue,
            self.mock_config
        )

    def test_find_username(self):
        """
        Tests 'find_username' function
        """
        # Call the function
        response = d.find_username(
            self.mock_issue,
            self.mock_config
        )

        # Assert everything was called correctly
        self.assertEqual(response, 'mock_user')

    @mock.patch('jira.client.JIRA')
    def test_check_comments_for_duplicates(self,
                                           mock_client):
        """
        Tests 'check_comments_for_duplicates' function
        """
        # Set up return values
        mock_comment = MagicMock()
        mock_comment.body = 'Marking as duplicate of TEST-1234'
        mock_comment.author.name = 'mock_user'
        mock_client.comments.return_value = [mock_comment]
        mock_client.issue.return_value = 'Successful Call!'

        # Call the function
        response = d.check_comments_for_duplicate(
            client=mock_client,
            result=self.mock_downstream,
            username='mock_user'
        )

        # Assert everything was called correctly
        self.assertEqual(response, 'Successful Call!')
        mock_client.comments.assert_called_with(self.mock_downstream)
        mock_client.issue.assert_called_with('TEST-1234')

    def test_comment_matching(self):
        """
        Tests 'comment_matching' function
        """
        # Set up return values
        mock_issue_comment1 = {'body': 'test_body'}
        mock_issue_comment2 = {'body': 'not_in_jira'}
        mock_jira_comment = MagicMock()
        mock_jira_comment.body = 'test_body'

        # Call the function
        response = d.comment_matching(
            issue_comments=[mock_issue_comment1, mock_issue_comment2],
            comments=[mock_jira_comment]
        )

        # Assert everything was called correctly
        self.assertEqual(response, [mock_issue_comment2])

    @mock.patch(PATH + 'comment_matching')
    @mock.patch('jira.client.JIRA')
    def test_check_comments(self,
                            mock_client,
                            mock_comment_matching):
        """
        Tests 'check_comments' function where we have all comments in sync
        """
        # Set up return values
        mock_client.comments.return_value = 'mock_comments'
        mock_comment_matching.return_value = []
        self.mock_issue.out_of_sync = {'comments': 'test'}

        # Call the function
        response = d.check_comments(
            existing=self.mock_downstream,
            issue=self.mock_issue,
            client=mock_client
        )

        # Assert everything was called correctly
        mock_comment_matching.assert_called_with(self.mock_issue.comments, 'mock_comments')
        self.assertEqual(response.out_of_sync['comments'], 'in-sync')

    @mock.patch(PATH + 'comment_matching')
    @mock.patch('jira.client.JIRA')
    def test_check_comments_duplicates(self,
                                       mock_client,
                                       mock_comment_matching):
        """
        Tests 'check_comments' function where we have one comment out of sync
        """
        # Set up return values
        mock_client.comments.return_value = 'mock_comments'
        mock_comment_matching.return_value = [{'author': 'mock_author',
                                               'body': 'mock_body',
                                               'date_created': 'mock_date'}]
        self.mock_issue.out_of_sync = {'comments': 'test'}

        # Call the function
        response = d.check_comments(
            existing=self.mock_downstream,
            issue=self.mock_issue,
            client=mock_client
        )

        # Assert everything was called correctly
        mock_comment_matching.assert_called_with(self.mock_issue.comments, 'mock_comments')
        self.assertEqual(response.out_of_sync['comments'][0].author, 'mock_author')
        self.assertEqual(response.out_of_sync['comments'][0].body, 'mock_body')
        self.assertEqual(response.out_of_sync['comments'][0].date_created, 'mock_date')
