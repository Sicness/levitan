import json
import sys
import os
import inspect
import socket

import skypebot


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


def load_config(cfile):
    with open(cfile, 'r') as f:
        try:
            data = json.load(f)
            ckeys = data.keys()

            mandatory_keys = ['bind', 'port', 'rooms', 'plugins']

            for k in mandatory_keys:
                if not k in ckeys:
                    return -3, 'Mandatory field \'%s\' field is absent in %s' % (k, ckeys), None

            return 0, None, data
        except ValueError as e:
            return -2, 'Config file malformed: %s %s ' % (e, cfile), None


if __name__ == '__main__':
    config_file = None

    try:
        config_file = sys.argv[1]
        if not os.path.isfile(config_file):
            raise IndexError
    except IndexError:
        print('No external config file passed or it doesn\'t exist, trying one in possible directories!')
        config_file = 'levitan.conf'

        possible_conf_locations = [os.path.join(os.getcwd(), config_file),
                                   os.path.join(os.path.expanduser('~'), config_file),
                                   os.path.join('/etc', config_file)]
        found = False
        for location in possible_conf_locations:
            if os.path.isfile(location):
                config_file = location
                found = True
                break

        if not found:
            print('Configuration file wasn\'t found anywhere in the filesystem. Exiting')
            sys.exit(-1)

    print('Reading config file: %s' % config_file)

    config_status, error_msg, cfg = load_config(config_file)
    if config_status:
        print('Error occurred during reading configuration file:\n %s ' % error_msg)
        sys.exit(config_status)

    print('\nCompleted reading. Loading plugins:')

    # Create plugin names list
    load_plugins = []
    for plugin in cfg['plugins']:
        try:
            load_plugins.append(plugin['name'])
        except KeyError as e:
            print('Plugin section %s cannot be loaded as getting name returns KeyError: %s' % (plugin, e))

    # Create plugin class instances
    plugin_instances = []
    for plugin in load_plugins:
        module = __import__('Plugins.' + plugin)
        plugin_class = getattr(module, plugin)
        for elem in dir(plugin_class):
            obj = getattr(plugin_class, elem)
            if inspect.isclass(obj):
                plugin_instances.append(obj(filter(lambda x: x['name'] == plugin, cfg['plugins'])[0]))
                break

    # Test them
    for plugin in plugin_instances:
        print('Testing %s' % plugin.hello())
        t = plugin.check_plugin_config()
        if t['status']:
            print('Plugin was configured properly (everything was loaded)')
        else:
            print('Plugin wasn\'t configured properly: %s. Unloading' % t['errorMessage'])
            plugin_instances.remove(plugin)


    print('Starting SkypeBot and passing plugins')
    bot = skypebot.SkypeBot(plugin_instances)

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

