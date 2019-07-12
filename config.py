config = {
    'jibe': {
        # Your Github token
        'github_token': 'GITHUB_TOKEN',

        # Defualt JIRA instance to use of none is provided
        'default_jira_instance': 'example',

        'jira': {
           'example': {
               'options': {
                   'server': 'SOME_JIRA_SERVER',
                   'verify': True,
               },
               'basic_auth': ('USERNAME', 'PASSWORD'),
           },
        },

        'send-to': {
            'NAME_OF_GROUP': {
                'upstream': {
                    'pagure': {
                        # 'Demo_project': {'check': ['comments', 'tags', 'fixVersion', 'assignee', 'title',
                        #                            {'transition': 'CUSTOM_CLOSED_STATUS'}]},
                    },
                    'github': {
                        # 'Demo_username/Demo_project': {'check': ['comments', 'tags', 'fixVersion', 'assignee',
                        #                                           'title', {'transition': 'CUSTOM_CLOSED_STATUS'}]},
                    },
                },
                'email-to': ['SOME_EMAIL_LIST'],
                #'fun': True
                },
            },
        },
    }