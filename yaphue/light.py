from .rgb.rgbxy import Converter, GamutA


class Light(object):
    def __init__(self, bridge, id, **kwargs):
        self.bridge = bridge
        self.id = int(id)
        self.name = kwargs.get('name')
        self.model_id = kwargs.get('modelid')
        self.unique_id = kwargs.get('uniqueid')

        state = kwargs.get('state', {})
        self._on = state.get('on')
        self._brightness = state.get('bri')
        self._hue = state.get('hue')
        self._saturation = state.get('sat')
        self._xy = state.get('xy')
        self._temperature = state.get('ct')
        self.reachable = state.get('reachable')

    def __repr__(self):
        return '<Light "%s">' % (self.id)

    def set(self):
        self.bridge._put(
            'lights/%s/state' % (self.id),
            {
                key: value
                for key, value in {
                    'on': self._on,
                    'bri': self._brightness,
                    # Features not tested yet are commented out.
                    # 'hue': self._hue,
                    # 'sat': self._saturation,
                    'xy': self._xy,
                    'ct': self._temperature,
                }.items() if value is not None
            }
            if self.on else
            {
                'on': self.on,
            }
        )

    @property
    def capabilities(self):
        return [
            key
            for key, value in {
                'on': self._on,
                'brightness': self._brightness,
                # 'hue': self._hue,
                # 'saturation': self._saturation,
                'xy': self._xy,
                'temperature': self._temperature,
            }.items() if value is not None
        ]

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, value):
        self._on = value

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if not isinstance(value, int):
            raise ValueError('value must be an integer.')
        if value > 254:
            value = 254
        if value < 1:
            value = 1

        self._brightness = value

    @property
    def temperature(self):
        return int(1000000 / self._temperature)

    @temperature.setter
    def temperature(self, value):
        if 'temperature' not in self.capabilities:
            raise ValueError('Setting temperature is not supported by the light.')
        if not isinstance(value, int):
            raise ValueError('value must be an integer.')
        if value > 6500:
            value = 6500
        if value < 2000:
            value = 2000

        mired = int(1000000 / value)

        self._temperature = mired

    @property
    def hue(self):
        return self._hue

    @hue.setter
    def hue(self, value):
        if 'hue' not in self.capabilities:
            raise ValueError('Setting hue is not supported by the light.')
        self._hue = value

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        if 'xy' not in self.capabilities:
            raise ValueError('Setting color is not supported by the light.')
        self._xy = value

    @property
    def rgb(self):
        x, y = self._xy
        return Converter().xy_to_rgb(x, y, self.brightness)

    @rgb.setter
    def rgb(self, rgb):
        x, y = Converter().rgb_to_xy(*rgb)
        self._xy = [x, y]

    @property
    def saturation(self):
        return self._saturation

    @saturation.setter
    def saturation(self, value):
        if 'saturation' not in self.capabilities:
            raise ValueError('Setting saturation is not supported by the light.')
        self._saturation = value

    def alert(self):
        self.bridge._put(
            'lights/%s/state' % (self.id),
            {
                'alert': 'select',
            }
        )
