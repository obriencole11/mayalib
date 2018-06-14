import maya.cmds as cmds
import maya.api.OpenMaya as om
import pymel.core as pmc
from context_library import UndoOnError
import pprint
import math


class Attribute(object):

    def __init__(self, attr_name):
        self._node = attr_name.split('.')[0]
        self._attr = attr_name

    def get(self, **kwargs):
        return cmds.getAttr(self._attr, **kwargs)

    def set(self, value, **kwargs):
        return cmds.setAttr(self._attr, value, **kwargs)

    def connect(self, target_attr, **kwargs):
        cmds.connectAttr(self._attr, target_attr, **kwargs)

    def hide(self):
        return cmds.setAttr(self._attr, k=False, cb=False)

    def lock(self):
        return cmds.setAttr(self._attr, lock=True)

    def unlock(self):
        return cmds.setAttr(self._attr, lock=False)


class Node(object):

    _name = 'Node'

    def __init__(self, node):
        if isinstance(node, om.MObject):
            self._node = self._getName(node)
        elif isinstance(node, pmc.PyNode):
            self._node = node.name()
        elif isinstance(node, str) or isinstance(node, unicode):
            self._node = str(node)
        else:
            raise AssertionError('Invalid type for Transform, received: %s' % str(type(node)))

        assert cmds.objExists(self._node), 'Specified node does not exist: %s' % self._node

    def __str__(self):
        return self._node

    def __getattr__(self, attr):
        if self.hasAttr(attr):
            return self.attr(attr)
        raise AttributeError('%s does not have attribute: %s' % (self._node, attr))

    def _getName(self, mObject):
        return om.MFnDependencyNode(mObject).name()

    def _getMDagPath(self, node):
        selList = om.MSelectionList()
        selList.add(node)
        return selList.getDagPath(0)

    def _getMObject(self, node):
        selList = om.MSelectionList()
        selList.add(node)
        return selList.getDependNode(0)

    def attr(self, attr):
        if self.hasAttr(attr):
            return Attribute('%s.%s' % (self._node, attr))

    def hasAttr(self, attr):
        return cmds.attributeQuery(attr, node=self._node, exists=True)

    def getAttr(self, attr, **kwargs):
        return cmds.getAttr('%s.%s' % (self._node, attr), **kwargs)

    def setAttr(self, attr, value, **kwargs):
        return cmds.setAttr('%s.%s' % (self._node, attr), value, **kwargs)

    def addAttr(self, attr, **kwargs):
        return cmds.addAttr(self._node, ln=attr, **kwargs)

    @property
    def mFnDagNode(self):
        return om.MFnDagNode(self.dagPath)

    @property
    def dagPath(self):
        selList = om.MSelectionList()
        selList.add(self._node)
        return selList.getDagPath(0)

    @property
    def mObject(self):
        selList = om.MSelectionList()
        selList.add(self._node)
        return selList.getDependNode(0)

    @property
    def node(self):
        return pmc.PyNode(self._node)

    @property
    def name(self):
        return self._node

    @property
    def nodeName(self):
        name = (self.name).split('|')[-1]
        name = (name).split(':')[-1]
        return name

