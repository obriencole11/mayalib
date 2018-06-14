import pymel.core as pmc

class Component(object):

    def __init__(self, node=None, name=None):
        name = name if name else 'Untitled'
        self.component_group = node if node else pmc.group(empty=True, name=name+'_COM')

    def addInput(self, node, name=None):
        name = name or node.name()
        input_grp = pmc.group(empty=True, name=name + '_IN')
        pmc.matchTransform(input_grp, node)
        pmc.parent(input_grp, self.input_group)
        pmc.parentConstraint(node, input_grp, mo=True)
        self.__dict__[name] = input_grp

    def getInput(self, keyword):
        for input in self.inputs:
            if keyword in input:
                return self.inputs[input]
        return None

    def getOutput(self, keyword):
        for output in self.outputs:
            if keyword in output:
                return self.outputs[output]
        return None

    def getContent(self, keyword):
        for content in self.contents:
            if keyword in content:
                return self.contents[content]
        return None

    def addContents(self, nodes):
        pmc.parent(nodes, self.content_group)

    def addOutput(self, node, name=None):
        name = name or node.name()
        output_grp = pmc.group(empty=True, name=name + '_OUT')
        pmc.matchTransform(output_grp, node)
        pmc.parent(output_grp, self.output_group)
        pmc.parentConstraint(node, output_grp, mo=True)
        self.__dict__[name] = output_grp

    @property
    def contents(self):
        return {node.name(): node for node in self.content_group.getChildren()}

    @property
    def outputs(self):
        return {group.name(): group for group in self.output_group.getChildren()}

    @property
    def inputs(self):
        return {group.name(): group for group in self.input_group.getChildren()}

    @property
    def output_group(self):
        return self._getGroup('outputs')

    @property
    def input_group(self):
        return self._getGroup('inputs')

    @property
    def content_group(self):
        return self._getGroup('contents')

    def _getGroup(self, group_name):
        if group_name in self.children:
            return self.children[group_name]
        else:
            group = pmc.group(empty=True, name=group_name)
            pmc.parent(group, self.component_group)
            return group

    @property
    def children(self):
        return {group.name(): group for group in self.component_group.getChildren()}