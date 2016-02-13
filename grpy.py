import pygit2

repo = pygit2.Repository('/home/andrew/dev/grpy')

modified = len(repo.status())

'git status --branch --porcelain'
