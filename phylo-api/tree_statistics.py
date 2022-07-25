import treeswift
import types


def optimize_tree(tree):
    tree.label_to_node = types.MethodType(label_to_node_opt, tree)
    tree.node_lookup = tree.label_to_node("all")
    return tree


def label_to_node_opt(self, selection='leaves'):
        '''Return a dictionary mapping labels (strings) to ``Node`` objects.
        
        This is an altered version of the treeswift function, optimized for unique node labels

        * If ``selection`` is ``"all"``, the dictionary will contain all nodes
        * If ``selection`` is ``"leaves"``, the dictionary will only contain leaves
        * If ``selection`` is ``"internal"``, the dictionary will only contain internal nodes
        * If ``selection`` is a ``set``, the dictionary will contain all nodes labeled by a label in ``selection``
        * If multiple nodes are labeled by a given label, only the last (preorder traversal) will be obtained

        Args:
            ``selection`` (``str`` or ``set``): The selection of nodes to get
            * ``"all"`` to select all nodes
            * ``"leaves"`` to select leaves
            * ``"internal"`` to select internal nodes
            * A ``set`` of labels to specify nodes to select

        Returns:
            ``dict``: Dictionary mapping labels to the corresponding nodes
        '''
        if not isinstance(selection,set) and not isinstance(selection,list) and (not isinstance(selection,str) or not (selection != 'all' or selection != 'leaves' or selection != 'internal')):
            raise RuntimeError('"selection" must be one of the strings "all", "leaves", or "internal", or it must be a set containing Node labels')
        if isinstance(selection, str):
            selection = selection[0]
        elif isinstance(selection,list):
            selection = set(selection)
        if selection == 'a' and hasattr(self, "node_lookup"):
            return self.node_lookup
        if isinstance(selection, set):
            if not hasattr(self, "node_lookup"): self.node_lookup = self.label_to_node("all")
            return {l: self.node_lookup.get(l) for l in selection}
        label_to_node = dict()
        for node in self.traverse_preorder():
            if selection == 'a' or (selection == 'i' and not node.is_leaf()) or (selection == 'l' and node.is_leaf()) or str(node) in selection:
                label_to_node[str(node)] = node
        if not isinstance(selection,str) and len(label_to_node) != len(selection):
            warn("Not all given labels exist in the tree")
        return label_to_node


