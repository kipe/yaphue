from rgbxy import Converter, GamutA


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
        self._colormode = state.get('colormode')
        self.reachable = state.get('reachable')

    def __repr__(self):
        return '<Light "%s">' % (self.id)

    def _set(self, **args):
        print(args)
        self.bridge._put(
            'lights/%s/state' % (self.id),
            args
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
        self._set(on=value)

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        if 'brightness' not in self.capabilities:
            raise ValueError('Setting brightness is not supported by the light.')

        if not isinstance(value, int):
            raise ValueError('value must be an integer.')

        if value > 254:
            value = 254
        if value < 1:
            value = 1

        self._brightness = value
        if not self.on:
            self.on = True
        self._set(brightness=self._brightness)

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
        if not self.on:
            self.on = True
        self._set(ct=self._temperature)

    @property
    def xy(self):
        return self._xy

    @xy.setter
    def xy(self, value):
        if 'xy' not in self.capabilities:
            raise ValueError('Setting color is not supported by the light.')
        self._xy = value
        if not self.on:
            self.on = True
        self._set(xy=self.xy)

    @property
    def rgb(self):
        x, y = self._xy
        return Converter().xy_to_rgb(x, y, self.brightness)

    @rgb.setter
    def rgb(self, rgb):
        x, y = Converter().rgb_to_xy(*rgb)
        self.xy = [x, y]

    def alert(self):
        self.bridge._put(
            'lights/%s/state' % (self.id),
            {
                'alert': 'select',
            }
        )