class ShapeData(list):

    @classmethod
    def create(cls, node):
        node = ControlCurve(node)
        data = node.getShapeData()
        return cls(data)

    @classmethod
    def circle(cls):
        return cls([{
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
    ])

    @classmethod
    def triangle(cls):
        return cls([
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
        }])

    @classmethod
    def locator(cls):
        return cls([
        {'cvs': [[0.0, 0.0, -25.0], [0.0, 0.0, 25.0]],
          'degree': 1,
          'knots': [0.0, 1.0]},
         {'cvs': [[0.0, 25.0, 0.0], [0.0, -25.0, 0.0]],
          'degree': 1,
          'knots': [0.0, 1.0]},
         {'cvs': [[25.0, 0.0, 0.0], [-25.0, 0.0, 0.0]],
          'degree': 1,
          'knots': [0.0, 1.0]}
    ])

    @classmethod
    def starburst(cls):
        return cls([
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
    ])

    @classmethod
    def cross(cls):
        return cls([
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
    ])

    @classmethod
    def sphere(cls):
        return cls(
            [{'cvs': [[0.7836116248912245, 4.798237340988473e-17, -0.7836116248912246],
                      [6.785732323110912e-17,
                       6.785732323110912e-17,
                       -1.1081941875543877],
                      [-0.7836116248912245, 4.798237340988472e-17, -0.7836116248912244],
                      [-1.1081941875543881,
                       3.517735619006027e-33,
                       -5.74489823752483e-17],
                      [-0.7836116248912245, -4.7982373409884725e-17, 0.7836116248912245],
                      [-1.1100856969603225e-16,
                       -6.785732323110917e-17,
                       1.1081941875543884],
                      [0.7836116248912245, -4.798237340988472e-17, 0.7836116248912244],
                      [1.1081941875543881,
                       -9.253679210110099e-33,
                       1.511240500779959e-16],
                      [0.7836116248912245, 4.798237340988473e-17, -0.7836116248912246],
                      [6.785732323110912e-17,
                       6.785732323110912e-17,
                       -1.1081941875543877],
                      [-0.7836116248912245, 4.798237340988472e-17, -0.7836116248912244]],
              'degree': 3,
              'knots': [-2.0,
                        -1.0,
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
                        10.0]},
             {'cvs': [[0.7836116248912245, -0.7836116248912246, -2.2197910707351852e-16],
                      [6.785732323110912e-17,
                       -1.1081941875543877,
                       -3.1392586378683917e-16],
                      [-0.7836116248912245,
                       -0.7836116248912244,
                       -2.2197910707351847e-16],
                      [-1.1081941875543881,
                       -5.74489823752483e-17,
                       -1.6273972213863125e-32],
                      [-0.7836116248912245, 0.7836116248912245, 2.219791070735185e-16],
                      [-1.1100856969603225e-16,
                       1.1081941875543884,
                       3.1392586378683937e-16],
                      [0.7836116248912245, 0.7836116248912244, 2.2197910707351847e-16],
                      [1.1081941875543881,
                       1.511240500779959e-16,
                       4.2809959204349347e-32],
                      [0.7836116248912245, -0.7836116248912246, -2.2197910707351852e-16],
                      [6.785732323110912e-17,
                       -1.1081941875543877,
                       -3.1392586378683917e-16],
                      [-0.7836116248912245,
                       -0.7836116248912244,
                       -2.2197910707351847e-16]],
              'degree': 3,
              'knots': [-2.0,
                        -1.0,
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
                        10.0]},
             {'cvs': [[-4.798237340988475e-17, -0.7836116248912246, -0.7836116248912245],
                      [-3.1392586378683917e-16,
                       -1.1081941875543877,
                       -6.78573232311092e-17],
                      [-3.9597584073715224e-16, -0.7836116248912244, 0.7836116248912245],
                      [-2.4606854055573016e-16,
                       -5.74489823752483e-17,
                       1.1081941875543881],
                      [4.7982373409884725e-17, 0.7836116248912245, 0.7836116248912245],
                      [3.1392586378683937e-16,
                       1.1081941875543884,
                       1.1100856969603232e-16],
                      [3.9597584073715224e-16, 0.7836116248912244, -0.7836116248912245],
                      [2.460685405557302e-16,
                       1.511240500779959e-16,
                       -1.1081941875543881],
                      [-4.798237340988475e-17, -0.7836116248912246, -0.7836116248912245],
                      [-3.1392586378683917e-16,
                       -1.1081941875543877,
                       -6.78573232311092e-17],
                      [-3.9597584073715224e-16, -0.7836116248912244, 0.7836116248912245]],
              'degree': 3,
              'knots': [-2.0,
                        -1.0,
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
                        10.0]}]
        )

    @classmethod
    def cube(cls):
        return cls([
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
    ])

    @classmethod
    def arrow(cls):
        return cls([
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
    ])

    @classmethod
    def trapezoid(cls):
        return cls([
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
    ])

    @classmethod
    def star(cls):
        return cls([
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
    ])

    @classmethod
    def octohedron(cls):
        return cls([
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
    ])

    @classmethod
    def square(cls):
        return cls(
            [{'cvs': [[-25.0, 0.0, 25.0],
                      [-25.0, 0.0, -25.0],
                      [25.0, 0.0, -25.0],
                      [25.0, 0.0, 25.0],
                      [-25.0, 0.0, 25.0]],
              'degree': 1,
              'knots': [0.0, 1.0, 2.0, 3.0, 4.0]}]
        )

    @classmethod
    def fourarrow(cls):
        return cls([
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
    ])

    @classmethod
    def tetrahedron(cls):
        return cls([
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
    ])

    def __init__(self, data):
        list.__init__([])
        self.extend(data)

    def __str__(self):
        return pprint.pformat(self)

    @property
    def cvs(self):
        return [shape['cvs'] for shape in self]

    @cvs.setter
    def cvs(self, value):
        for i, shape in enumerate(self):
            shape['cvs'] = value[i]

    def transformCVs(self, matrix):
        new_cvs = []
        for cvs in self.cvs:
            points = [om.MVector(cv) for cv in cvs]
            points = [point * matrix for point in points]
            new_cvs.append([list(point) for point in points])
        self.cvs = new_cvs

