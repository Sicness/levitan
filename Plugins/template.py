import re


class PluginTemplate:
    """
    This class is template for Levitan Plugins
    Here are the methods, that must be overloaded (except plugin_process_request) for correct behaviour
    """
    def __init__(self, config):
        """
        __init__ - obviously create instance

        :param config: configuration section, which describes this particular plugin (chosen by
        name in pluginInitializer.initialize_plugins
        :return instance of plugin
        """
        self.name = config['name']
        self.requests = []

    def plugin_process_request(self, skypeMessage):
        """
        This method runs match against self.request list of regexps
        and returns check status and calls self.process as message

        :param skypeMessage: instance of Skype4Py.Chat.ChatMessage

        """
        for rq in self.requests:
            if re.match(rq, skypeMessage.Body, re.IGNORECASE):
                return {'status': True, 'message': self.process(skypeMessage)}
        return {'status': False, 'message': 'None'}

    def process(self, skypeMessage):
        """
        This method does all the things. It's not a must to return anything, but usually it's expected

        :param skypeMessage: instance of Skype4Py.Chat.ChatMessage
        """
        return None

    def check_plugin_config(self):
        """
        This method runs check, if all  self.config passed all the requested variables
        """
        return {'status': True, 'errorMessage': None}

    def hello(self):
        """
        Return name (or some additional information). Used on init.
        """
        return "Plugin"