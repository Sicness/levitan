from template import PluginTemplate


class HiPlugin(PluginTemplate):
    """
    HiPlugin - simplest plugin to check that Levitan is running.
    It responds 'hello' to 'hello' from user
    """
    def __init__(self, config=None):
        self.requests = ["^\s*hello\s*$"]

    def process(self, skype_message):
        return "hello"

    def check_plugin_config(self):
        return {'status': True, 'errorMessage': None}
