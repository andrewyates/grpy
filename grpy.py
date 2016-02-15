import codecs
import json
import os

import pygit2
import termcolor


class ManagedRepo:
    def __init__(self, path, branches):
        error = None
        path = _expand(path)
        if not os.path.exists(path):
            error = "repository path does not exist: %s" % path
        elif not os.path.exists(os.path.join(path, '.git')):
            error = "path does not contain a git repository: %s" % path

        if error is not None:
            raise RuntimeError(error)
            
        self.repo = pygit2.Repository(path)
        self.path = _normalize(path)
        
        self.branches = branches

    def status(self):
        branches = {branch: self.branch_status(branch) for branch in self.branches}
        modified = len(self.repo.status())

        return (modified, branches)

    def branch_status(self, branch):
        if branch in self.repo.listall_branches():
            missing = False

            if self.repo.lookup_branch(branch).upstream is not None:
                ahead, behind = self.repo.ahead_behind(self.repo.lookup_branch(branch).target,
                                                       self.repo.lookup_branch(branch).upstream.target)
            else:
                ahead, behind = -1, 0
        else:
            missing = True
            ahead, behind = None, None, None

        return missing, ahead, behind

    def split_path(self):
        i = self.path.rfind('/', 0, len(self.path) - 1) + 1
        basepath, dirname = self.path[:i], self.path[i:]
        return basepath, dirname

        
def _expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def _normalize(path):
    home = os.path.expanduser("~/")
    path = os.path.expandvars(os.path.expanduser(path))
    if path.startswith(home):
        path = os.path.join("~/", path[len(home):])

    return path


def _not_colored(s, color, attrs=[]):
    return s


def load_grconfig(fn, branches=['master']):
    repos = {}

    with codecs.open(fn, 'r', encoding='utf-8') as f:
        js = json.load(f)

        if len(js.keys()) > 1 or 'tags' not in js:
            raise RuntimeError("grconfig '%s' contains unknown keys: %s" % (fn, js.keys()))

        for tag in js['tags']:
            for repo in js['tags'][tag]:
                repos.setdefault(repo, {}).setdefault('tags', set()).add(tag)

    for repo in repos:
        assert 'branches' not in repos[repo]
        repos[repo]['branches'] = branches

    return repos


def print_details(mr, maxlen):
    modified, branches = mr.status()

    pathA, pathB = mr.split_path()
    header_name = "%0-*s" % (maxlen, pathA + pathB)
    i = header_name.find(pathA) + len(pathA)
    header_name = colored(header_name[:i], "white", attrs=["dark"]) + colored(header_name[i:], "white")

    print "%s %s" % (header_name, colored("%s modified" % modified, "red") if modified != 0 else colored("Clean", "green"))

    skip_updated = True
    for branch, (missing, ahead, behind) in branches.iteritems():
        if missing:
            brstate = None
        else:
            brstate = ["%s %s" % (k, count) for k, count in [('ahead', ahead), ('behind', behind)] if count > 0]

        updated = False
        if brstate is None:
            state = colored("missing", "magenta")
        elif len(brstate) == 0:
            if ahead == -1:
                state = colored("no remote", "magenta")
            else:
                updated = True
                state = colored("up-to-date", "white")
        else:
            state = colored(", ".join(brstate), "cyan")

        header_branch = colored("%0*s" % (maxlen / 2, "   " + branch), "white", attrs=[])
        if not (skip_updated and updated):
            print "%s  %s" % (header_branch, state)

if __name__ == "__main__":
    if True:
        colored = termcolor.colored
    else:
        colored = _not_colored
        
    repos = load_grconfig(_expand("~/.grconfig.json"))

    mrs = []
    for repo, d in sorted(repos.iteritems()):
        try:
            mrs.append(ManagedRepo(repo, d['branches']))
        except:
            print colored("missing: ", "red") + _expand(repo)

    maxlen = max(len(mr.path) for mr in mrs) + 2
    for mr in mrs:
        print_details(mr, maxlen)

