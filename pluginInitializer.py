import inspect


def create_initial_plugin_list(cfg):
    """
    Create list of plugin names from configuration file
    :param cfg: configuration file
    :return: plugins: raw names
    """
    print('\nLoading plugins:')
    # Create plugin names list
    plugins = cfg['plugins'].keys()
    return plugins


def initialize_plugins(plugin_name_list, cfg):
    """
    Create plugin objects and run their internal checks
    :param plugin_name_list: the raw list from create_initial_plugin_list
    :param cfg: configuration file
    :return: plugins: list of checked plugin instances
    """
    print plugin_name_list
    print('\nInitializing and checking plugins:')
    plugins = []
    for name in plugin_name_list:
        module = __import__('Plugins.' + name)
        plugin_class = getattr(module, name)
        obj = getattr(plugin_class, filter(lambda x: x == name, dir(plugin_class))[0])
        if inspect.isclass(obj):
            instance = obj(*cfg['plugins'][name])

            print('Checking: %s\n' % instance.hello())
            check_response = instance.check_plugin_config()
            if check_response['status']:
                print('%s OK.' % instance.hello())
                plugins.append(instance)
            else:
                print('%s FAIL. Error: %s.' % (instance.hello(), check_response['errorMessage']))
        else:
            print('Plugin with name %s failed to initialize: unable to create instance.' % name)
    return plugins