class Shape(Node):

    def getCVs(self):
        return [list(point)[:3] for point in self.mFnNurbsCurve.cvPositions(om.MSpace.kTransform)]

    def setCVs(self, points):
        self.mFnNurbsCurve.setCVPositions(points, om.MSpace.kTransform)

    def updateCurve(self):
        self.mFnNurbsCurve.updateCurve()

    def getKnots(self):
        return list(self.mFnNurbsCurve.knots())

    def getDegree(self):
        return int(self.mFnNurbsCurve.degree)

    def getData(self):
        shape_data = {}
        shape_data['cvs'] = self.getCVs()
        shape_data['knots'] = self.getKnots()
        shape_data['degree'] = self.getDegree()
        return shape_data

    def setColor(self, color):
        self.overrideEnabled.set(True)
        self.overrideRGBColors.set(True)
        self.overrideColorR.set(color[0])
        self.overrideColorG.set(color[1])
        self.overrideColorB.set(color[2])

    @property
    def mFnNurbsCurve(self):
        return om.MFnNurbsCurve(self.dagPath)

class Transform(Node):

    _name = 'Transform'

    @classmethod
    def create(cls, name=None):
        name = name or cls._name
        node = cmds.group(empty=True, name=name)
        return cls(node)

    def getParent(self, index=0):
        try:
            parent = self._getName(self.mFnDagNode.parent(index))
            if parent != 'world':
                return Transform(parent)
            else:
                return None
        except RuntimeError:
            return None

    def getBuffers(self):
        index = 0
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

        if parent and parent.hasAttr('_isBuffer'):
            return parent
        else:
            return None

    def getShapes(self):
        shapes = []
        for index in range(self.dagPath.numberOfShapesDirectlyBelow()):
            name = self._getName(self.dagPath.extendToShape(index).node())
            shapes.append(Shape(name))
        return shapes

    def addBuffer(self, name=None, suffix='BUF'):
        name = name or self.nodeName
        name = '_'.join([name, suffix])
        buffer = Transform.create(name)
        buffer.addAttr('_isBuffer', at='message')
        buffer.match(self.getTopBuffer())
        pmc.parent(buffer, self.getTopBuffer().getParent())
        pmc.parent(self.getTopBuffer(), buffer)
        return buffer

    def match(self, target_node, translation=True, rotation=True):
        target_transform = om.MFnTransform(self._getMDagPath(str(target_node)))
        matrix = om.MTransformationMatrix(om.MMatrix(cmds.xform(target_node, matrix=True, ws=1, q=True)))
        if translation:
            translation = om.MVector(target_transform.rotatePivot(om.MSpace.kWorld))
            self.setTranslation(translation, worldSpace=True)
        if rotation:
            rotation = matrix.rotation(True)
            self.mFnTransform.setRotation(rotation, om.MSpace.kWorld)

    def setTranslation(self, vector, worldSpace=False):
        space = om.MSpace.kWorld if worldSpace else om.MSpace.kObject
        vector = om.MVector(vector[0], vector[1], vector[2])
        self.mFnTransform.setTranslation(vector, space)

    def setRotation(self, rotation, worldSpace=False):
        rotation = om.MEulerRotation(rotation[0], rotation[1], rotation[2]).asQuaternion()
        space = om.MSpace.kWorld if worldSpace else om.MSpace.kObject
        self.mFnTransform.setRotation(rotation, space)

    def getMatrix(self, worldSpace=False):
        if worldSpace:
            return self.getAttr('worldMatrix')
        else:
            return self.getAttr('matrix')

    def setMatrix(self, matrix, translation=True, rotation=True, worldSpace=False):
        matrix = om.MTransformationMatrix(om.MMatrix(matrix))
        if translation:
            self.setTranslation(matrix.translation(True), worldSpace)
        if rotation:
            self.setRotation(matrix.rotation(True), worldSpace)

    def lockTransform(self, translate=False, rotate=False, scale=False, hide=False):
        def lock(prefix):
            for attr in ['x', 'y', 'z']:
                self.attr(prefix + attr).lock()
                if hide:
                    self.attr(prefix + attr).hide()
        if translate:
            lock('t')
        if rotate:
            lock('r')
        if scale:
            lock('s')

    def unlockTransform(self, translate=False, rotate=False, scale=False, hide=False):
        def unlock(prefix):
            for attr in ['x', 'y', 'z']:
                self.attr(prefix + attr).unlock()
                if hide:
                    self.attr(prefix + attr).hide()
        if translate:
            unlock('t')
        if rotate:
            unlock('r')
        if scale:
            unlock('s')

    @property
    def mFnTransform(self):
        return om.MFnTransform(self.dagPath)

    @property
    def translate(self):
        return self.getAttr('translate')

    @property
    def rotate(self):
        return self.getAttr('rotate')

    @property
    def scale(self):
        return self.getAttr('scale')


