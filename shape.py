import pymel.core as pmc
import pymel.core.datatypes as dt
import pprint

class Shape(object):

    def __init__(self, node=None, type='Circle', name=None, color=None):
        name = name if name else 'Shape'
        self.node = node if node else pmc.group(empty=True, name=name)

    @classmethod
    def get_data(cls, node):
        data = []
        for shape in node.getShapes():
            shape_data = {}
            shape_data['cvs'] = shape.getCVs()
            shape_data['knots'] = shape.getKnots()
            shape_data['degree'] = shape.degree()
            data.append(shape_data)

        return data

    @classmethod
    def get_data_string(cls, node):
        data = cls.get_data(node)
        return pprint.pformat(data)

    @classmethod
    def set_color(cls, shapes, color=dt.Color(0,0,1)):
        for shape in shapes:
            shape.overrideEnabled.set(True)
            shape.overrideRGBColors.set(True)
            shape.overrideColorRGB.set(color)

    @property
    def data(self):
        return self.get_data(self.node)

    @property
    def data_string(self):
        return self.get_data_string(self.node)

    @property
    def shapes(self):
        return self.node.getShapes()

    @property
    def name(self):
        return self.node.name()

    @property
    def color(self):
        return self.shapes[0].overrideColorRGB.get()

    @color.setter
    def color(self, value):
        self.set_color(self.shapes, value)

    def setColor(self, value):
        self.set_color(self.shapes, value)

_shape_data = {
    'Circle': [{
            'cvs': [([0.783611624891, 4.79823734099e-17, -0.783611624891]),
                     ([-1.26431706078e-16, 6.78573232311e-17, -1.10819418755]),
                     ([-0.783611624891, 4.79823734099e-17, -0.783611624891]),
                     ([-1.10819418755, 1.96633546162e-32, -3.21126950724e-16]),
                     ([-0.783611624891, -4.79823734099e-17, 0.783611624891]),
                     ([-3.33920536359e-16, -6.78573232311e-17, 1.10819418755]),
                     ([0.783611624891, -4.79823734099e-17, 0.783611624891]),
                     ([1.10819418755, -3.6446300679e-32, 5.95213259928e-16]),
                     ([0.783611624891, 4.79823734099e-17, -0.783611624891]),
                     ([-1.26431706078e-16, 6.78573232311e-17, -1.10819418755]),
                     ([-0.783611624891, 4.79823734099e-17, -0.783611624891])],
            'knots': [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0],
            'degree': 3
        }
    ],
    'Triangle':[
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0
            ],
            "cvs": [
                [
                    0.0,
                    0.0,
                    1.0
                ],
                [
                    -1.0,
                    0.0,
                    -1.0
                ],
                [
                    1.0,
                    0.0,
                    -1.0
                ],
                [
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "degree": 1
        }
    ],
    'Locator': [
        {'cvs': [dt.Point([0.0, 0.0, -25.0]), dt.Point([0.0, 0.0, 25.0])],
          'degree': 1,
          'knots': [0.0, 1.0]},
         {'cvs': [dt.Point([0.0, 25.0, 0.0]), dt.Point([0.0, -25.0, 0.0])],
          'degree': 1,
          'knots': [0.0, 1.0]},
         {'cvs': [dt.Point([25.0, 0.0, 0.0]), dt.Point([-25.0, 0.0, 0.0])],
          'degree': 1,
          'knots': [0.0, 1.0]}
    ]
}