import json
import sys
import os
import inspect
import socket

import skypebot


def dispatch(s):
    pass

def check_load_config(cfile = './levitan.conf'):
    print('Reading config file: %s' % cfile)

    if not os.path.isfile(cfile):
        return -1, 'Config file not found: %s ' % cfile, None
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
    except IndexError:
        print('No external config file passed, using default one!')

    config_status, error_msg, parsed_cfg = check_load_config(config_file) if config_file else check_load_config()
    if config_status:
        print('Error occurred during reading configuration file:\n %s ' % error_msg)
        sys.exit(config_status)

    print('\nCompleted reading. Loading plugins:')

    # Create plugin names list
    load_plugins = []
    for plugin in parsed_cfg['plugins']:
        try:
            load_plugins.append(plugin['name'])
        except KeyError as e:
            print('Plugin section %s cannot be loaded as getting name returns KeyError: %s' % (plugin, e))

    # Creat plugin class instances
    plugin_instances = []
    for plugin in load_plugins:
        module = __import__('Plugins.' + plugin)
        plugin_class = getattr(module, plugin)
        for elem in dir(plugin_class):
            obj = getattr(plugin_class, elem)
            if inspect.isclass(obj):
                plugin_instances.append(obj(filter(lambda x: x['name'] == plugin, parsed_cfg['plugins'])[0]))
                break

    # Test them
    for plugin in plugin_instances:
        print plugin.hello()
        print('Testing %s' % plugin.hello())
        t = plugin.check_plugin_config()
        if t['status']:
            print('Plugin was configured properly (everything was loaded)')
        else:
            print('Plugin wasn\'t configured properly: %s. Unloading' % t['errorMessage'])
            plugin_instances.remove(plugin)


    print('Starting SkypeBot and passing plugins')
    bot = skypebot.SkypeBot(plugin_instances)

    bind = parsed_cfg['bind']
    port = int(parsed_cfg['port'])  # just in case
    print ('Running Levitan on %s:%d' % (bind, port))

    # Listen!
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind, port))
    s.listen(1)

    while 1:
        conn, addr = s.accept()
        data = conn.recv(1024)
        print "recv: ", data
        dispatch(data)
        conn.close()

    s.close()

