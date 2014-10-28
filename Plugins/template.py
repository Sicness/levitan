import re


class PluginTemplate:
    def __init__(self, config):
        self.name = config['name']
        self.requests = []

    def plugin_process_request(self, incoming):
        for rq in self.requests:
            if re.match(rq, incoming, re.IGNORECASE):
                return {'status': True, 'message': self.process(incoming)}
        return {'status': False, 'message': 'None'}

    def process(self, incoming):
        return None

    def check_plugin_config(self):
        return {'status': True, 'errorMessage': None}

    def hello(self):
        return "Plugin"