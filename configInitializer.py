import json
import os

def parse_config(file):
    """
    If configuration file was found, then parse it and get
    resulting configuration dictionary
    :param file: path (pre-checked) to configuration file
    :return: status, error_msg, cfg: integer status, 0 if ok, error_message
     with description or None, cfg - dictionary or None
    """
    print('Reading config file: %s' % file)

    with open(file, 'r') as f:
        try:
            data = json.load(f)
            ckeys = data.keys()

            mandatory_keys = ['bind', 'port', 'rooms', 'plugins']

            for k in mandatory_keys:
                if not k in ckeys:
                    return -3, 'Mandatory field \'%s\' field is absent in %s' % (k, ckeys), None

            return 0, None, data
        except ValueError as e:
            return -2, 'Config file malformed: %s %s ' % (e, file), None


def load_config(argv):
    """
    Check configuration file existence. First of all, it checked as a parameter for
    the script (argv), then checked in current working directory, in home directory and
    finally in /etc. If no config found, exit, else parse it with parse_config()
    :param argv: arguments from python script runtime
    :return: see parse_config() return
    """
    found = False
    try:
        config_file = argv[1]
        if not os.path.isfile(config_file):
            raise IndexError
        found = True
    except IndexError:
        print('No external config file passed or it doesn\'t exist, trying one in possible directories!')
        config_file = 'levitan.conf'

        possible_conf_locations = [os.path.join(os.getcwd(), config_file),
                                   os.path.join(os.path.expanduser('~'), config_file),
                                   os.path.join('/etc', config_file)]

        for location in possible_conf_locations:
            if os.path.isfile(location):
                config_file = location
                found = True
                break

    if not found:
        return -1, 'Configuration file wasn\'t found anywhere in the filesystem. Exiting', None

    return parse_config(config_file)
