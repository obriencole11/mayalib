import pymel.core as pmc
import maya.cmds as cmds
from context_library import UndoOnError
from nodes import ControlCurve

def build_fk_chain(targets, name='Unnamed'):
    with UndoOnError():
        previous_target = None
        controls = []
        for i, target in enumerate(targets):
            name = '_'.join([target.name(), 'CTRL'])
            ctrl = ControlCurve.create(name, 'circle')
            ctrl.rotateShape([0,0,90])
            ctrl.scaleShape([10,10,10])
            cmds.matchTransform(ctrl, target.name())
            if previous_target:
                pmc.parent(ctrl, previous_target)
            previous_target = ctrl
            ctrl.addBuffer()
            pmc.parentConstraint(ctrl, target, mo=True)
            controls.append(ctrl)
        return [controls[0].getTopBuffer()]


def build_ik_chain(targets, name='Unnamed'):
    with UndoOnError():

        start_joint = targets[0]
        pole_joint = targets[0].getChildren()[0]
        end_joint = targets[1]

        handle = pmc.ikHandle(sj=start_joint, ee=end_joint)[0]
        pmc.hide(handle)

        ik_ctrl = ControlCurve.create(name=name + '_Ik_CTRL', shapeType='circle')
        ik_ctrl.scaleShape([10,10,10])
        ik_ctrl.setTranslation(end_joint.getTranslation(worldSpace=True), worldSpace=True)
        ik_ctrl.addBuffer()
        ik_ctrl.lockTransform(scale=True, hide=True)
        pmc.orientConstraint(ik_ctrl, end_joint, mo=True)
        pmc.parent(handle, ik_ctrl)

        start_ctrl = ControlCurve.create(name=name + '_Base_CTRL', shapeType='circle')
        start_ctrl.scaleShape([10,10,10])
        start_ctrl.setMatrix(start_joint.getMatrix(worldSpace=True), worldSpace=True)
        start_ctrl.addBuffer()
        start_ctrl.lockTransform(rotate=True, scale=True, hide=True)
        pmc.parentConstraint(start_ctrl, start_joint, mo=True)

        pole_ctrl = ControlCurve.create(name=name + '_Pole_CTRL', shapeType='octohedron')
        pole_ctrl.scaleShape([10,10,10])
        pole_ctrl.setTranslation(pole_joint.getTranslation(worldSpace=True), worldSpace=True)
        pole_ctrl.addBuffer()
        pole_ctrl.lockTransform(rotate=True, scale=True, hide=True)
        pmc.poleVectorConstraint(pole_ctrl, handle)

        return ik_ctrl, pole_ctrl, start_ctrl

def build_quad_leg(targets, name='Unnamed'):
    with UndoOnError():
        assert len(targets) >= 2, 'Not enough valid targets for quad leg.'

        ik_ctrl, pole_ctrl, base_ctrl = build_ik_chain([targets[0], targets[2]], name)

        ik_ctrl.visibility.set(0)

        foot_ctrl = ControlCurve.create(name=name + '_Foot_CTRL', shapeType='cube')
        foot_ctrl.scaleShape([20,20,20])
        foot_ctrl.match(targets[-1].name(), rotation=False)
        foot_ctrl.lockTransform(scale=True, hide=True)
        foot_ctrl.addBuffer()

        hoc_ctrl = ControlCurve.create(name=name + '_Hoc_CTRL', shapeType='circle')
        hoc_ctrl.scaleShape([10,10,10])
        hoc_ctrl.lockTransform(translate=True, scale=True, hide=True)
        hoc_ctrl.rotateShape([0,0,90])
        hoc_ctrl.match(targets[-1].name())

        toe_ctrl = ControlCurve.create(name=name + '_Toe_CTRL', shapeType='circle')
        toe_ctrl.scaleShape([10, 10, 10])
        toe_ctrl.rotateShape([0,0,90])
        toe_ctrl.lockTransform(translate=True, scale=True, hide=True)
        toe_ctrl.match(targets[-1].name())

        pmc.parent([hoc_ctrl, toe_ctrl], foot_ctrl)
        hoc_ctrl.addBuffer()
        toe_ctrl.addBuffer()

        pmc.parentConstraint(hoc_ctrl, ik_ctrl, mo=True)
        pmc.parentConstraint(toe_ctrl, targets[-1], mo=True)

        return [ik_ctrl, pole_ctrl, base_ctrl, foot_ctrl]