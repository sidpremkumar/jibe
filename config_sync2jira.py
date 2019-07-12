config = {
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
    },
}