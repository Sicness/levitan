import re
import datetime

from template import PluginTemplate
import gc
import skypebot

def fancy_time_output(delta):
    """
    Convert raw datetime.datetime object to fancy string

    :param delta: datetime.datetime.now() - Environment.start_time object
    :return: string, showing for how long an instance was taken
    """
    if delta.seconds < 60:
        return 'just now'
    elif (delta.seconds / 60) < 2:
        return 'for a few minutes already'
    elif (delta.seconds / 3600) == 0:
        return 'for %s minutes already' % (delta.seconds / 60)
    else:
        return 'for %s hours already' % (delta.seconds / 3600)


class Environment:
    """
    This class provides environment entity with its name, status and time difference between
    taking it and current time.

    Also it provides fancy output for Skype message.
    """
    def __init__(self, name):
        self.env_name = name
        self.taken = False
        self.start_time = None
        self.time_taken = None
        self.owner = None

    def take(self, person):
        self.owner = person
        self.taken = True
        self.start_time = datetime.datetime.now()

    def free(self):
        self.taken = False
        self.owner = None
        self.time_taken = None
        self.start_time = None

    def __repr__(self):
        if self.taken:
            return "%s taken by %s %s" % (self.env_name, self.owner, fancy_time_output(self.time_taken))
        else:
            return "%s free" % self.env_name

    def __str__(self):
        return self.__repr__()


