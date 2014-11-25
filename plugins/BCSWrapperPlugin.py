import socket
import re
import requests


from template import PluginTemplate


class BCSWrapperPlugin(PluginTemplate):
    """
    BCSWP - simple wrapper around Build-Correlation Service. This service is intended to tell you
    about builds on each repo and corresponding version.


    Available commands:
    ?bcs help - print this help
    ?bcs list - get list of watched repositories
    ?bcs show <repo name> - show the full log of repo
    ?env build <repo name> <commit hash> - show build which corresponds with <commit hash>
    ?env commit <repo name> <build number> - show commit hash which corresponds with <build number>
    """

    def __init__(self, config):
        self.name = str(self.__class__.__name__)
        self.host = None
        self.port = None
        self.config = config
        self.requests = ['^\s*\?bcs\s+help*$',
                         '^\s*\?bcs\s+list*$',
                         '^\s*\?bcs\s+show\s+([^ ]*)\s*$',
                         '^\s*\?bcs\s+build\s+([^ ]*)\s+([^ ]*)\s*$',
                         '^\s*\?bcs\s+commit\s+([^ ]*)\s+([^ ]*)\s*$']

        self.method = zip(self.requests, [self.help,
                                          self.get_list,
                                          self.show_repo,
                                          self.build,
                                          self.commit])

    def process(self, message):
        for t in self.method:
            match = re.match(t[0], message.Body, re.IGNORECASE)
            if match:
                return t[1](*match.groups())

    def check_plugin_config(self):
        try:
            self.host = self.config['plugins'][self.name]['bcshost']
            self.port = int(self.config['plugins'][self.name]['bcsport'])
        except KeyError as e:
            return {'status': False, 'errorMessage': 'Obligatory param \'%s\' is absent' % e}

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        resp_code = sock.connect_ex((self.host, self.port))
        if resp_code:
            return {'status': False, 'errorMessage': 'Port %d seems to be closed on %s' % (self.port, self.host)}

        return {'status': True, 'errorMessage': None}

    def help(self):
        return self.__doc__

    def get_list(self):
        return self.process_rq('repolist')

    def show_repo(self, repo):
        return self.process_rq('%s/log' % repo)

    def build(self, repo, build):
        return self.process_rq('%s/build/%s' % (repo, build))

    def commit(self, repo, commit):
        return self.process_rq('%s/commit/%s' % (repo, commit))

    def process_rq(self, address):
        r = requests.get('http://%s:%d/%s' % (self.host, self.port, address))
        return '\n' + r.content
