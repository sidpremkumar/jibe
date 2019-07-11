# Jibe 💃

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