class EnvPlugin(PluginTemplate):
    """
    EnvPlugin - managing environments across developers. You can take or free envs, which are gathered from
    configuration file. It doesn't actually lock any server to you, but gives information to your teammates with
    which environment you are currently working.

    This was the most useful part of classical Levitan.

    Available commands:
    For both personal chats and chat rooms:
    ?env help - print this help
    ?env take <env name> - take an env
    ?env free <env name> - set the env free

    For personal chats:
    ?env <room tag> - get the list of all the envs and statuses
    ?env take <env name> <room tag> - take an env, used if duplicates found.
    ?env free <env name> <room tag> - free an env, used if duplicates found.
    """

    def __init__(self, config):
        self.name = str(self.__class__.__name__)
        self.skypebot_instance = None
        self.sender = None
        self.room_tag = None
        self.config = config
        self.requests = ['^\s*\?env\s*$',
                         '^\s*\?env\s+help*$',
                         '^\s*\?env\s+take\s+([^ ]*)\s*$',
                         '^\s*\?env\s+free\s+([^ ]*)\s*$',
                         '^\s*\?env\s+([^ ]*)\s*$',
                         '^\s*\?env\s+take\s+([^ ]*)\s+([^ ]*)\s*$',
                         '^\s*\?env\s+free\s+([^ ]*)\s+([^ ]*)\s*$'
                         ]
        self.methods = [self.help_match,
                        self.env_match, self.env_match_personal,
                        self.take_match, self.take_match_personal,
                        self.free_match, self.free_match_personal]
        self.envs = {}

    def process(self, message):
        self.sender = message.Sender.FullName

        is_personal = False
        tag = ''
        if message.Chat.Topic:
            tag = self.config['rooms'].keys()[self.config['rooms'].values().index(message.Chat.Topic)]
        else:
            is_personal = True

        for method in self.methods:
            response = method(message, tag, is_personal)
            if not response is None:
                return response

    def help_match(self, message, tag=None, is_personal=False):
        if re.match('^\s*\?env\s+help*$', message.Body, re.IGNORECASE):
            return self.help()

        return None

    def env_match(self, message, tag=None, is_personal=False):
        if re.match('^\s*\?env\s*$', message.Body, re.IGNORECASE):
            if is_personal:
                return 'Please specify room ?env <room_tag>. Available tags:\n%s' % \
                       '\n'.join(self.config['plugins'][self.name]['rooms'].keys())
            else:
                return self.get_env(tag)

        return None

    def env_match_personal(self, message, tag, is_personal=True):
        env_match = re.match('^\s*\?env\s+([^ ]*)\s*$', message.Body, re.IGNORECASE)
        if env_match:
            tag = env_match.groups()[0]
            if self.sender_in_room(message.Sender, tag):
                return self.get_env(tag)
            else:
                return 'You are not authorized to make changes in this room or room doesn\'t exist'

        return None

    def take_match(self, message, tag, is_personal=False):
        take_match = re.match('^\s*\?env\s+take\s+([^ ]*)\s*$', message.Body, re.IGNORECASE)
        if take_match:
            env = take_match.groups()[0]
            if is_personal:
                tags = self.get_rooms_by_env(env)
                if not tags:
                    return 'There is no watched room with such env'
                if len(tags) > 1:
                    return 'There are several rooms with such env. Specify room by ?env take <env> <room>'

                if self.sender_in_room(message.Sender, tags[0]):
                    return self.take_env(env, tags[0])
                else:
                    return 'You are not authorized to make changes in this room or room doesn\'t exist'
            else:
                return self.take_env(env, tag)

        return None

    def take_match_personal(self, message, tag, is_personal=True):
        take_match_personal = re.match('^\s*\?env\s+take\s+([^ ]*)\s+([^ ]*)\s*$', message.Body, re.IGNORECASE)
        if take_match_personal:
            env = take_match_personal.groups()[0]
            tag = take_match_personal.groups()[1]
            if self.sender_in_room(message.Sender, tag):
                return self.take_env(env, tag)
            else:
                return 'You are not authorized to make changes in this room or room doesn\'t exist'

    def free_match(self, message, tag, is_personal=False):
        free_match = re.match('^\s*\?env\s+free\s+([^ ]*)\s*$', message.Body, re.IGNORECASE)
        if free_match:
            env = free_match.groups()[0]
            if is_personal:
                tags = self.get_rooms_by_env(env)
                if not tags:
                    return 'There is no watched room with such env'
                if len(tags) > 1:
                    return 'There are several rooms with such env. Specify room by ?env free <env> <room>'

                if self.sender_in_room(message.Sender, tags[0]):
                    return self.free_env(env, tags[0])
                else:
                    return 'You are not authorized to make changes in this room or room doesn\'t exist'
            else:
                return self.free_env(env, tag)

        return None

    def free_match_personal(self, message, tag, is_personal=True):
        free_match_personal = re.match('^\s*\?env\s+free\s+([^ ]*)\s+([^ ]*)\s*$', message.Body, re.IGNORECASE)
        if free_match_personal:
            env = free_match_personal.groups()[0]
            tag = free_match_personal.groups()[1]
            if self.sender_in_room(message.Sender, tag):
                return self.free_env(env, tag)
            else:
                return 'You are not authorized to make changes in this room or room doesn\'t exist'

        return None

    def check_plugin_config(self):
        try:
            local_rooms = self.config['plugins'][self.name]['rooms']
        except KeyError:
            return {'status': False, 'errorMessage': 'Obligatory param \'rooms\' is absent'}

        avail_room_tags = self.config['rooms'].keys()
        local_room_tags = local_rooms.keys()

        if not list(set(local_room_tags)) == local_room_tags:
            return {'status': False, 'errorMessage': 'Duplicate rooms found in plugin config'}

        if False in map(lambda x: x in avail_room_tags, local_room_tags):
            return {'status': False, 'errorMessage': 'Plugin has rooms, which are not defined globally'}

        try:
            envs_by_room_list = [room['envs'] for room in local_rooms.values()]
        except KeyError:
            return {'status': False, 'errorMessage': 'Some room has no envs section'}

        self.envs = dict((name, map(Environment, envl)) for name, envl in zip(local_room_tags, envs_by_room_list))

        return {'status': True, 'errorMessage': None}

    def get_env(self, tag):
        self.check_expire(tag)
        return '\n'.join(map(str, self.envs[tag]))

    def help(self):
        return self.__doc__

    def take_env(self, env, tag):
        self.check_expire(tag)
        envs_by_tag = self.envs[tag]
        try:
            env_obj = filter(lambda x: x.env_name == env, envs_by_tag)[0]
            env_obj.take(self.sender)
            return 'Env %s is now taken by %s' % (env, self.sender)
        except IndexError:
            return '%s doesn\'t seem to exist in env list: %s.' % (env,
                                                                   ', '.join(map(lambda x: x.env_name,
                                                                                 envs_by_tag)))

    def free_env(self, env, tag):
        self.check_expire(tag)
        envs_by_tag = self.envs[tag]

        try:
            env_obj = filter(lambda x: x.env_name == env, envs_by_tag)[0]
        except IndexError:
            return '%s doesn\'t seem to exist in env list: %s.' % (env,
                                                                   ', '.join(map(lambda x: x.env_name,
                                                                                     envs_by_tag)))
        if env_obj.taken:
            env_obj.free()
            return 'Env %s is now free' % env
        else:
            return 'Env %s wasn\'t taken by anyone' % env


    def check_expire(self, tag):
        """
        On each request this function updates time_taken value (difference between times when the env was first taken
        and current time). If this time is bigger than expire_time, it sets the env free.
        """
        envs_by_tag = self.envs[tag]
        try:
            expire_time = int(self.config['plugins'][self.name]['rooms'][tag]['expireTime'])
        except KeyError:
            expire_time = 6

        if expire_time == -1:
            return

        for env in envs_by_tag:
            if env.taken:
                env.time_taken = datetime.datetime.now() - env.start_time
                hours = env.time_taken.total_seconds() / 3600
                if hours >= expire_time:
                    env.free()

    def sender_in_room(self, sender, room_tag):
        """
        This method checks, if sender belongs any watched room
        :param skype_message: sender's
        :return: -1 if room_tag is not in watched
        """
        self.get_skype_bot()
        if not room_tag in self.config['plugins'][self.name]['rooms'].keys():
            return False

        # Get watched rooms
        room_topics_list = [self.config['rooms'][x] for x in self.config['plugins'][self.name]['rooms'].keys()]
        room_object_list = filter((lambda c: c.Topic in room_topics_list),
                                  [x for x in self.skypebot_instance.skype.Chats])

        for room in room_object_list:
            for user in room.Members:
                if sender == user and room.Topic == self.config['rooms'][room_tag]:
                    return True

        return False

    def get_skype_bot(self):
        if self.skypebot_instance is None:
            # Get SkypeBot instance for one-on-one messaging
            for obj in gc.get_objects():
                if isinstance(obj, skypebot.SkypeBot):
                    self.skypebot_instance = obj
                    break


    def get_rooms_by_env(self, env):
        self.get_skype_bot()
        local_rooms = self.config['plugins'][self.name]['rooms']
        envs_by_rooms = [room['envs'] for room in local_rooms.values()]
        zipped_envs_by_rooms =  zip (local_rooms.keys(), envs_by_rooms)
        rooms = []
        for room in zipped_envs_by_rooms:
            if env in room[1]:
                rooms.append(room[0])

        return rooms
