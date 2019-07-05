
class Issue(object):
    def __init__(self, source, title, url, upstream, comments,
                 config, tags, fixVersion, priority, content,
                 reporter, assignee, status, id, downstream=None):
        self.source = source
        self.title = title
        self.url = url
        self.upstream = upstream
        self.comments = comments
        self.tags = tags
        self.fixVersion = fixVersion
        self.priority = priority
        self.content = content
        self.reporter = reporter
        self.assignee = assignee
        self.status = status
        self.id = id
        self.downstream_url = ''
        self.downstream_id = ''
        self.out_of_sync = {'comments': 'in-sync', 'tags': 'in-sync', 'fixVersion': 'in-sync',
                            'assignee': 'in-sync', 'title': 'in-sync', 'transition': 'in-sync'}
        if not downstream:
            self.downstream = config['jibe']['upstream'][self.source][upstream]
        else:
            self.downstream = downstream

    @classmethod
    def from_github(cls, upstream, issue, config):
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

        # TODO: Priority is broken
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
            content=issue['body'],
            reporter=issue['user'],
            assignee=issue['assignees'],
            status=issue['state'],
            id=issue['id']
        )

    def __repr__(self):
        return "<Issue %s >" % self.url


class Comment(object):
    def __init__(self, author, body, date_created):
        self.author = author
        self.body = body
        self.date_created = date_created
