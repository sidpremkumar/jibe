# Built In Modules
import mock
import unittest
try:
    # Python 3.3 >
    from unittest.mock import MagicMock  # noqa: F401
except ImportError:
    from mock import MagicMock  # noqa: F401

# Local Modules
import jibe.intermediary as i

# Global Variables
PATH = 'jibe.intermediary.'


class TestIntermediary(unittest.TestCase):
    """
    This Class tests the intermediary.py function under jibe
    """

    def setUp(self):
        self.mock_config = {
            'jibe': {
                'pagure_url': 'dummy_pagure_url',
                'map': {
                    'pagure': {
                        'pagure': 'mock_downstream'
                    },
                    'github': {
                        'github': 'mock_downstream'
                    }
                },
                'send-to': {
                    'NAME_OF_GROUP': {
                        'upstream': {
                            'github': {
                                'github': 'mock_downstream'
                            },
                            'pagure': {
                                'pagure': 'mock_downstream'
                            }
                        }
                    }
                }
            }
        }

    @mock.patch(PATH + 'datetime')
    def test_from_pagure(self,
                         mock_datetime):
        """
        This tests the 'from_pagure' function under the Issue class
        """
        # Set up return values
        mock_datetime.utcfromtimestamp.return_value = 'mock_date'
        mock_issue = {
            'comments': [{
                'date_created': '1234',
                'user': {
                    'name': 'mock_name'
                },
                'comment': 'mock_body',
                'id': '1234',
            }],
            'title': 'mock_title',
            'id': 1234,
            'tags': 'mock_tags',
            'milestone': 'mock_milestone',
            'priority': 'mock_priority',
            'content': 'mock_content',
            'user': 'mock_reporter',
            'assignee': 'mock_assignee',
            'status': 'mock_status',
            'date_created': 'mock_date'
        }

        # Call the function
        response = i.Issue.from_pagure(
            upstream='pagure',
            issue=mock_issue,
            config=self.mock_config,
            group='NAME_OF_GROUP'
        )

        # Assert that we made the calls correctly
        self.assertEqual(response.source, 'pagure')
        self.assertEqual(response.title, 'mock_title')
        self.assertEqual(response.url, 'dummy_pagure_url/pagure/issue/1234')
        self.assertEqual(response.upstream, 'pagure')
        self.assertEqual(response.comments, [{'body': 'mock_body', 'name': 'mock_name',
                                              'author': 'mock_name', 'changed': None,
                                              'date_created': 'mock_date', 'id': '1234'}])
        self.assertEqual(response.tags, 'mock_tags')
        self.assertEqual(response.fixVersion, ['mock_milestone'])
        self.assertEqual(response.priority, 'mock_priority')
        self.assertEqual(response.content, 'mock_content')
        self.assertEqual(response.reporter, 'mock_reporter')
        self.assertEqual(response.assignee, 'mock_assignee')
        self.assertEqual(response.status, 'mock_status')
        self.assertEqual(response.id, 'mock_date')
        self.assertEqual(response.downstream, 'mock_downstream')
        self.assertEqual(response.out_of_sync, {'comments': 'in-sync', 'tags': 'in-sync',
                                                'fixVersion': 'in-sync', 'assignee': 'in-sync',
                                                'title': 'in-sync', 'transition': 'in-sync'})

    def test_from_github(self):
        """
        This tests the 'from_github' function under the Issue class
        """
        # Set up return values
        mock_issue = {
            'comments': [{
                'author': 'mock_author',
                'name': 'mock_name',
                'body': 'mock_body',
                'id': 'mock_id',
                'date_created': 'mock_date'
            }],
            'title': 'mock_title',
            'html_url': 'mock_url',
            'id': 1234,
            'labels': 'mock_tags',
            'milestone': 'mock_milestone',
            'priority': 'mock_priority',
            'body': 'mock_content',
            'user': 'mock_reporter',
            'assignees': 'mock_assignee',
            'state': 'open',
            'date_created': 'mock_date'
        }

        # Call the function
        response = i.Issue.from_github(
            upstream='github',
            issue=mock_issue,
            config=self.mock_config,
            group='NAME_OF_GROUP'
        )

        # Assert that we made the calls correctly
        self.assertEqual(response.source, 'github')
        self.assertEqual(response.title, 'mock_title')
        self.assertEqual(response.url, 'mock_url')
        self.assertEqual(response.upstream, 'github')
        self.assertEqual(response.comments, [{'body': 'mock_body', 'name': 'mock_name', 'author': 'mock_author',
                                              'changed': None, 'date_created': 'mock_date', 'id': 'mock_id'}])
        self.assertEqual(response.tags, 'mock_tags')
        self.assertEqual(response.fixVersion, ['mock_milestone'])
        self.assertEqual(response.priority, None)
        self.assertEqual(response.content, 'mock_content')
        self.assertEqual(response.reporter, 'mock_reporter')
        self.assertEqual(response.assignee, 'mock_assignee')
        self.assertEqual(response.status, 'Open')
        self.assertEqual(response.id, '1234')
        self.assertEqual(response.downstream, 'mock_downstream')
        self.assertEqual(response.out_of_sync, {'comments': 'in-sync', 'tags': 'in-sync',
                                                'fixVersion': 'in-sync', 'assignee': 'in-sync',
                                                'title': 'in-sync', 'transition': 'in-sync'})
