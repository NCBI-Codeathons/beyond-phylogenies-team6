import treeswift
import types


def enhance_swift_tree(tree):
    tree.label_to_node = types.MethodType(label_to_node_opt, tree)
    tree.node_lookup = tree.label_to_node("all")
    tree.mrca_hierarchical = types.MethodType(mrca_hierarchical, tree)
    tree.cladeness = types.MethodType(cladeness, tree)
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


def mrca_hierarchical(self, labels):
        '''Return the MRCAs of all subsets of nodes labeled by a label in ``labels``,
        along with the number of nodes in ``labels`` below the respective MRCA.
        Assumes unique labels: If multiple nodes are labeled by a given label,
        only the last (preorder traversal) will be obtained

        Args:
            ``labels`` (``set``): Set of leaf labels

        Returns:
            ``Dict``: A dict with the labels of the MRCAs as keys and
            the share of nodes in ``labels`` below them as values.
        '''
        if not isinstance(labels,set):
            try:
                labels = set(labels)
            except:
                raise TypeError("labels must be iterable")
        l2n = self.label_to_node(labels)
        count = dict()
        sub_mrcas = set()
        for node in l2n.values():
            merged = False
            for a in node.traverse_ancestors():
                if a not in count:
                    count[a] = 0
                if count[a] > 0 and not merged:
                    sub_mrcas.add(a)
                    merged = True
                count[a] += 1
                if count[a] == len(l2n):
                    return({i.label:count[i] for i in sub_mrcas})
        raise RuntimeError("There somehow does not exist an MRCA for the given labels")


def cladeness(self, labels):
        '''Return the MRCAs of all subsets of nodes labeled by a label in ``labels``,
        along with the number of nodes in ``labels`` below the respective MRCA.
        Assumes unique labels: If multiple nodes are labeled by a given label,
        only the last (preorder traversal) will be obtained

        Args:
            ``labels`` (``set``): Set of leaf labels

        Returns:
            ``Dict``: A dict with the labels of the MRCAs as keys and
            the share of nodes in ``labels`` below them as values.
        '''
        if not isinstance(labels,set):
            try:
                labels = set(labels)
            except:
                raise TypeError("labels must be iterable")
        l2n = self.label_to_node(labels)
        
        # count mrcas
        mrca_count = dict()
        sub_mrcas = set()
        total_mrca = None
        for node in l2n.values():
            merged = False
            for a in node.traverse_ancestors():
                if a not in mrca_count:
                    mrca_count[a] = 0
                if mrca_count[a] > 0 and not merged:
                    sub_mrcas.add(a)
                    merged = True
                mrca_count[a] += 1
                if mrca_count[a] == len(l2n):
                    total_mrca = a
                    break
            if total_mrca is not None:
                break
        if total_mrca is None: raise RuntimeError("There somehow does not exist an MRCA for the given labels")
        
        # count leaves below mrcas
        num_valid_leaves = dict()
        for node in total_mrca.traverse_postorder():
                if node.is_leaf():
                    num_valid_leaves[node] = 1 # Filtering criteria to be applied here
                else:
                    num_valid_leaves[node] = sum(num_valid_leaves[c] for c in node.children)
        
        # compute cladeness scores
        cladeness = {i.label:mrca_count[i]/num_valid_leaves[i] for i in sub_mrcas}
        
        return cladeness
