# Built In Modules
from datetime import datetime


class Issue(object):
    def __init__(self, source, title, url, upstream, comments,
                 config, tags, fixVersion, priority, priority_icon,
                 content, reporter, assignee, status, id, group,
                 downstream=None):
        self.source = source
        self.title = title
        self.url = url
        self.upstream = upstream
        self.comments = comments
        self.tags = tags
        self.fixVersion = fixVersion
        self.priority = priority
        self.priority_icon = priority_icon
        self.content = content
        self.reporter = reporter
        self.assignee = assignee
        self.status = status
        self.id = str(id)
        self.downstream_url = ''
        self.downstream_id = ''
        self.percent_done = ''
        self.done = ''
        self.total = ''
        self.check = []
        self.out_of_sync = {'comments': 'in-sync', 'tags': 'in-sync', 'fixVersion': 'in-sync',
                            'assignee': 'in-sync', 'title': 'in-sync', 'transition': 'in-sync'}
        if not downstream:
            self.downstream = config['jibe']['send-to'][group]['upstream'][self.source][upstream]
        else:
            self.downstream = downstream

    @property
    def upstream_title(self):
        return u'[%s] %s' % (self.upstream, self.title)

    @classmethod
    def from_github(cls, upstream, issue, config, group):
        comments = []
        for comment in issue['comments']:
            comments.append({
                'author': comment['author'],
                'name': comment['name'],
                'body': comment['body'],
                'id': comment['id'],
                'date_created': comment['date_created'],
                'changed': None
            })

        # Reformat the state field
        if issue['state']:
            if issue['state'] == 'open':
                issue['state'] = 'Open'
            elif issue['state'] == 'closed':
                issue['state'] = 'Closed'

        return Issue(
            source='github',
            title=issue['title'],
            url=issue['html_url'],
            upstream=upstream,
            config=config,
            comments=comments,
            tags=issue['labels'],
            fixVersion=[issue['milestone']],
            priority=None,
            priority_icon=None,
            content=issue['body'],
            reporter=issue['user'],
            assignee=issue['assignees'],
            status=issue['state'],
            id=issue['id'],
            group=group
        )

    @classmethod
    def from_pagure(cls, upstream, issue, config, group):
        base = config['jibe'].get('pagure_url', 'https://pagure.io')
        comments = []
        for comment in issue['comments']:
            # Only add comments that are not Metadata updates
            if '**Metadata Update' in comment['comment']:
                continue
            # Else add the comment
            # Convert the date to datetime
            comment['date_created'] = datetime.utcfromtimestamp(float(comment['date_created']))
            comments.append({
                'author': comment['user']['name'],
                'body': comment['comment'],
                'name': comment['user']['name'],
                'id': comment['id'],
                'date_created': comment['date_created'],
                'changed': None
            })

        return Issue(
            source='pagure',
            title=issue['title'],
            url=base + '/%s/issue/%i' % (upstream, issue['id']),
            upstream=upstream,
            config=config,
            comments=comments,
            tags=issue['tags'],
            fixVersion=[issue['milestone']],
            priority=issue['priority'],
            priority_icon=None,
            content=issue['content'],
            reporter=issue['user'],
            assignee=issue['assignee'],
            status=issue['status'],
            id=issue['date_created'],
            group=group
        )

    def __repr__(self):
        return "<Issue %s >" % self.url


class Comment(object):
    def __init__(self, author, body, date_created):
        self.author = author
        self.body = body
        self.date_created = date_created
