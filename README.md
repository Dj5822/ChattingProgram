# Python Chatting Program

Note that this program was designed to be used on Linux.
You need to use WSL on Windows to run this program.

## Prerequisites

- Python 3
- uv

1) Run: `uv sync`
2) Run: `uv run python3 server.py`
3) Run the following command twice: `uv run python3 client.py`

Every time you execute `uv run python client.py` you will create a new client.
You may choose to execute this command as many times as you want.

4) Enter in the following details:
```
IP Address: localhost 
Port: 9988
Nickname: [SomeUniqueName]
```

Where [SomeUniqueName] is a name that is unique.
