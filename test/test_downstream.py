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
from jibe.intermediary import Issue

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
            'check': [
                'comments',
                'tags',
                'fixVersion',
                'assignee', 'title',
                {'transition': 'CUSTOM TRANSITION'}
            ],
            'owner': 'mock_owner'
        }
        self.mock_issue.out_of_sync = {'tags': 'in-sync',
                                       'fixVersion': 'in-sync',
                                       'assignee': 'in-sync',
                                       'title': 'in-sync',
                                       'transition': 'in-sync',
                                       'comments': 'in-sync'}
        self.mock_issue.content = 'mock_content'
        self.mock_issue.reporter = {'fullname': 'mock_user'}
        self.mock_issue.url = 'mock_url'
        self.mock_issue.title = 'mock_title'
        self.mock_issue.comments = 'mock_comments'
        self.mock_issue.tags = ['tag1', 'tag2']
        self.mock_issue.fixVersion = ['fixVersion3', 'fixVersion4']
        self.mock_issue.assignee = [{'fullname': 'mock_assignee'}]
        self.mock_issue.status = 'Closed'
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
        self.mock_downstream.fields.assignee.displayName = 'mock_assignee'
        self.mock_downstream.fields.summary = 'mock_title'
        self.mock_downstream.fields.status.name = 'CUSTOM TRANSITION'
        self.mock_downstream.key = 'mock_key'

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
        mock_client.search_issues.return_value = [mock_downstream_issue,
                                                  bad_downstream_issue]
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
        mock_comment_matching.assert_called_with(self.mock_issue.comments,
                                                 'mock_comments')
        self.assertEqual(response.out_of_sync['comments'], 'in-sync')

    @mock.patch(PATH + 'comment_matching')
    @mock.patch('jira.client.JIRA')
    def test_check_comments_out_of_sync(self,
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
        mock_comment_matching.assert_called_with(self.mock_issue.comments,
                                                 'mock_comments')
        self.assertEqual(response.out_of_sync['comments'][0].author, 'mock_author')
        self.assertEqual(response.out_of_sync['comments'][0].body, 'mock_body')
        self.assertEqual(response.out_of_sync['comments'][0].date_created, 'mock_date')

    def test_check_tags(self):
        """
        Tests 'check_tags' function where we have all tags in sync
        """
        # Set up return values
        self.mock_downstream.fields.labels = ['tag1', 'tag2']

        # Call the function
        response = d.check_tags(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['tags'], 'in-sync')

    def test_check_tags_out_of_sync(self):
        """
        Tests 'check_tags' function where we don't have all tags in sync
        """
        # Call the function
        response = d.check_tags(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['tags'],
                         {'difference': ['tag3', 'tag4', 'tag1', 'tag2'],
                          'upstream': ['tag1', 'tag2'],
                          'downstream': ['tag3', 'tag4']})

    def test_check_fixVersion(self):
        """
        Test 'check_fixVersion' function where we have all fixVersions in sync
        """
        # Call the function
        response = d.check_fixVersion(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['fixVersion'], 'in-sync')

    def test_check_fixVersion_out_of_sync(self):
        """
        Test 'check_fixVersion' function where we do not have all fixVersions in sync
        """
        # Set up return values
        self.mock_issue.fixVersion = ['fixVersion5']

        # Call the function
        response = d.check_fixVersion(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['fixVersion'],
                         {'upstream': ['fixVersion5'],
                          'downstream': ['fixVersion3', 'fixVersion4'],
                          'difference': ['fixVersion3', 'fixVersion4',
                                         'fixVersion5']})

    def test_check_assginee(self):
        """
        Test 'check_assignee' function where we have assignees in sync
        """
        # Call the function
        response = d.check_assignee(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['assignee'], 'in-sync')

    def test_check_assginee_out_of_sync(self):
        """
        Test 'check_assignee' function where we have assignees in sync
        """
        # Set up return values
        self.mock_issue.assignee = [{'fullname': 'dummy_user'}]

        # Call the function
        response = d.check_assignee(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['assignee'],
                         {'upstream': 'dummy_user',
                          'downstream': self.mock_downstream.fields.assignee})

    def test_check_title(self):
        """
        Tests 'check_title' function where we have titles in sync
        """
        # Call the function
        response = d.check_title(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['title'], 'in-sync')

    def test_check_title_out_of_sync(self):
        """
        Tests 'check_title' function where we have title out of sync
        """
        # Set up return values
        self.mock_issue.title = 'dummy_title'

        # Call the function
        response = d.check_title(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['title'], {'upstream': 'dummy_title',
                                                         'downstream': 'mock_title'})

    def test_check_transition(self):
        """
        Tests 'check_transition' function where we have transitions in sync
        """
        # Call the function
        response = d.check_transition(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['transition'], 'in-sync')

    def test_check_transition_out_of_sync_upstream(self):
        """
        Tests 'check_transition' function where we don't have transitions in sync
            * Upstream is closed
            * Downstream is open
        """
        # Set up return values
        self.mock_downstream.fields.status.name = 'Open'
        self.mock_issue.status = 'Closed'

        # Call the function
        response = d.check_transition(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['transition'],
                         {'upstream-close-downstream-open':
                              {'upstream': 'Closed', 'downstream': 'Open'}})

    def test_check_transition_out_of_sync_downstream(self):
        """
        Tests 'check_transition' function where we don't have transitions in sync
            * Upstream is Open
            * Downstream is Closed
        """
        # Set up return values
        self.mock_downstream.fields.status.name = 'CUSTOM TRANSITION'
        self.mock_issue.status = 'Open'

        # Call the function
        response = d.check_transition(self.mock_downstream, self.mock_issue)

        # Assert everything was called correctly
        self.assertEqual(response.out_of_sync['transition'],
                         {'upstream-open-downstream-close':
                              {'upstream': 'Open', 'downstream':
                                  'CUSTOM TRANSITION'}})

    @mock.patch(PATH + 'check_comments')
    @mock.patch(PATH + 'check_tags')
    @mock.patch(PATH + 'check_fixVersion')
    @mock.patch(PATH + 'check_assignee')
    @mock.patch(PATH + 'check_title')
    @mock.patch(PATH + 'check_transition')
    @mock.patch('jira.client.JIRA')
    def test_update_out_of_sync(self,
                                mock_client,
                                mock_check_transition,
                                mock_check_title,
                                mock_check_assignee,
                                mock_check_fixVersion,
                                mock_check_tags,
                                mock_check_comments):
        """
        Tests 'update_out_of_sync' function
        """
        # Set up return values
        mock_check_transition.return_value = self.mock_issue
        mock_check_title.return_value = self.mock_issue
        mock_check_assignee.return_value = self.mock_issue
        mock_check_fixVersion.return_value = self.mock_issue
        mock_check_tags.return_value = self.mock_issue
        mock_check_comments.return_value = self.mock_issue

        # Call the function
        response = d.update_out_of_sync(
            existing=self.mock_downstream,
            issue=self.mock_issue,
            client=mock_client,
            config=self.mock_config)

        # Assert everything was called correctly
        self.assertEqual(response.total, 6)
        self.assertEqual(response.done, 6)
        self.assertEqual(response.percent_done, 100)

    @mock.patch(PATH + 'get_jira_client')
    @mock.patch(PATH + 'get_existing_jira_issue')
    @mock.patch(PATH + 'update_out_of_sync')
    @mock.patch('jira.client.JIRA')
    def test_sync_with_downstream(self,
                                  mock_client,
                                  mock_update_out_of_sync,
                                  mock_get_existing_jira_issue,
                                  mock_get_jira_client):
        """
        Tests 'sync_with_downstream' function
        """
        # Set up return values
        mock_bad_issue = MagicMock()
        mock_update_out_of_sync.return_value = self.mock_issue
        mock_get_existing_jira_issue.side_effect = [self.mock_downstream, None]
        mock_get_jira_client.return_value = mock_client

        # Call the function
        out_of_sync_issues, missing_issues = d.sync_with_downstream(
            issues=[self.mock_issue, mock_bad_issue],
            config=self.mock_config
        )

        # Assert everything was called correctly
        self.assertEqual(out_of_sync_issues, [self.mock_issue])
        self.assertEqual(missing_issues, [mock_bad_issue])
        mock_get_jira_client.assert_any_call(self.mock_issue, self.mock_config)
        mock_get_jira_client.assert_any_call(mock_bad_issue, self.mock_config)
        mock_update_out_of_sync.assert_called_with(
            self.mock_downstream,
            self.mock_issue,
            mock_client,
            self.mock_config
        )



