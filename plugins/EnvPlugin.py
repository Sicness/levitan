import re
import datetime

from template import PluginTemplate


def human(delta):
    if delta.seconds < 60:
        return 'just now'
    elif (delta.seconds / 60) < 2:
        return 'for a few minutes already'
    elif (delta.seconds / 3600) == 0:
        return 'for %s minutes already' % (delta.seconds / 60)
    else:
        return 'for %s hours already' % (delta.seconds / 3600)


class Environment:
    def __init__(self, name):
        self.env_name = name
        self.taken = False
        self.start_time = None
        self.time_taken = None
        self.person = None

    def take(self, person):
        self.person = person
        self.taken = True
        self.start_time = datetime.datetime.now()

    def free(self):
        self.taken = False
        self.person = None
        self.time_taken = None
        self.start_time = None

    def __repr__(self):
        if self.taken:
            return "%s taken by %s %s" % (self.env_name, self.person, human(self.time_taken))
        else:
            return "%s free" % self.env_name

    def __str__(self):
        return self.__repr__()


class EnvPlugin(PluginTemplate):
    """
    EnvPlugin - managing environments across developrs. You can take or free envs, which are gathered from
    configuration file. It doesn't actually lock any server to you, but gives information to your teammates with
    which environment you are currently working.

    This was the most useful part of classical Levitan.

    Available commands:
    ?env - get the list of all the envs and statuses
    ?env take <env name> - take an env
    ?env free <env name> - set the env free
    ?env free me - set all envs, taken by me, free
    """

    def __init__(self, config):
        self.name = str(self.__class__.__name__)
        self.sender = None
        self.room_tag = None
        self.config = config
        self.requests = ['^\s*\?env\s*$',
                         '^\s*\?env\s+take\s+([^ ]*)\s*$',
                         '^\s*\?env\s+free\s+([^ ]*)\s*$'
        ]
        self.method = zip(self.requests, [self.get_env, self.take_env, self.free_env])
        self.envs = {}

    def process(self, message):
        self.sender = message.Sender.FullName
        try:
            self.room_tag = self.config['rooms'].keys()[self.config['rooms'].values().index(message.Chat.Topic)]
        except ValueError:
            return 'EnvPlugin can only be called in chat rooms, not individually'

        for t in self.method:
            match = re.match(t[0], message.Body, re.IGNORECASE)
            if match:
                return t[1](*match.groups())

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

        envs_by_room_list = [room['envs'] for room in local_rooms.values()]
        if False in map(lambda x: sorted(list(set(x))) == sorted(x), envs_by_room_list):
            return {'status': False, 'errorMessage': 'Some room has duplicate envs'}

        self.envs = dict((name, map(Environment, envl)) for name, envl in zip(local_room_tags, envs_by_room_list))

        return {'status': True, 'errorMessage': None}

    def get_env(self):
        self.check_expire()
        return '\n'.join(map(str, self.envs[self.room_tag]))

    def take_env(self, env):
        self.check_expire()
        envs_by_tag = self.envs[self.room_tag]
        try:
            env_obj = filter(lambda x: x.env_name == env, envs_by_tag)[0]
            env_obj.take(self.sender)
            return 'Env %s is now taken by %s' % (env, self.sender)
        except IndexError:
            return '%s doesn\'t seem to exist in env list: %s.' % (env,
                                                                   ', '.join(map(lambda x: x.env_name,
                                                                                 envs_by_tag)))

    def free_env(self, env):
        self.check_expire()
        envs_by_tag = self.envs[self.room_tag]
        if env == 'me':
            env_obj_list = filter(lambda x: x.person == self.sender, envs_by_tag)
        else:
            try:
                env_obj_list = filter(lambda x: x.env_name == env, envs_by_tag)
            except IndexError:
                return '%s doesn\'t seem to exist in env list: %s.' % (env,
                                                                       ', '.join(map(lambda x: x.env_name,
                                                                                     envs_by_tag)))
        answer = []
        for e in env_obj_list:
            if e.taken:
                e.free()
                answer.append('Env %s is now free' % e.env_name)
            else:
                answer.append('Env %s wasn\'t taken by anyone' % e.env_name)

        return '\n'.join(answer) if answer else 'You haven\'t taken any envs'

    def check_expire(self, ):
        envs_by_tag = self.envs[self.room_tag]
        try:
            expire_time = int(self.config['plugins'][self.name]['rooms'][self.room_tag]['expireTime'])
        except KeyError:
            expire_time = 6
        for env in envs_by_tag:
            if env.taken:
                env.time_taken = datetime.datetime.now() - env.start_time
                hours = env.time_taken.seconds / 3600
                if hours >= expire_time:
                    env.free()
