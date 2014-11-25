from template import PluginTemplate


class HiPlugin(PluginTemplate):
    """
    HiPlugin - simplest plugin to check that Levitan is running.
    It responds 'hi' to 'hi' from user
    """
    def __init__(self, config=None):
        self.requests = ["^\s*hi\s*$"]

    def process(self, skype_message):
        return "hi"

    def check_plugin_config(self):
        return {'status': True, 'errorMessage': None}