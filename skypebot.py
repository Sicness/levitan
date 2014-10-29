import Skype4Py


class SkypeBot:
    def __init__(self, plugins):
        self.skype = Skype4Py.Skype(Events=self)
        self.skype.FriendlyName = "Skype Bot"
        self.skype.Attach()
        self.plugins = plugins

    def AttachmentStatus(self, status):
        if status == Skype4Py.apiAttachAvailable:
            self.skype.Attach()

    def MessageStatus(self, msg, status):
        print("INCOMING> %s" % msg.Body)
        if status == Skype4Py.cmsReceived:
            for plugin in self.plugins:
                r = plugin.plugin_process_request(msg.Body)
                if r['status']:
                    msg.Chat.SendMessage(r['message'])

    def send(self, topic, message):
        for chat in self.skype.Chats:
            if chat.Topic == topic:
                chat.SendMessage(message)
