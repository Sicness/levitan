from template import PluginTemplate


class HiPlugin(PluginTemplate):
    def __init__(self, config):
        PluginTemplate.__init__(self, config)
        self.requests = ["^\s*hello\s*$"]

    def plugin_process_request(self, incoming):
        return PluginTemplate.plugin_process_request(self, incoming)

    def process(self, incoming):
        return "hello"

    def check_plugin_config(self):
        return {'status': True, 'errorMessage': None}

    def hello(self):
        return "HiPlugin"