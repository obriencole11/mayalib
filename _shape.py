'''
A module for creating custom shape curves.

Curves operate with a set of data, in which we can create curves from.
The data is structured like so:

data = [
    {
        'cvs': [(0,0,0), ...],
        'knots': [0,0,0],
        'degree': 3
    },
    {...}
]

'''

import math
import pymel.core as pmc
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt
import maya.api.OpenMaya as om
from pymel.internal.factories import virtualClasses

##### UTILITY FUNCTIONS #####



def get_data(node):
    '''
    Retrieves shape data from a node.
    :param node: A transform node with a shape.
    :return: A correctly formatted set of shape data.
    '''

    assert isinstance(node, nt.Transform), 'Node must be a Transform, received: %s' % str(type(node))
    assert len(node.getShapes()) > 0, 'No shape found.'

    data = []
    for shape in node.getShapes():
        shape_data = {}
        shape_data['cvs'] = shape.getCVs()
        shape_data['knots'] = shape.getKnots()
        shape_data['degree'] = shape.degree()
        data.append(shape_data)

    return data

def print_data(node):

    data = get_data(node)
    data_string = "%s" % data
    data_string.replace(', ', ',\n ')
    data_string.replace('[', '[\n\t')
    data_string.replace('{', '{\n\t')
    print data_string

def create_shape_from_data(data):
    '''
    Creates a new shape from the input data.
    This is really a redundant method as you can just call Shape(data), however its a bit more clear.
    :param data: A correctly formatted set of shape data.
    :return: The Transform node of the new shape.
    '''

    assert isinstance(data, list), 'Data must be a list, received: %s' % str(type(data))
    return ControlCurve(data=data).parent

def set_shape_from_data(node, data):
    '''
    Switches the shape of an existing Transform node with a shape.
    Again, this is partially redundant but is a bit more clear.
    :param node: A Transform node with at least one shape.
    :param data: A correctly formatted set of shape data.
    :return: The Shape class
    '''

    assert isinstance(node, nt.Transform), 'Node must be a Transform, received: %s' % str(type(node))
    assert len(node.getShapes()) > 0, 'No shape found.'
    assert isinstance(data, list), 'Data must be a list, received: %s' % str(type(data))

    return ControlCurve(data=data, parent=node)

def set_shape_color(node, color):
    '''
    Changes the color of the specified node.
    :param node: A Transform with at least one shape node.
    :param color: The pymel color to swap to.
    '''

    assert isinstance(node, nt.Transform), 'Node must be a Transform, received: %s' % str(type(node))
    assert len(node.getShapes()) > 0, 'No shape found.'

    for shape in node.getShapes():
        shape.overrideEnabled.set(True)
        shape.overrideRGBColors.set(True)
        shape.overrideColorRGB.set(color)


##### CLASSES #####

