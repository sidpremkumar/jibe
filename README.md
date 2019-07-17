<h1 align="center"> Jibe 💃 </h1>

## What it does? 
Jibe is a program that can be used to track if upstream issues (i.e. issues on github, pagure, etc) are 
in sync with downstream issues (i.e. on JIRA).

Once configured, wth one command users can send a 'Jibe report' of issues out-of-sync to a email list.

## Installation 
For use:
```
python setup.py install 
```
For development: 
```
python setup.py develop 
```
Set up Mailer by setting the following environmental variables: 

1. `export DEFAULT_FROM="Email address used to send emails"`
2. `export DEFAULT_SERVER="Mail server to be used"`

## Script
To configure emails. Please add the appropriate `DEFAULT_FROM` and `DEFAULT_SERVER` in [mailer.py](jibe/mailer.py)
```shell
> jibe --help 

optional arguments:
  -h, --help            show this help message and exit
  --sync2jira           Parse sync2jira config file instead 
  --link-issue FACTORY-XXX some_url.com
                        Add remote link to downstream issues
  --ignore-in-sync      Omit issues that are in sync from report
```

`--sync2jira`: This argument can be added to parse JIRA data from a [sync2jira](https://pagure.io/sync-to-jira) config 
file. Copy the contents into the Jibe directory and set up [config_sync2jira.py](config_sync2jira.py). Rename the file 
to sync2jira_config.py and you should be all set. 


`--link-issue`: This argument takes two values: Downstream issue ID and upstream URL. To link a downstream and upstream
issue users can use this command **and** ensure the titles of the issues are the same. 

`--ignore-in-sync`: This argument will omit all in-sync issues from Jibe report
## Tests 
Tests are run through the tox automation project
```shell
tox
```
They are automatically run against Python 3.7. HTML coverage files can be found under [htmlcov-py36](htmlcov-py36).
## Configuration 
You can edit the `config.py` file to add an email list and relevant checks. A sample config file 
can be found [here](config.py)

The way Jibe matches issues downstream is through a remote link and title matching. That means if you want to link 
a upstream issue to a downstream Jira ticket all you have to do is: 
1. Add the upstream issue link to the 'remote links' field on Jira
2. Ensure the titles of the upstream/downstream issues match

Note: The `NAME_OF_GROUP` field will be what is used for the subject of the email 

Do you like dad jokes? Add `fun: True` under 'NAME_OF_GROUP'

## Adding New Upstream Repos 
Have you ever wanted to use Jibe on a different git repository? Now you can!

Jibe is set up to easily add new git repos:
1. Edit [intermediary.py](jibe/intermediary.py) to create a new classmethod for your git repo. You can use 
`from_pagure` as an example. 
1. Edit [upstream.py](jibe/upstream.py) by adding a new function that generates intermediate issue objects 
from an upstream repo. You can use `pagure_issues` as an example. 
1. Edit the function `get_upstream_issues` in [upstream.py](jibe/upstream.py) to append the newly created issues 
to the `all_issues` list
1. You're all done! Now you should be able to add the repo to the config file 🤠
1. *Note:* If you want to submit a PR, please add appropriate tests. 
