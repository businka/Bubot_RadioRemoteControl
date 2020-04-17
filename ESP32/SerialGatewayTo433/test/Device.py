class Device:
    signature = None
    bit_length = None
    bit_length_min = None
    bit_length_max = None
    signal_length_bit_min = None
    signal_length_bit_max = None

    def detect(self, signal_data, bit_length=None):
        result = dict(
            matched=0,
            props_count=0,
            device=self
        )
        _data = '{0:x}'.format(signal_data)
        if bit_length and self.bit_length_min and self.bit_length_max:
            result['props_count'] += 1
            if self.bit_length_max <= bit_length <= self.bit_length_min:
                result['matched'] += 1
        for props in self.signature:
            if props['position']:
                position = props['position']
                value = _data[position[0]:position[1]]
                if 'items' in props:
                    result['props_count'] += 1
                    found = False
                    for item in props['items']:
                        if value in props['items'][item]:
                            result['matched'] += 1
                            if 'name' in props:
                                setattr(self, props['name'], item)
                            found = True
                            break
                    if not found and props.get('unknown'):
                        result['props_count'] -= 1
                        setattr(self, props['name'], '{0}:{1}'.format(props['name'], value))

                else:
                    setattr(self, props['name'], value)

        result['matched'] = int(round(result['matched'] / result['props_count'] * 100))
        if result['matched'] < 50:
            return None
        return result
