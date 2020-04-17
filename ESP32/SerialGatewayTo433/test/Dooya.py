from .Device import Device


class Dooya(Device):
    name = 'Dooya'
    bit_length = 355
    bit_length_min = 353
    bit_length_max = 357
    commands = dict(
        stop=['9a69a6'],
        up=['926926'],
        down=['936936']
    )
    models = dict(
        DC1651=['9a6d36d3', '9b4924d3'],
        DC1653=['9a692693'],
    )
    channels = {
        '0': ['924'],
        '1': ['926'],
        '2': ['934'],
        '3': ['936'],
        '4': ['9a4'],
        '5': ['9a6'],
        '6': ['9b4'],
        '7': ['9b6'],
        '8': ['d24'],
        '9': ['d26'],
        '10': ['d34'],
        '11': ['d36'],
        '12': ['da4'],
        '13': ['da6'],
        '14': ['db4'],
        '15': ['db6'],
    }
    addresses = dict()
    signature = [
        {
            'name': 'model',
            'position': [-30, -28],
            'items': {
                'Dooya': '9a',
            }
        },
        {
            'name': 'model',
            'position': [-30, -22],
            'unknown': True,
            'items': models
        },
        {
            'name': 'di',
            'unknown': True,
            'position': [-30, -6],
            'items': addresses
        },
        {
            'name': 'address',
            'unknown': True,
            'position': [-22, -9],
            'items': addresses
        },
        {
            'name': 'channel',
            # 'unknown': True,
            'position': [-9, -6],
            'items': channels
        },
        {
            'name': 'command',
            'position': [-6, None],
            'items': commands
        }
    ]

    def __init__(self, **kwargs):
        self.address = None
        self.command = None
        self.model = None
        self.channel = None
        pass

    def up(self):
        return ''

    def __str__(self):
        return '{0} {1} {2} {3} {4}'.format(self.name, self.model, self.address, self.channel, self.command)
