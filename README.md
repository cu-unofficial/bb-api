## bb-api

An experimental API for blackboard.

## Installation

You need to have Python 3 installed on your system. Python 2 might work but we won't provide any
support for it. You also need to have the command-line version for [git](https://git-scm.com/downloads)
installed, otherwise you could directly download and extract the ZIP file of this repository and follow
along.

Open up a terminal and run:
(The `$` sign indicates the commands are to be run in a shell. It is not supposed to be a part of
the command)

```
$ git clone https://github.com/cu-unofficial/bb-api
$ cd bb-api
$ pip install -e .
```

## Usage Examples

```python
from bb_api import SessionBlackBoard

me = SessionBlackBoard("UID", "PASSWORD")

for course in me.courses:
    print(course.course["displayName"])
    session = course.next_session()
    if session is not None:
        # Teacher has a future online session scheduled
        url = session.join().get("url")
        if url is not None:
            # Session is active right now.
            # Session only goes active 15 minutes prior to the class start
            # time and stays active until the end of class.
            print(url)
            # This URL allows you to join the on-going online session/class.
            # Also, this is a standalone URL which means it can be
            # opened direcly in a webbrowser and can be used to attend
            # the class without ever having to log into your blackboard.
```

