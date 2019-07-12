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

## Tests 
Coming soon

## Configuration 
You can edit the `config.py` file to add an email list and relevant checks. A sample config file 
can be found [here](config.py)

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
1. You're all done! Now you should be able to add the repo to the config file :) 