class ControlCurve(Transform):

    _name = 'ControlCurve'

    @classmethod
    def create(cls, name=None, shapeType='circle'):
        data = cls._getData(shapeType)
        name = name or cls._name
        node = ControlCurve(cmds.group(empty=True, name=name))
        node.addShape(data)
        return node

    @classmethod
    def _getData(self, shapeType):
        if isinstance(shapeType, str):
            assert shapeType in ShapeData.__dict__, 'Could not find shape data for %s' % shapeType
            return getattr(ShapeData, shapeType)()
        elif isinstance(shapeType, list):
            return shapeType
        raise TypeError('Invalid shape type %s' % shapeType)

    def copyShape(self):
        shapeData = ShapeData([shape.getData() for shape in self.shapes])
        shapeData.transformCVs(om.MMatrix(self.worldMatrix.get()))
        return shapeData

    def pasteShape(self, data):
        data.transformCVs(om.MMatrix(self.worldInverseMatrix.get()))
        self.setShape(data)

    def getShapeData(self):
        return ShapeData([shape.getData() for shape in self.shapes])

    def setShape(self, shape):
        data = self._getData(shape)
        for shape in self.shapes:
            cmds.delete(shape, shape=True)
        self.addShape(data)

    def addShape(self, shape):
        data = self._getData(shape)
        for shape in data:
            curve = Transform(cmds.curve(p=shape['cvs'], k=shape['knots'], d=shape['degree']))
            cmds.parent(curve.getShapes()[0], self._node, shape=True, r=True)
            cmds.delete(curve)

    def getColor(self):
        return self.shapes[0].overrideColorRGB.get()

    def setColor(self, color):
        for shape in self.shapes:
            shape.setColor(color)

    def translateShape(self, translation, worldSpace=False):
        matrix = om.MTransformationMatrix()
        matrix.translateBy(om.MVector(translation), om.MSpace.kWorld)
        self.transformShape(matrix.asMatrix(), worldSpace)

    def rotateShape(self, rotation, worldSpace=False):
        rotation = om.MEulerRotation([math.radians(axis) for axis in rotation]).asQuaternion()
        matrix = om.MTransformationMatrix()
        matrix.rotateBy(rotation, om.MSpace.kWorld)
        self.transformShape(matrix.asMatrix(), worldSpace)

    def scaleShape(self, scale, worldSpace=False):
        matrix = om.MTransformationMatrix()
        matrix.scaleBy(om.MVector(scale), om.MSpace.kWorld)
        self.transformShape(matrix.asMatrix(), worldSpace)

    def mirrorShape(self, vector, worldSpace=True):
        vector = [math.fabs(axis) for axis in vector]
        vector = om.MVector([1,1,1]) - om.MVector(vector).normalize() * 2
        self.scaleShape(vector, worldSpace)

    def transformShape(self, matrix, worldSpace=False):
        with UndoOnError():
            for shape in self.shapes:
                cvs = [om.MPoint(cv) for cv in shape.getCVs()]
                rotation_matrix = om.MTransformationMatrix(om.MMatrix(self.worldMatrix.get())).rotation(True).asMatrix()
                new_cvs = cvs
                if worldSpace:
                    new_cvs = [cv * rotation_matrix for cv in new_cvs]
                new_cvs = [cv * matrix for cv in new_cvs]
                if worldSpace:
                    new_cvs = [cv * rotation_matrix.inverse() for cv in new_cvs]
                shape.setCVs(new_cvs)
                shape.updateCurve()

    @property
    def shapes(self):
        return self.getShapes()
