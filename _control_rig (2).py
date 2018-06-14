'''
A utility module for creating common parts of control rigs.
This is a tricky module as since we cannot allow extra dependencies, shapes must be supplied to controls.
So this module's goal is to isolate the mechanics behind rigs, not how they're assembled or organized.
'''

import pymel.core as pmc
import pymel.core.nodetypes as nt


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


class RigComponent(object):
    '''
    This is the base class of all RigComponents.
    The goal of this is mostly to group parts together rather than represent them as a whole.
    '''

    _name = None

    def __init__(self, name):
        # Gathers settings
        self.name = name if name else self._name
        self._component_group = None

        self.controls = []
        self.groups = []
        self.support = []
        self.components = []

    def store_reference(self, source, target, name=None):
        '''
        Stores a reference to a specified target in a message attribute.
        :param source: The object to contain the message attr.
        :param target: The object to store a reference to.
        :return: The newly created attribute.
        '''
        name = name if name else target.nodeName()
        new_name = ''.join(['_',name,'_reference'])
        attr = source.addAttr(name=new_name, at='message')
        source.attr(new_name).connect(target)
        return attr

    def snap(self, time=None):
        # Snaps the controls to the joints
        raise NotImplementedError

    def bind(self):
        # Attaches the controls to the joints
        raise NotImplementedError

    def bake(self, time=None, attributes=[]):
        # Sets a keyframe on each control
        time = time if time else pmc.currentTime(q=True)

        for control in self.controls:
            if len(attributes) > 0:
                pmc.setKeyframe(control, at=attributes, t=time)
            else:
                pmc.setKeyframe(control, t=time)

    def unbind(self):
        # Removes the controls safely
        raise NotImplementedError

    def add_support(self, *args):
        self.support.extend(args)

    def get_controls(self):
        controls = self.controls
        for component in self.components:
            controls.extend(component.controls)
        return controls

    def add_control(self, shape=None, name=None):
        control = shape.duplicate()[0] if shape else pmc.group(empty=True)
        control.rename('_'.join([name, 'CTRL']))
        self.controls.append(control)
        return control

    def add_groups(self, parent=None):
        self.master_group = pmc.group(empty=True, name='_'.join([self.name, 'COM']))
        if parent:
            pmc.parent(self.master_group, parent)
        self.control_group = self.add_group('controls')
        self.support_group = self.add_group('support')
        self.component_group = self.add_group('components')

        for control in self.controls:
            pmc.parent(control, self.control_group)
        for component in self.components:
            component.add_groups(self.component_group)
        for support in self.support:
            pmc.parent(support, self.support_group)

        pmc.hide(self.support_group)

        if len(self.component_group.getChildren()) == 0:
            pmc.delete(self.component_group)
        if len(self.support_group.getChildren()) == 0:
            pmc.delete(self.support_group)
        if len(self.control_group.getChildren()) == 0:
            pmc.delete(self.control_group)

    def add_group(self, name, parent=None):

        group = pmc.group(empty=True, name=name)
        self.groups.append(group)

        if parent:
            pmc.parent(group, parent)
        else:
            pmc.parent(group, self.master_group)

        return group

    def add_component(self, component_type, **kwargs):
        component = component_type(**kwargs)
        self.components.append(component)
        return component

class FKComponent(RigComponent):

    _name = 'FK'

    def __init__(self, joints, control, name=None):
        RigComponent.__init__(self, name)

        joints.sort(reverse=True, key=lambda j: len(j.listRelatives(ad=True)))
        self.control_joints = []
        for joint in joints:
            new_control = self.add_control(control, joint.nodeName())
            self.control_joints.append(Struct(joint=joint, control=new_control))
        pmc.delete(control)

        for i, control_joint in enumerate(self.control_joints):
            if i > 0:
                pmc.parentConstraint(self.control_joints[i-1].control, control_joint.control, mo=True)

    def snap(self, time=None):
        time = time if time else pmc.currentTime(q=True)
        for control_joint in self.control_joints:
            joint_matrix = control_joint.joint.worldMatrix.get(time=time)
            control_joint.control.setMatrix(joint_matrix, worldSpace=True)

    def bind(self):
        self.constraints = []
        for i, control_joint in enumerate(self.control_joints):
            constraint = pmc.parentConstraint(control_joint.control, control_joint.joint, mo=True)
            self.constraints.append(constraint)


