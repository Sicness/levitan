import json
import sys
import socket

import skypebot
from pluginInitializer import create_initial_plugin_list, initialize_plugins
from configInitializer import load_config

def dispatch(message, rooms):
    print message
    try:
        res = json.loads(message)
        if not 'message' in res:
            raise ValueError
    except ValueError:
        print('Incoming message was malformed')
        return

    if 'room' in res:
        for room in rooms:
            if res['room'] in room:
                bot.send(room[res['room']], res['message'])
            else:
                print('Unknown room %s' % (res['room']))


if __name__ == '__main__':

    # Load config
    status, error_msg, cfg = load_config(sys.argv)
    if status:
        print('Error occurred during reading configuration file:\n %s ' % error_msg)
        sys.exit(status)

    print('Complete reading.')

    # Create plugin list from all the plugins in configuration
    plugin_name_list = create_initial_plugin_list(cfg)

    # Create plugin class instances
    plugins = initialize_plugins(plugin_name_list, cfg)

    print('Starting SkypeBot and passing plugins')
    bot = skypebot.SkypeBot(plugins)

    bind = cfg['bind']
    port = int(cfg['port'])  # just in case
    print ('Running TCP socket on %s:%d' % (bind, port))

    # Listen the socket!
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind, port))
    s.listen(1)

    while True:
        conn, addr = s.accept()
        recv_data = conn.recv(1024)
        print ("recv: %s" % recv_data)
        dispatch(recv_data, cfg['rooms'])
        conn.close()

    s.close()