class ControlCurve(nt.Transform):
    '''
    This wraps the pymel transform class, adding a curve on creation.
    Additionally the class features utility methods for manipulating the curve, changing size, color, ect.
    '''

    _shapeID = 'ControlCurve'
    _data = [
        {
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
    ]


    ##### Pymel Class Methods #####

    @classmethod
    def _isVirtual(cls, obj, name, data=None, color=None, scale_offset=None, rotate_offset=None, translate_offset=None):
        '''
        Pymel calls this method to confirm if the input object can be wrapped.
        :param obj: The input dag node.
        :param name: The name for the node.
        :param color: The color for the control curve.
        '''

        fn = pmc.api.MFnDependencyNode(obj)
        try:
            return fn.hasAttribute(cls._shapeID)
        except: pass
        return False

    @classmethod
    def _preCreateVirtual(cls, **kwargs):
        '''
        This is called right before node creation and gives us a chance to set input arguments.
        :param kwargs: The input arguments.
        :return: Two dictionaries. One containing args for pymel, the other is sent to _postCreateVirtual
        '''

        if 'name' not in kwargs and 'n' not in kwargs:
            kwargs['name'] = cls._shapeID
        if 'data' not in kwargs:
            kwargs['data'] = cls._data
        if 'color' not in kwargs:
            kwargs['color'] = dt.Color.blue
        if 'scale_offset' not in kwargs:
            kwargs['scale_offset'] = (1,1,1)
        if 'rotate_offset' not in kwargs:
            kwargs['rotate_offset'] = (0,0,0)
        if 'translate_offset' not in kwargs:
            kwargs['translate_offset'] = (0,0,0)

        postKwargs = {}

        postKwargs['data'] = kwargs.pop('data')
        postKwargs['color'] = kwargs.pop('color')
        postKwargs['scale_offset'] = kwargs.pop('scale_offset')
        postKwargs['translate_offset'] = kwargs.pop('translate_offset')
        postKwargs['rotate_offset'] = kwargs.pop('rotate_offset')

        return kwargs, postKwargs

    @classmethod
    def _postCreateVirtual(cls, newNode, **kwargs):
        '''
        This is called after the new node has been created and gives us a chance to modify it.
        :param newNode: The newly created node.
        :param kwargs: The arguments from _preCreateVirtual
        '''

        newNode.addAttr(cls._shapeID)
        data = kwargs.get('data')
        color = kwargs.get('color')
        cls._set_shape(newNode, data)
        cls._set_color(newNode, color)
        cls._add_scale(newNode, kwargs.get('scale_offset'))
        cls._add_rotate(newNode, kwargs.get('rotate_offset'))
        cls._add_translate(newNode, kwargs.get('translate_offset'))


    ##### Private Class Methods #####

    @classmethod
    def _set_shape(cls, node, data):
        '''
        Sets the target nodes shape to match the input data.
        This is a class method so that it can be called during _postCreate
        :param node: The node to modify.
        :param data: The curve data.
        '''
        for shape in node.getShapes():
            pmc.delete(shape, shape=True)
        for shape in data:
            curve = pmc.curve(p=shape['cvs'], k=shape['knots'], d=shape['degree'])
            pmc.parent(curve.getShape(), node, shape=True, r=True)
            pmc.delete(curve)

    @classmethod
    def _add_scale(cls, node, scale):
        matrix = dt.TransformationMatrix()
        matrix.addScale(scale, space='world')
        cls._add_transformation(node, matrix)

    @classmethod
    def _add_translate(cls, node, translation):
        if not isinstance(translation, list):
            translation = dt.Vector(translation)
        translation *= 100

        matrix = dt.TransformationMatrix()
        matrix.addTranslation(translation, space='world')
        cls._add_transformation(node, matrix)

    @classmethod
    def _add_rotate(cls, node, rotation):
        rotation = dt.EulerRotation([axis for axis in rotation])
        matrix = dt.TransformationMatrix()

        q = rotation.asQuaternion()
        matrix.addRotationQuaternion(q.x, q.y, q.z, q.w, space='object')
        cls._add_transformation(node, matrix)

    @classmethod
    def _add_transformation(cls, node, matrix):
        for shape in node.getShapes():
            cvs = shape.getCVs()
            new_cvs = [cv * matrix for cv in cvs]
            shape.setCVs(new_cvs)
            shape.updateCurve()

    @classmethod
    def _set_color(cls, node, color):
        '''
        Sets the color of the target node.
        This is a classmethod so that it can be called during _postCreate.
        :param node: The node to modify.
        :param color: The color to switch to.
        '''
        for shape in node.getShapes():
            shape.overrideEnabled.set(True)
            shape.overrideRGBColors.set(True)
            shape.overrideColorRGB.set(color)


    ##### Public Methods #####

    def setColor(self, color):
        self._set_color(self, color)

    def setShape(self, data):
        self._set_shape(self, data)

    def scaleShapeBy(self, scale):
        self._add_scale(self, scale)

    def rotateShapeBy(self, rotation):
        self._add_rotate(self, rotation)

    def translateShapeBy(self, translation):
        self._add_translate(self, translation)

    def getBuffers(self):

        index = 1
        buffers = []
        while True:
            buffer = self.getBufferAt(index)
            if buffer:
                buffers.append(buffer)
                index += 1
            else:
                break

        return buffers

    def getTopBuffer(self):
        if len(self.getBuffers()) > 0:
            return self.getBuffers()[-1]
        else:
            return self

    def getBufferAt(self, index):
        parent = self.getParent(index)

        if parent and parent.name().endswith('BUF'):
            return parent
        else:
            return None

    def translateBuffer(self, index, translation):
        if not isinstance(translation, list):
            translation = dt.Vector(translation)
        translation *= 100

        buffer = self.get_buffer_at(index)
        buffer_child = self.get_buffer_at(index - 1)
        if not buffer_child:
            buffer_child = self.control_curve

        matrix = dt.TransformationMatrix()
        matrix.addTranslation(translation, space='world')

        buffer.setMatrix(buffer.getMatrix(worldSpace=True) * matrix, worldSpace=True)
        buffer_child.setMatrix(buffer_child.getMatrix() * matrix.asMatrixInverse())


    def addBuffer(self, suffix='BUF'):
        name = '_'.join([self.nodeName(), suffix])
        buffer = pmc.group(empty=True, name=name)
        buffer.setMatrix(self.getTopBuffer().getMatrix(worldSpace=True), worldSpace=True)
        pmc.parent(buffer, self.getTopBuffer().getParent())
        pmc.parent(self.getTopBuffer(), buffer)
        return buffer

    def match(self, node):
        self.setMatrix(node.getMatrix(worldSpace=True), worldSpace=True)


virtualClasses.register(ControlCurve, nameRequired=False )

##### SHAPE PRESETS #####

class LocatorCurve(ControlCurve):
    _shapeID = 'LocatorCurve'
    _data = [
        {
            'knots': [0.0, 1.0], 'cvs': [dt.Point([0.0, 0.0, -25.0]), dt.Point([0.0, 0.0, 25.0])], 'degree': 1}, {'knots': [0.0, 1.0], 'cvs': [dt.Point([0.0, 25.0, 0.0]), dt.Point([0.0, -25.0, 0.0])], 'degree': 1}, {'knots': [0.0, 1.0], 'cvs': [dt.Point([25.0, 0.0, 0.0]), dt.Point([-25.0, 0.0, 0.0])], 'degree': 1}]

class Circle(ControlCurve):
    _shapeID = 'Circle'
    _data = [
        {
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
    ]
virtualClasses.register(Circle, nameRequired=False)

class Triangle(ControlCurve):
    _shapeID = 'Triangle'
    _data = [
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
    ]
virtualClasses.register(Triangle, nameRequired=False)

class Starburst(ControlCurve):
    _shapeID = 'StarBurst'
    _data = [
        {
            "knots": [
                0.0,
                0.19603428065912118,
                0.39206856131824236,
                0.5881028419773635,
                0.7841371226364847,
                0.9801714032956059,
                1.176205683954727,
                1.3722399646138481,
                1.5682742452729692,
                1.7643085259320903,
                1.9603428065912114,
                2.1563770872503327,
                2.352411367909454,
                2.5484456485685754,
                2.7444799292276967,
                2.9405142098868176,
                3.1365484905459384,
                3.3325827712050593,
                3.52861705186418,
                3.724651332523301,
                3.9206856131824224,
                4.116719893841544,
                4.312754174500665,
                4.508788455159785,
                4.704822735818906,
                4.900857016478027,
                5.096891297137148,
                5.292925577796269,
                5.48895985845539,
                5.684994139114511,
                5.8810284197736316,
                6.077062700432752,
                6.273096981091873
            ],
            "cvs": [
                [
                    -4.2960347312131776e-17,
                    4.505183215544229e-17,
                    -0.7357522542305117
                ],
                [
                    -0.1950903220161282,
                    6.005577771483278e-17,
                    -0.9807852804032304
                ],
                [
                    -0.28156019801928445,
                    4.162246563054696e-17,
                    -0.6797464486826104
                ],
                [
                    -0.5555702330196022,
                    5.091282996473014e-17,
                    -0.8314696123025452
                ],
                [
                    -0.5202554082396837,
                    3.1856456021991396e-17,
                    -0.5202554082396837
                ],
                [
                    -0.8314696123025451,
                    3.401886537845025e-17,
                    -0.5555702330196022
                ],
                [
                    -0.6797464486826102,
                    1.7240589763580565e-17,
                    -0.2815601980192845
                ],
                [
                    -0.9807852804032302,
                    1.1945836920083896e-17,
                    -0.1950903220161283
                ],
                [
                    -0.7357522542305113,
                    1.0145165574887427e-32,
                    -1.5923776969841639e-16
                ],
                [
                    -0.9807852804032302,
                    -1.1945836920083884e-17,
                    0.19509032201612808
                ],
                [
                    -0.6797464486826102,
                    -1.7240589763580555e-17,
                    0.28156019801928434
                ],
                [
                    -0.831469612302545,
                    -3.4018865378450236e-17,
                    0.555570233019602
                ],
                [
                    -0.5202554082396836,
                    -3.1856456021991383e-17,
                    0.5202554082396835
                ],
                [
                    -0.5555702330196021,
                    -5.0912829964730115e-17,
                    0.8314696123025449
                ],
                [
                    -0.28156019801928445,
                    -4.162246563054694e-17,
                    0.6797464486826101
                ],
                [
                    -0.19509032201612825,
                    -6.005577771483274e-17,
                    0.9807852804032299
                ],
                [
                    -1.7390646627634521e-16,
                    -4.5051832155442255e-17,
                    0.735752254230511
                ],
                [
                    0.19509032201612803,
                    -6.005577771483274e-17,
                    0.9807852804032299
                ],
                [
                    0.2815601980192841,
                    -4.162246563054694e-17,
                    0.6797464486826101
                ],
                [
                    0.5555702330196017,
                    -5.09128299647301e-17,
                    0.8314696123025447
                ],
                [
                    0.5202554082396833,
                    -3.185645602199137e-17,
                    0.5202554082396833
                ],
                [
                    0.8314696123025446,
                    -3.401886537845023e-17,
                    0.5555702330196018
                ],
                [
                    0.6797464486826098,
                    -1.7240589763580558e-17,
                    0.28156019801928445
                ],
                [
                    0.9807852804032295,
                    -1.1945836920083898e-17,
                    0.19509032201612833
                ],
                [
                    0.7357522542305107,
                    -6.626048435718203e-33,
                    1.146569405524477e-16
                ],
                [
                    0.9807852804032295,
                    1.1945836920083869e-17,
                    -0.19509032201612783
                ],
                [
                    0.6797464486826098,
                    1.7240589763580537e-17,
                    -0.281560198019284
                ],
                [
                    0.8314696123025445,
                    3.40188653784502e-17,
                    -0.5555702330196014
                ],
                [
                    0.5202554082396832,
                    3.185645602199135e-17,
                    -0.5202554082396829
                ],
                [
                    0.5555702330196017,
                    5.091282996473007e-17,
                    -0.8314696123025441
                ],
                [
                    0.2815601980192844,
                    4.1622465630546905e-17,
                    -0.6797464486826095
                ],
                [
                    0.19509032201612836,
                    6.005577771483269e-17,
                    -0.9807852804032291
                ],
                [
                    1.8167315328117634e-16,
                    4.505183215544223e-17,
                    -0.7357522542305105
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Starburst, nameRequired=False)

class Cross(ControlCurve):
    _shapeID = 'Cross'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0
            ],
            "cvs": [
                [
                    -0.5,
                    0.0,
                    1.0
                ],
                [
                    -0.5,
                    0.0,
                    0.5
                ],
                [
                    -1.0,
                    0.0,
                    0.5
                ],
                [
                    -1.0,
                    0.0,
                    -0.5
                ],
                [
                    -0.5,
                    0.0,
                    -0.5
                ],
                [
                    -0.5,
                    0.0,
                    -1.0
                ],
                [
                    0.5,
                    0.0,
                    -1.0
                ],
                [
                    0.5,
                    0.0,
                    -0.5
                ],
                [
                    1.0,
                    0.0,
                    -0.5
                ],
                [
                    1.0,
                    0.0,
                    0.5
                ],
                [
                    0.5,
                    0.0,
                    0.5
                ],
                [
                    0.5,
                    0.0,
                    1.0
                ],
                [
                    -0.5,
                    0.0,
                    1.0
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Cross, nameRequired=False )

class Sphere(ControlCurve):
    _shapeID = 'Sphere'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0
            ],
            "cvs": [
                [
                    -0.5,
                    0.0,
                    1.0
                ],
                [
                    -0.5,
                    0.0,
                    0.5
                ],
                [
                    -1.0,
                    0.0,
                    0.5
                ],
                [
                    -1.0,
                    0.0,
                    -0.5
                ],
                [
                    -0.5,
                    0.0,
                    -0.5
                ],
                [
                    -0.5,
                    0.0,
                    -1.0
                ],
                [
                    0.5,
                    0.0,
                    -1.0
                ],
                [
                    0.5,
                    0.0,
                    -0.5
                ],
                [
                    1.0,
                    0.0,
                    -0.5
                ],
                [
                    1.0,
                    0.0,
                    0.5
                ],
                [
                    0.5,
                    0.0,
                    0.5
                ],
                [
                    0.5,
                    0.0,
                    1.0
                ],
                [
                    -0.5,
                    0.0,
                    1.0
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Sphere, nameRequired=False )

class Cube(ControlCurve):
    _shapeID = 'Cube'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0
            ],
            "cvs": [
                [
                    0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    -0.5
                ],
                [
                    0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    -0.5
                ],
                [
                    0.5,
                    -0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    -0.5
                ],
                [
                    -0.5,
                    -0.5,
                    0.5
                ],
                [
                    -0.5,
                    0.5,
                    0.5
                ],
                [
                    -0.5,
                    -0.5,
                    0.5
                ],
                [
                    0.5,
                    -0.5,
                    0.5
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Cube, nameRequired=False)

class Arrow(ControlCurve):
    _shapeID = 'Arrow'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0
            ],
            "cvs": [
                [
                    -0.4,
                    0.0,
                    0.0
                ],
                [
                    -0.4,
                    0.0,
                    1.2000000000000002
                ],
                [
                    -0.8,
                    0.0,
                    1.2000000000000002
                ],
                [
                    0.0,
                    0.0,
                    2.0
                ],
                [
                    0.8,
                    0.0,
                    1.2000000000000002
                ],
                [
                    0.4,
                    0.0,
                    1.2000000000000002
                ],
                [
                    0.4,
                    0.0,
                    0.0
                ],
                [
                    -0.4,
                    0.0,
                    0.0
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Arrow, nameRequired=False)

class Trapezoid(ControlCurve):
    _shapeID = 'Trapezoid'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0
            ],
            "cvs": [
                [
                    -1.0,
                    0.0,
                    2.0
                ],
                [
                    -2.0,
                    0.0,
                    -2.0
                ],
                [
                    2.0,
                    0.0,
                    -2.0
                ],
                [
                    1.0,
                    0.0,
                    2.0
                ],
                [
                    -1.0,
                    0.0,
                    2.0
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Trapezoid, nameRequired=False)

class Star(ControlCurve):
    _shapeID = 'Star'
    _data = [
        {
            "knots": [
                0.0,
                0.6180339887498948,
                1.2360679774997898,
                1.8541019662496847,
                2.4721359549995796,
                3.0901699437494745,
                3.7082039324993694,
                4.326237921249264,
                4.944271909999159,
                5.562305898749054,
                6.180339887498949
            ],
            "cvs": [
                [
                    6.123233995736766e-17,
                    6.123233995736766e-17,
                    -1.0
                ],
                [
                    -0.25721542377496187,
                    2.1677880734809045e-17,
                    -0.3540266589501904
                ],
                [
                    -0.9510565162951536,
                    1.8921833652170756e-17,
                    -0.3090169943749475
                ],
                [
                    -0.4161832980985968,
                    -8.280213636630507e-18,
                    0.1352261507954053
                ],
                [
                    -0.5877852522924731,
                    -4.953800363085458e-17,
                    0.8090169943749475
                ],
                [
                    -2.6795334196357118e-17,
                    -2.6795334196357118e-17,
                    0.4376010163095678
                ],
                [
                    0.5877852522924731,
                    -4.953800363085458e-17,
                    0.8090169943749475
                ],
                [
                    0.4161832980985968,
                    -8.280213636630514e-18,
                    0.1352261507954053
                ],
                [
                    0.9510565162951536,
                    1.8921833652170747e-17,
                    -0.30901699437494734
                ],
                [
                    0.25721542377496187,
                    2.1677880734809045e-17,
                    -0.3540266589501904
                ],
                [
                    6.123233995736766e-17,
                    6.123233995736766e-17,
                    -1.0
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Star, nameRequired=False)

class Octohedron(ControlCurve):
    _shapeID = 'Octohedron'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0
            ],
            "cvs": [
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    1.0,
                    2.220446049250313e-16
                ],
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ],
                [
                    1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    2.220446049250313e-16,
                    -1.0
                ],
                [
                    0.0,
                    1.0,
                    2.220446049250313e-16
                ],
                [
                    -1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    -2.220446049250313e-16,
                    1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ],
                [
                    -1.0,
                    0.0,
                    0.0
                ],
                [
                    0.0,
                    2.220446049250313e-16,
                    -1.0
                ],
                [
                    0.0,
                    -1.0,
                    -2.220446049250313e-16
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Octohedron, nameRequired=False)

class FourArrow(ControlCurve):
    _shapeID = 'Four-Arrow'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0,
                9.0,
                10.0,
                11.0,
                12.0,
                13.0,
                14.0,
                15.0,
                16.0,
                17.0,
                18.0,
                19.0,
                20.0,
                21.0,
                22.0,
                23.0,
                24.0
            ],
            "cvs": [
                [
                    -0.333,
                    0.0,
                    0.33
                ],
                [
                    -0.333,
                    0.0,
                    1.32
                ],
                [
                    -0.666,
                    0.0,
                    1.32
                ],
                [
                    0.0,
                    0.0,
                    1.98
                ],
                [
                    0.666,
                    0.0,
                    1.32
                ],
                [
                    0.333,
                    0.0,
                    1.32
                ],
                [
                    0.333,
                    0.0,
                    0.33
                ],
                [
                    1.332,
                    0.0,
                    0.33
                ],
                [
                    1.332,
                    0.0,
                    0.66
                ],
                [
                    1.9980000000000002,
                    0.0,
                    0.0
                ],
                [
                    1.332,
                    0.0,
                    -0.66
                ],
                [
                    1.332,
                    0.0,
                    -0.33
                ],
                [
                    0.333,
                    0.0,
                    -0.33
                ],
                [
                    0.333,
                    0.0,
                    -1.32
                ],
                [
                    0.666,
                    0.0,
                    -1.32
                ],
                [
                    0.0,
                    0.0,
                    -1.98
                ],
                [
                    -0.666,
                    0.0,
                    -1.32
                ],
                [
                    -0.333,
                    0.0,
                    -1.32
                ],
                [
                    -0.333,
                    0.0,
                    -0.33
                ],
                [
                    -1.332,
                    0.0,
                    -0.33
                ],
                [
                    -1.332,
                    0.0,
                    -0.66
                ],
                [
                    -1.9980000000000002,
                    0.0,
                    0.0
                ],
                [
                    -1.332,
                    0.0,
                    0.66
                ],
                [
                    -1.332,
                    0.0,
                    0.33
                ],
                [
                    -0.333,
                    0.0,
                    0.33
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(FourArrow, nameRequired=False)

class Tetrahedron(ControlCurve):
    _shapeID = 'Tetrahedron'
    _data = [
        {
            "knots": [
                0.0,
                1.0,
                2.0,
                3.0,
                4.0,
                5.0,
                6.0,
                7.0,
                8.0
            ],
            "cvs": [
                [
                    1.0,
                    -0.7071067690849304,
                    -1.5700924318127872e-16
                ],
                [
                    0.0,
                    0.7071067690849304,
                    1.5700924318127872e-16
                ],
                [
                    -0.5,
                    -0.7071067690849304,
                    -0.8660253882408142
                ],
                [
                    -0.5,
                    -0.7071067690849304,
                    0.8660253882408142
                ],
                [
                    0.0,
                    0.7071067690849304,
                    1.5700924318127872e-16
                ],
                [
                    1.0,
                    -0.7071067690849304,
                    -1.5700924318127872e-16
                ],
                [
                    -0.5,
                    -0.7071067690849304,
                    0.8660253882408142
                ],
                [
                    1.0,
                    -0.7071067690849304,
                    -1.5700924318127872e-16
                ],
                [
                    -0.5,
                    -0.7071067690849304,
                    -0.8660253882408142
                ]
            ],
            "degree": 1
        }
    ]
virtualClasses.register(Tetrahedron, nameRequired=False)
