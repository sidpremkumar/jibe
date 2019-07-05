config = {
    'jibe': {
        # Don't actually make changes to JIRA...
        'testing': False,

        'legacy_matching': False,

        'default_jira_instance': 'example',

        'jira': {
           'example': {
               'options': {
                   'server': 'https://projects.devel.engineering.redhat.com',
                   'verify': False,
               },
               'basic_auth': ('spremkum', 'wnmquh6d'),
           },
        },

        'upstream': {
            'pagure': {
                'Demo_project': {'project': 'FACTORY', 'component': 'gitbz',
                                 'check': ['comments', 'tags', 'fixVersion', 'assignee', 'title',
                                           {'transition': 'CUSTOM_CLOSED_STATUS'}]},
                #'koji': { 'project': 'BREW', 'component': None, },
            },
            'github': {
                'sidpremkumar/Demo_project': {'project': 'FACTORY', 'component': 'gitbz',
                                              'check': ['comments', 'tags', 'fixVersion', 'assignee', 'title',
                                                        {'transition': 'CUSTOM_CLOSED_STATUS'}]},
            },
        },
        'github_token': '***'
    },
}