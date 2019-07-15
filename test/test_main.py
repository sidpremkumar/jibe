# Built In Modules
import mock
import unittest
try:
    # Python 3.3 >
    from unittest.mock import MagicMock  # noqa: F401
except ImportError:
    from mock import MagicMock  # noqa: F401

# Local Modules
import jibe.main as m

# Global Variables
PATH = 'jibe.main.'


class TestMain(unittest.TestCase):
    """
    This class tests main.py under jibe
    """
    def setUp(self):
        self.mock_sync2jira_config = {
            'sync2jira': {
                # Admins to be cc'd in duplicate emails
                'admins': ['demo_email@demo.com'],

                # Scrape sources at startup
                'initialize': True,

                # Listen on the message bus
                'listen': True,

                # Don't actually make changes to JIRA...
                'testing': True,

                # Your Github token
                'github_token': 'YOUR_TOKEN',

                'legacy_matching': False,

                'default_jira_instance': 'example',
                'jira': {
                    'example': {
                        'options': {
                            'server': 'https://some_jira_server_somewhere.com',
                            'verify': True,
                        },
                        'basic_auth': ('YOU_USERNAME', 'YOUR_PASSWORD'),
                    },
                },

                'map': {
                    'pagure': {
                        'Demo_project': {'project': 'FACTORY', 'component': 'gitbz',
                                         'updates': ['test']},
                        # 'koji': { 'project': 'BREW', 'component': None, },
                    },
                    'github': {
                        'GITHUB_USERNAME/Demo_project': {'project': 'FACTORY', 'component': 'gitbz',
                                                         'updates': ['test']},
                    },
                },
                'filters': {
                    'github': {
                        # Only sync multi-type tickets from bodhi.
                        'fedora-infra/bodhi': {'state': 'open', 'milestone': 4, },
                    },
                }
            },
        }
        self.mock_config_sync2jira = {
            'jibe': {
                'send-to': {
                    'NAME_OF_GROUP': {
                        'email-to': ['SOME_EMAIL_LIST'],
                        'projects': ['PROJECT_IN_SYNC2JIRA_CONFIG'],
                        'check': ['comments', 'tags', 'fixVersion', 'assignee', 'title',
                                  {'transition': 'CUSTOM_CLOSED_STATUS'}],
                        # 'fun': True
                    }
                }
            }
        }

        self.mock_config = {
            'jibe': {
                'default_jira_instance': 'mock_default_jira',
                'jira': {
                    'mock_default_jira': {'test_get_jira': 'test'}
                },
                'send-to': {
                    'NAME_OF_GROUP': {
                        'email-to': ['mock_email']
                    }
                }
            }
        }

    @mock.patch(PATH + 'load_config_files')
    def test_load_sync2jira_config(self,
                                   load_config_files):
        """
        Tests load_sync2jira_config function
        """
        # Set up return values
        load_config_files.return_value = self.mock_config_sync2jira, self.mock_sync2jira_config,

        # Call the function
        response = m.load_sync2jira_config()

        # Assert everything was called correctly
        self.assertEqual(response, {'jibe': {'jira': {'example':
                                                          {'options':
                                                               {'verify': True, 'server':
                                                                          'https://some_jira_server_somewhere.com'},
                                                                  'basic_auth': ('YOU_USERNAME', 'YOUR_PASSWORD')}},
                                             'default_jira_instance': 'example', 'github_token': 'YOUR_TOKEN',
                                             'send-to': {'NAME_OF_GROUP': {'fun': {}, 'email-to': ['SOME_EMAIL_LIST'],
                                                                           'upstream': {'pagure': {},
                                                                                        'github': {}}}}}})

    @mock.patch(PATH + 'datetime')
    @mock.patch(PATH + 'jinja2')
    def test_create_html_no_joke(self,
                                 mock_jinja2,
                                 mock_datetime):
        """
        Tests 'create_html' function with no joke
        """
        # Set up return values
        mock_jinja2.FileSystemLoader.return_value = 'mock_templateLoader'
        mock_template = MagicMock()
        mock_template.render.return_value = 'mock_render'
        mock_templateEnv = MagicMock()
        mock_templateEnv.get_template.return_value = mock_template
        mock_jinja2.Environment.return_value = mock_templateEnv
        mock_datetime_now = MagicMock()
        mock_datetime_now.strftime.return_value = 'mock_now'
        mock_datetime.now.return_value = mock_datetime_now

        # Call the function
        response = m.create_html(
            out_of_sync_issues=['out_of_sync'],
            missing_issues=['missing_issues'],
            joke=''
        )

        # Assert everything was called correctly
        mock_jinja2.FileSystemLoader.assert_called_with(searchpath='./jibe/')
        mock_jinja2.Environment.assert_called_with(loader='mock_templateLoader')
        mock_templateEnv.get_template.assert_called_with("html_template.jinja")
        mock_datetime_now.strftime.assert_called_with('%Y-%m-%d')
        mock_template.render.assert_called_with({'out_of_sync_issues': ['out_of_sync'],
                                                 'now': 'mock_now',
                                                 'missing_issues': ['missing_issues']})
        self.assertEqual(response, 'mock_render')

    @mock.patch(PATH + 'datetime')
    @mock.patch(PATH + 'jinja2')
    def test_create_html_with_joke(self,
                                   mock_jinja2,
                                   mock_datetime):
        """
        Tests 'create_html' function with joke
        """
        # Set up return values
        mock_jinja2.FileSystemLoader.return_value = 'mock_templateLoader'
        mock_template = MagicMock()
        mock_template.render.return_value = 'mock_render'
        mock_templateEnv = MagicMock()
        mock_templateEnv.get_template.return_value = mock_template
        mock_jinja2.Environment.return_value = mock_templateEnv
        mock_datetime_now = MagicMock()
        mock_datetime_now.strftime.return_value = 'mock_now'
        mock_datetime.now.return_value = mock_datetime_now

        # Call the function
        response = m.create_html(
            out_of_sync_issues=['out_of_sync'],
            missing_issues=['missing_issues'],
            joke='test'
        )

        # Assert everything was called correctly
        mock_jinja2.FileSystemLoader.assert_called_with(searchpath='./jibe/')
        mock_jinja2.Environment.assert_called_with(loader='mock_templateLoader')
        mock_templateEnv.get_template.assert_called_with("html_template.jinja")
        mock_datetime_now.strftime.assert_called_with('%Y-%m-%d')
        mock_template.render.assert_called_with({'out_of_sync_issues': ['out_of_sync'],
                                                 'now': 'mock_now',
                                                 'missing_issues': ['missing_issues'],
                                                 'joke': 'test'})
        self.assertEqual(response, 'mock_render')

    @mock.patch('jira.client.JIRA')
    def test_attach_link_helper(self,
                                mock_client):
        """
        Tests 'attach_link_helper' function
        """
        # Set up return values
        mock_downstream = MagicMock()
        mock_downstream.key = 'mock_key'
        mock_downstream.id = 'mock_id'
        mock_downstream.fields.description = 'test'

        # Call the function
        response = m.attach_link_helper(
            client=mock_client,
            downstream=mock_downstream,
            remote_link='mock_remote_link')

        # Assert everything was called correctly
        mock_client.add_remote_link.assert_called_with('mock_id', 'mock_remote_link')
        mock_downstream.update.assert_called_with({'description': 'test '})
        self.assertEqual(mock_downstream, response)

    @mock.patch(PATH + 'attach_link_helper')
    @mock.patch('jira.client.JIRA')
    def test_attach_link(self,
                         mock_client,
                         mock_attach_link_helper):
        """
        Tests 'attach_link' function
        """
        # Set up return values
        mock_client().issue.return_value = 'mock_downstream'
        mock_attach_link_helper.return_value = True


        # Call the function
        m.attach_link(
            issue_id='mock_issue_id',
            url='mock_url',
            config=self.mock_config
        )

        # Assert everything was called correctly
        mock_client().issue.assert_called_with('mock_issue_id')
        mock_attach_link_helper.assert_called_with(
            mock_client(),
            'mock_downstream',
            {'url': 'mock_url', 'title': 'Upstream issue'}
        )

    @mock.patch(PATH + 'attach_link')
    @mock.patch(PATH + 'load_sync2jira_config')
    @mock.patch(PATH + 'm.send')
    @mock.patch(PATH + 'create_html')
    @mock.patch(PATH + 'format_check')
    @mock.patch(PATH + 'd.sync_with_downstream')
    @mock.patch(PATH + 'u.get_upstream_issues')
    @mock.patch(PATH + 'load_config')
    @mock.patch(PATH + 'parse_args')
    def test_main(self,
                  mock_parse_args,
                  mock_load_config,
                  mock_get_upstream_issues,
                  mock_sync_with_downstream,
                  mock_format_check,
                  mock_create_html,
                  mock_m_send,
                  mock_load_sync2jira_config,
                  mock_attach_link):
        """
        Test 'main' function with no parameters
        """
        # Set up return values
        mock_args = MagicMock()
        mock_args.sync2jira = False
        mock_args.link_issue = False
        mock_args.ignore_in_sync = False
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.mock_config
        mock_get_upstream_issues.return_value = 'mock_issues'
        mock_sync_with_downstream.return_value = ('mock_out_of_sync', 'mock_out_of_sync')
        mock_create_html.return_value = 'mock_html'

        # Call the function
        m.main()

        # Assert everything was called correctly
        mock_get_upstream_issues.assert_called_with(self.mock_config, 'NAME_OF_GROUP')
        mock_sync_with_downstream.assert_called_with('mock_issues', self.mock_config)
        mock_format_check.assert_called_with('mock_out_of_sync')
        mock_m_send.assert_called_with(['mock_email'], 'Jibe Report for NAME_OF_GROUP', 'mock_html')
        mock_load_sync2jira_config.assert_not_called()
        mock_load_config.assert_any_call()
        mock_attach_link.assert_not_called()

    @mock.patch(PATH + 'attach_link')
    @mock.patch(PATH + 'load_sync2jira_config')
    @mock.patch(PATH + 'm.send')
    @mock.patch(PATH + 'create_html')
    @mock.patch(PATH + 'format_check')
    @mock.patch(PATH + 'd.sync_with_downstream')
    @mock.patch(PATH + 'u.get_upstream_issues')
    @mock.patch(PATH + 'load_config')
    @mock.patch(PATH + 'parse_args')
    def test_main_sync2jira(self,
                            mock_parse_args,
                            mock_load_config,
                            mock_get_upstream_issues,
                            mock_sync_with_downstream,
                            mock_format_check,
                            mock_create_html,
                            mock_m_send,
                            mock_load_sync2jira_config,
                            mock_attach_link):
        """
        Test 'main' function where we load from sync2jira config file
        """
        # Set up return values
        mock_args = MagicMock()
        mock_args.sync2jira = True
        mock_args.link_issue = False
        mock_args.ignore_in_sync = False
        mock_parse_args.return_value = mock_args
        mock_load_sync2jira_config.return_value = self.mock_config
        mock_get_upstream_issues.return_value = 'mock_issues'
        mock_sync_with_downstream.return_value = ('mock_out_of_sync', 'mock_out_of_sync')
        mock_create_html.return_value = 'mock_html'

        # Call the function
        m.main()

        # Assert everything was called correctly
        mock_get_upstream_issues.assert_called_with(self.mock_config, 'NAME_OF_GROUP')
        mock_sync_with_downstream.assert_called_with('mock_issues', self.mock_config)
        mock_format_check.assert_called_with('mock_out_of_sync')
        mock_m_send.assert_called_with(['mock_email'], 'Jibe Report for NAME_OF_GROUP', 'mock_html')
        mock_load_sync2jira_config.assert_any_call()
        mock_load_config.assert_not_called()
        mock_attach_link.assert_not_called()

    @mock.patch(PATH + 'attach_link')
    @mock.patch(PATH + 'load_sync2jira_config')
    @mock.patch(PATH + 'm.send')
    @mock.patch(PATH + 'create_html')
    @mock.patch(PATH + 'format_check')
    @mock.patch(PATH + 'd.sync_with_downstream')
    @mock.patch(PATH + 'u.get_upstream_issues')
    @mock.patch(PATH + 'load_config')
    @mock.patch(PATH + 'parse_args')
    def test_main_sync2jira(self,
                            mock_parse_args,
                            mock_load_config,
                            mock_get_upstream_issues,
                            mock_sync_with_downstream,
                            mock_format_check,
                            mock_create_html,
                            mock_m_send,
                            mock_load_sync2jira_config,
                            mock_attach_link):
        """
        Test 'main' function where we load from sync2jira config file
        """
        # Set up return values
        mock_args = MagicMock()
        mock_args.sync2jira = False
        mock_args.link_issue = ['mock_id', 'mock_url']
        mock_args.ignore_in_sync = False
        mock_parse_args.return_value = mock_args
        mock_load_config.return_value = self.mock_config
        mock_get_upstream_issues.return_value = 'mock_issues'
        mock_sync_with_downstream.return_value = ('mock_out_of_sync', 'mock_out_of_sync')
        mock_create_html.return_value = 'mock_html'

        # Call the function
        m.main()

        # Assert everything was called correctly
        mock_attach_link.assert_called_with('mock_id', 'mock_url', self.mock_config)
        mock_get_upstream_issues.assert_not_called()
        mock_sync_with_downstream.assert_not_called()
        mock_format_check.assert_not_called()
        mock_m_send.assert_not_called()
        mock_load_config.assert_any_call()
        mock_load_sync2jira_config.assert_not_called()