class IKComponent(RigComponent):

    _name = 'IK'

    def __init__(self, joints, ik_control=None, pole_control=None, base_control=None, name=None):
        RigComponent.__init__(self, name)

        self.joints = joints
        self.joints.sort(reverse=True, key=lambda j: len(j.listRelatives(ad=True)))
        self.start_joint = self.joints[0]
        self.pole_joint = self.joints[1]
        self.end_joint = self.joints[-1]
        self.ik_control = self.add_control(ik_control, name='IK_CTRL')
        self.pole_control = self.add_control(pole_control, name='POLE_CTRL')
        self.base_control = self.add_control(base_control, name='BASE_CTRL')

    def snap(self, time=None):
        time = time if time else pmc.currentTime(q=True)

        start_matrix = self.start_joint.worldMatrix.get(time=time)
        start_point = start_matrix.translate
        end_matrix = self.end_joint.worldMatrix.get(time=time)
        end_point = end_matrix.translate
        knee_point = self.pole_joint.worldMatrix.get(time=time).translate

        self.ik_control.setMatrix(end_matrix, worldSpace=True)
        self.base_control.setMatrix(start_matrix, worldSpace=True)

        ik_vector = end_point - start_point
        mid_point = (ik_vector / 2) + start_point
        pole_vector = (knee_point - mid_point).normal()
        pole_point = mid_point + (pole_vector * 50)
        self.pole_control.setTranslation(pole_point, space='world')

    def bind(self):

        self.handle = pmc.ikHandle(sj=self.start_joint, ee=self.end_joint)[0]
        self.handle.hide()
        pmc.parent(self.handle, self.ik_control)
        pmc.poleVectorConstraint(self.pole_control, self.handle)
        pmc.parentConstraint(self.base_control, self.start_joint, mo=True)
        pmc.orientConstraint(self.ik_control, self.end_joint, mo=True)


class FKIKBlendComponent(RigComponent):

    _name = 'FKIKBlend'

    def __init__(self, joints, fk_control=None, ik_control=None, pole_control=None, master_control=None, name=None):
        RigComponent.__init__(self, name)

        self.master_control = self.add_control(master_control, self.name)
        self.master_control.addAttr('FkIkBlend', at='float', k=True, min=0.0, max=1.0)

        self.joints = joints
        self.joints.sort(reverse=True, key=lambda j: len(j.listRelatives(ad=True)))
        self.fk_chain = self._create_chain(self.joints, 'FK')
        self.ik_chain = self._create_chain(self.joints, 'IK')
        self.result_chain = self._create_chain(self.joints, '_Result')

        self.fk_component = self.add_component(FKComponent, joints=self.fk_chain, control=fk_control, name='FK')
        self.ik_component = self.add_component(IKComponent, joints=self.ik_chain, ik_control=ik_control,
                                   pole_control=pole_control, name='IK')

        pmc.parentConstraint(self.master_control, self.fk_component.control_joints[0].control, mo=True)
        pmc.parentConstraint(self.master_control, self.ik_component.base_control, mo=True)

        for control_joint in self.fk_component.control_joints[1:]:
            self.master_control.FkIkBlend.connect(control_joint.control.visibility)

        ik_reverse = pmc.createNode('reverse')
        self.master_control.FkIkBlend.connect(ik_reverse.inputX)
        ik_reverse.outputX.connect(self.ik_component.ik_control.visibility)
        pole_reverse = pmc.createNode('reverse')
        self.master_control.FkIkBlend.connect(pole_reverse.inputX)
        pole_reverse.outputX.connect(self.ik_component.pole_control.visibility)

        pmc.hide(self.fk_component.control_joints[0].control)

        for i, joint in enumerate(self.fk_chain):
            for attr in ['rotate', 'translate']:
                blend_node = pmc.createNode('blendColors')
                self.master_control.FkIkBlend.connect(blend_node.blender)

                joint.attr(attr).connect(blend_node.color1)
                self.ik_chain[i].attr(attr).connect(blend_node.color2)
                blend_node.output.connect(self.result_chain[i].attr(attr))

    def snap(self, time=None):
        time = time if time else pmc.currentTime(q=True)
        for i in range(len(self.joints)):
            matrix = self.joints[i].worldMatrix.get(time=time)
            self.fk_chain[i].setMatrix(matrix, worldSpace=True)
            self.ik_chain[i].setMatrix(matrix, worldSpace=True)
            pmc.setKeyframe(self.ik_chain[i], time=time)
            pmc.setKeyframe(self.fk_chain[i], time=time)

        master_matrix = self.joints[0].worldMatrix.get(time=time)
        self.master_control.setMatrix(master_matrix, worldSpace=True)

        self.fk_component.snap(time=time)
        self.ik_component.snap(time=time)

    def bake(self, time=None, attributes=[]):
        self.fk_component.bake(time, attributes)
        self.ik_component.bake(time, attributes)
        RigComponent.bake(self, time, attributes)

    def bind(self):

        self.fk_component.bind()
        self.ik_component.bind()
        for i in range(len(self.result_chain)):
            pmc.parentConstraint(self.result_chain[i], self.joints[i])

    def _create_chain(self, joints, suffix):
        new_chain = pmc.duplicate(joints)
        pmc.parent(new_chain[0], world=True)
        self.add_support(new_chain[0])
        for joint in new_chain:
            joint.rename('_'.join([joint.name(), suffix]))
        return new_chain

class FkIkBlendControl():
    _name = 'Fk/Ik Blend Control'

