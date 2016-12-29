import os
import io
import json
import requests
import socket
from .light import Light


class HueError(Exception):
    pass


class Bridge(object):
    APPLICATION_NAME = 'yaphue'

    def __init__(self, ip, id='unknown', name='unknown', configuration_path=None):
        self.ip = ip
        self.id = id
        self.name = name
        self.__lights = None
        self.__configuration_path = configuration_path or os.environ.get('HUE_PATH') or os.path.expanduser('~/.config/yaphue')
        self.__username = self.configuration.get('username')

    def __repr__(self):
        return '<Bridge "%s">' % (self.ip)

    def __raise_exceptions(self, response):
        if isinstance(response, list):
            for message in response:
                if 'error' in message.keys():
                    raise HueError(message['error']['description'])

    def __load_configuration(self):
        configuration_file = os.path.join(self.__configuration_path, 'config.json')
        configuration = {}

        if not os.path.exists(configuration_file):
            return configuration

        with open(configuration_file, 'r') as f:
            try:
                configuration = json.loads(f.read())
            except:
                return configuration
        return configuration

    @property
    def configuration(self):
        configuration = self.__load_configuration()
        return configuration.get(self.ip, {})

    @configuration.setter
    def configuration(self, new_configuration):
        if not os.path.exists(self.__configuration_path):
            os.makedirs(self.__configuration_path)

        configuration_file = os.path.join(self.__configuration_path, 'config.json')
        configuration = self.__load_configuration()
        with open(configuration_file, 'w') as f:
            if self.ip in configuration:
                configuration[self.ip].update(new_configuration)
            else:
                configuration[self.ip] = new_configuration
            f.write(json.dumps(configuration))

    def api(self, endpoint, use_username):
        if use_username:
            if self.__username is None:
                raise ValueError('username is not set! Please re-authenticate.')
            return 'http://%s/api/%s/%s' % (self.ip, self.__username, endpoint)
        return 'http://%s/api/%s' % (self.ip, endpoint)

    def _get(self, endpoint, use_username=True):
        r = requests.get(self.api(endpoint, use_username))
        r.raise_for_status()
        response = r.json()
        self.__raise_exceptions(response)
        return response

    def _post(self, endpoint, body, use_username=True):
        r = requests.post(self.api(endpoint, use_username), json=body)
        r.raise_for_status()
        response = r.json()
        self.__raise_exceptions(response)
        return response

    def _put(self, endpoint, body, use_username=True):
        r = requests.put(self.api(endpoint, use_username), json=body)
        r.raise_for_status()
        response = r.json()
        self.__raise_exceptions(response)
        return response

    def authorize(self):
        hostname = socket.gethostname()[0:19]
        for message in self._post('', {'devicetype': '%s#%s' % (self.APPLICATION_NAME, hostname)}, False):
            if 'success' in message:
                self.__username = message['success']['username']
                print('Authorized with username "%s"' % self.__username)
                self.configuration = {
                    'username': self.__username
                }
                return
        raise HueError('Unknown error while authorizing.')

    @property
    def username(self):
        if self.__username:
            return self.__username
        raise HueError('username not set! Have you authorized?')

    @property
    def lights(self):
        if self.__lights:
            return self.__lights
        response = self._get('lights')
        self.__lights = {
            int(id): Light(self, id, **attrs)
            for id, attrs in response.items()
        }
        return self.__lights

    @staticmethod
    def discover():
        r = requests.get('https://www.meethue.com/api/nupnp')
        r.raise_for_status()

        return [
            Bridge(ip=bridge['internalipaddress'], id=bridge.get('id'), name=bridge.get('name'))
            for bridge in r.json()
        ]
