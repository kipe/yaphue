import os
import json
import requests
import socket
from .light import Light


class HueError(Exception):
    pass


class Bridge(object):
    APPLICATION_NAME = 'yaphue'

    def __init__(self, id, ip=None, configuration_path=None):
        self.id = id

        self.__configuration_path = configuration_path or os.environ.get('HUE_PATH') or os.path.expanduser('~/.config/yaphue')
        self.__username = self.configuration.get('username')
        self._ip = ip

    def __repr__(self):
        return '<Bridge "%s">' % (self.ip)

    def __raise_exceptions(self, response):
        if isinstance(response, list):
            for message in response:
                if 'error' in message.keys():
                    raise HueError(message['error']['description'])

    @property
    def configuration_file(self):
        if not os.path.exists(self.__configuration_path):
            os.makedirs(self.__configuration_path)
        full_path = os.path.join(self.__configuration_path, 'config.json')
        # touch the file, creating it if if doesn't exist
        open(full_path, 'a').close()
        return full_path

    def __load_configuration(self):
        configuration = {}
        with open(self.configuration_file, 'r') as f:
            try:
                configuration = json.loads(f.read())
            except:
                return configuration
        return configuration

    @property
    def configuration(self):
        configuration = self.__load_configuration()
        return configuration.get(self.id, {})

    @configuration.setter
    def configuration(self, new_configuration):
        configuration = self.__load_configuration()
        with open(self.configuration_file, 'w') as f:
            if self.id in configuration:
                configuration[self.id].update(new_configuration)
            else:
                configuration[self.id] = new_configuration
            f.write(json.dumps(configuration))

    @property
    def ip(self):
        if self._ip:
            return self._ip

        # Try to discover the device
        for bridge in Bridge.discover():
            if bridge.id == self.id:
                self._ip = bridge.ip
                break

        # If bridge cannot be found, raise an AttributeError
        if self._ip is None:
            raise AttributeError('IP address is not set and cannot be discovered')
        return self._ip

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
        return {
            int(id): Light(self, id, **attrs)
            for id, attrs in self._get('lights').items()
        }

    @staticmethod
    def discover():
        r = requests.get('https://discovery.meethue.com')
        r.raise_for_status()

        return [
            Bridge(id=bridge['id'], ip=bridge['internalipaddress'])
            for bridge in r.json()
        ]
