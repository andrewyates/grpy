import pygit2

repo = pygit2.Repository('/home/andrew/dev/grpy')

modified = len(repo.status())
ahead, behind = repo.ahead_behind(repo.head.target, repo.lookup_branch('master').upstream.target)

print "%s modified, %s ahead, %s behind" % (modified, ahead, behind)

