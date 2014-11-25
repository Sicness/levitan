import re
from jenkinsapi.jenkins import Jenkins
from template import PluginTemplate


class JenkinsJob(PluginTemplate):
    """
    This plugin check status of set Jenkins job and reports detailed info
    if the jobs is running right now
    """
    def __init__(self, config):
        self.name = self.__class__.__name__
        self.mandatory_params = ["jenkins_url", "user", "password", "job"]
        self.requests = ['^\s*\?ci\s*$']
        self.full_config = config
        self.config = config['plugins'][self.name]
        self.jenkins_url = None
        self.user = None
        self.password = None
        self.auth = None
        self.job = None

    def process(self, skype_message):
        try:
            if self.auth:
                j = Jenkins(self.jenkins_url, self.user, self.password)
            else:
                j = Jenkins(self.jenkins_url)
            build = j.get_job(self.job).get_last_build()
            if build.is_running():
                build_params=build._data['actions'][3]['parameters']
                p=dict([(i['name'], i['value']) for i in build_params])
                return "CI process is busy by %s | %s | %s | %s\ngit fetch gerrit %s" \
                       % (p['GERRIT_EVENT_ACCOUNT_NAME'],
                          p['GERRIT_PATCHSET_REVISION'][:7],
                          p['GERRIT_CHANGE_SUBJECT'],
                          p['GERRIT_CHANGE_URL'],
                          p['GERRIT_REFSPEC'])
            else:
                return "CI process is free"
        except Exception as e:
            return "JenkinsJob: something gone wrong: ", e

    def check_plugin_config(self):
        for i in self.mandatory_params:
            if not i in self.config:
                return {'status' : False,
                        'errorMessage': "No " + i + " in config"}

        self.jenkins_url = self.config['jenkins_url']
        self.user = self.config['user']
        self.password = self.config['password']
        self.auth = True if self.config['authorization'] == "true" else False
        self.job = self.config['job']
        return {'status': True, 'errorMessage': None}

    def hello(self):
        """
        Return name (or some additional information). Used on init.
        """
        return "JenkinsJob plugin"