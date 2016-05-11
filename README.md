# grpy
grpy is a work-in-progress Python port of [gr](https://github.com/mixu/gr), a tool for interacting with multiple git repositories at once.

## Installation
```sh
$ sudo apt-get install libgit2-dev
$ pip install -r requirements.txt
$ cp grconfig.json.example ~/.grconfig.json
$ $EDITOR ~/.grconfig.json
```
## Usage
- List repositories: python grpy.py
- Tags and arbitrary commands are not yet supported 
