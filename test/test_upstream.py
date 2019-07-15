# Built In Modules
import mock
import unittest
try:
    # Python 3.3 >
    from unittest.mock import MagicMock  # noqa: F401
except ImportError:
    from mock import MagicMock  # noqa: F401

# Local Modules
import jibe.upstream as u

# Global Variables
PATH = 'jibe.upstream.'

class TestUpstream(unittest.TestCase):
    """
    This class test the upstream.py file under jibe
    """
    def setUp(self):
        # Mock config
        self.mock_config = {
            'jibe': {
                'send-to': {
                    'NAME_OF_GROUP': {
                        'upstream': {
                            'github': {
                                'mock_repo0': {}
                            },
                            'pagure': {
                                'mock_repo1': {}
                            }
                        }
                    }
                },
                'filters': {
                    'github':
                        {'org/repo': {'filter1': 'filter1', 'labels': 'custom_tag'}},
                    'pagure':
                        {'org/repo': {'filter1': 'filter1', 'tags': ['custom_tag']}},
                },
                'github_token': 'mock_token'
            }
        }

        # Mock Github Comment
        self.mock_github_comment = MagicMock()
        self.mock_github_comment.user.name = 'mock_username'
        self.mock_github_comment.user.login = 'mock_user_login'
        self.mock_github_comment.body = 'mock_body'
        self.mock_github_comment.id = 'mock_id'
        self.mock_github_comment.created_at = 'mock_created_at'

        # Mock github issue
        self.mock_github_issue = MagicMock()
        self.mock_github_issue.get_comments.return_value = [self.mock_github_comment]

        # Mock Github Reporter
        self.mock_github_person = MagicMock()
        self.mock_github_person.name = 'mock_name'

        # Mock Github Repo
        self.mock_github_repo = MagicMock()
        self.mock_github_repo.get_issue.return_value = self.mock_github_issue

        # Mock Github Client
        self.mock_github_client = MagicMock()
        self.mock_github_client.get_repo.return_value = self.mock_github_repo
        self.mock_github_client.get_user.return_value = self.mock_github_person

        # Mock Github Issue Raw
        self.mock_github_issue_raw = {
            'comments': ['some comment'],
            'number': '1234',
            'user': {
                'login': 'mock_login'
            },
            'assignees': [{'login': 'mock_assignee_login'}],
            'labels': [{'name': 'some_label'}],
            'milestone': {
                'title': 'mock_milestone'
            }
        }

    @mock.patch(PATH + 'pagure_issues')
    @mock.patch(PATH + 'github_issues')
    def test_get_upstream_issues(self,
                                 mock_github_issues,
                                 mock_pagure_issues):
        """
        Test 'get_upstream_issues' function
        """
        # Set up variables and return values
        mock_github_issues.return_value = '1'
        mock_pagure_issues.return_value = '1'

        # Call function
        response = u.get_upstream_issues(
            config=self.mock_config,
            group='NAME_OF_GROUP'
        )

        # Assert everything was called correctly
        mock_github_issues.assert_called_with(
            'mock_repo0',
            self.mock_config,
            'NAME_OF_GROUP'
        )
        mock_pagure_issues.assert_called_with(
            'mock_repo1',
            self.mock_config,
            'NAME_OF_GROUP'
        )
        self.assertEqual(response, ['1', '1'])

    @mock.patch('jibe.intermediary.Issue.from_github')
    @mock.patch(PATH + 'Github')
    @mock.patch(PATH + '_get_all_github_issues')
    def test_github_issues(self,
                           mock_get_all_github_issues,
                           mock_github,
                           mock_issue_from_github):
        """
        This function tests 'github_issues' function
        """
        # Set up return values
        mock_github.return_value = self.mock_github_client
        mock_get_all_github_issues.return_value = [self.mock_github_issue_raw]
        mock_issue_from_github.return_value = 'Successful Call!'

        # Call the function
        response = list(u.github_issues(
            upstream='org/repo',
            config=self.mock_config,
            group='NAME_OF_GROUP'
        ))

        # Assert that calls were made correctly
        try:
            mock_get_all_github_issues.assert_called_with(
                'https://api.github.com/repos/org/repo/issues?labels=custom_tag&filter1=filter1',
                {'Authorization': 'token mock_token'}
            )
        except AssertionError:
            mock_get_all_github_issues.assert_called_with(
                'https://api.github.com/repos/org/repo/issues?filter1=filter1&labels=custom_tag',
                {'Authorization': 'token mock_token'}
            )
        self.mock_github_client.get_user.assert_any_call('mock_login')
        self.mock_github_client.get_user.assert_any_call('mock_assignee_login')
        mock_issue_from_github.assert_called_with(
            'org/repo',
            {'labels': ['some_label'], 'number': '1234', 'comments': [
                {'body': 'mock_body', 'name': 'mock_user_login', 'author': 'mock_username', 'changed': None,
                 'date_created': 'mock_created_at', 'id': 'mock_id'}], 'assignees': [{'fullname': 'mock_name'}],
             'user': {'login': 'mock_login', 'fullname': 'mock_name'}, 'milestone': 'mock_milestone'},
            self.mock_config,
            'NAME_OF_GROUP'
        )
        self.mock_github_client.get_repo.assert_called_with('org/repo')
        self.mock_github_repo.get_issue.assert_called_with(number='1234')
        self.mock_github_issue.get_comments.assert_any_call()
        self.assertEqual(response[0], 'Successful Call!')

    @mock.patch('jibe.intermediary.Issue.from_github')
    @mock.patch(PATH + 'Github')
    @mock.patch(PATH + '_get_all_github_issues')
    def test_github_issues_no_token(self,
                                    mock_get_all_github_issues,
                                    mock_github,
                                    mock_issue_from_github):
        """
        This function tests 'github_issues' function where we have no github token
        and no comments
        """
        # Set up return values
        self.mock_config['jibe']['github_token'] = None
        self.mock_github_issue_raw['comments'] = 0
        mock_github.return_value = self.mock_github_client
        mock_get_all_github_issues.return_value = [self.mock_github_issue_raw]
        mock_issue_from_github.return_value = 'Successful Call!'

        # Call the function
        response = list(u.github_issues(
            upstream='org/repo',
            config=self.mock_config,
            group='NAME_OF_GROUP'
        ))

        # Assert that calls were made correctly
        try:
            mock_get_all_github_issues.assert_called_with(
                'https://api.github.com/repos/org/repo/issues?labels=custom_tag&filter1=filter1',
                {}
            )
        except AssertionError:
            mock_get_all_github_issues.assert_called_with(
                'https://api.github.com/repos/org/repo/issues?filter1=filter1&labels=custom_tag',
                {}
            )
        self.mock_github_client.get_user.assert_any_call('mock_login')
        self.mock_github_client.get_user.assert_any_call('mock_assignee_login')
        mock_issue_from_github.assert_called_with(
            'org/repo',
            {'labels': ['some_label'], 'number': '1234', 'comments': [], 'assignees': [{'fullname': 'mock_name'}],
             'user': {'login': 'mock_login', 'fullname': 'mock_name'}, 'milestone': 'mock_milestone'},
            self.mock_config,
            'NAME_OF_GROUP'
        )
        self.assertEqual(response[0], 'Successful Call!')
        self.mock_github_client.get_repo.assert_not_called()
        self.mock_github_repo.get_issue.assert_not_called()
        self.mock_github_issue.get_comments.assert_not_called()

    @mock.patch('jibe.intermediary.Issue.from_pagure')
    @mock.patch(PATH + 'requests')
    def test_pagure_issues_error(self,
                                 mock_requests,
                                 mock_issue_from_pagure):
        """
        This function tests 'pagure_issues' function where we get an IOError
        """
        # Set up return values
        get_return = MagicMock()
        get_return.__bool__ = mock.Mock(return_value=False)
        get_return.__nonzero__ = get_return.__bool__
        get_return.json.side_effect = Exception()
        get_return.text.return_value = {
            'issues': [
                {'assignee': 'mock_assignee'}
            ]

        }
        mock_requests.get.return_value = get_return

        # Call the function
        with self.assertRaises(IOError):
            list(u.pagure_issues(
                upstream='org/repo',
                config=self.mock_config,
                group='NAME_OF_GROUP'
            ))

        # Assert everything was called correctly
        mock_requests.get.assert_called_with(
            'https://pagure.io/api/0/org/repo/issues',
            params={'filter1': 'filter1', 'tags': ['custom_tag']}
        )
        mock_issue_from_pagure.assert_not_called()

    @mock.patch('jibe.intermediary.Issue.from_pagure')
    @mock.patch(PATH + 'requests')
    def test_pagure_issues(self,
                           mock_requests,
                           mock_issue_from_pagure):
        """
        This function tests 'pagure_issues' function
        """
        # Set up return values
        get_return = MagicMock()
        get_return.json.return_value = {
            'issues': [
                {'assignee': 'mock_assignee'}
            ]

        }
        get_return.request.url = 'mock_url'
        mock_requests.get.return_value = get_return
        mock_issue_from_pagure.return_value = 'Successful Call!'

        # Call the function
        response = list(u.pagure_issues(
            upstream='org/repo',
            config=self.mock_config,
            group='NAME_OF_GROUP'
        ))

        # Assert everything was called correctly
        self.assertEqual(response[0], 'Successful Call!')
        mock_requests.get.assert_called_with(
            'https://pagure.io/api/0/org/repo/issues',
            params={'filter1': 'filter1', 'tags': ['custom_tag']}
        )
        mock_issue_from_pagure.assert_called_with(
            'org/repo',
            {'assignee': ['mock_assignee']},
            self.mock_config,
            'NAME_OF_GROUP'
        )