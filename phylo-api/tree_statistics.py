import treeswift
import types


def enhance_swift_tree(tree):
    tree.label_to_node = types.MethodType(label_to_node_opt, tree)
    tree.node_lookup = tree.label_to_node("all")
    tree.mrca_hierarchical = types.MethodType(mrca_hierarchical, tree)
    tree.cladeness = types.MethodType(cladeness, tree)
    tree.cladeness_clusters = types.MethodType(cladeness_clusters, tree)
    tree.clusters = types.MethodType(clusters, tree)
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


def mrca_hierarchical(labels, parents):
        '''Return the MRCAs of all subsets of nodes labeled by a label in ``labels``,
        along with the number of nodes in ``labels`` below the respective MRCA.
        Assumes unique labels: If multiple nodes are labeled by a given label,
        only the last (preorder traversal) will be obtained

        Args:
            ``labels`` (``set``): Set of leaf labels
            ``parents`` (``dict``): Dictionary of the parents of the leaves

        Returns:
            ``Dict``: A dict with the labels of the MRCAs as keys and
            the share of nodes in ``labels`` below them as values.
        '''
        if not isinstance(labels,set):
            try:
                labels = set(labels)
            except:
                raise TypeError("labels must be iterable")
        count = dict()
        sub_mrcas = set()
        for node in labels:
            merged = False
            for a in parents[node]:
                if a not in count:
                    count[a] = 0
                if count[a] > 0 and not merged:
                    sub_mrcas.add(a)
                    merged = True
                count[a] += 1
                if count[a] == len(labels):
                    return({i for i in sub_mrcas})
        raise RuntimeError("There somehow does not exist an MRCA for the given labels")


def cladeness(self, labels, metadata = None, filter_criteria = None):
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
        if metadata is None and filter_criteria is not None:
            raise ValueError("Filter criteria supplied but no metadata available.")
        
        # find mrca
        mrca = self.mrca(labels)
        
        # count leaves below mrca
        num_valid_leaves = 0
        for node in mrca.traverse_postorder():
                if node.is_leaf():
                    # apply filter criteria
                    if filter_criteria is None or node_meets_criteria(node, metadata, filter_criteria):
                        num_valid_leaves += 1
        
        # compute cladeness scores
        cladeness = {mrca.label:{"size":len(labels),"cladeness":len(labels)/num_valid_leaves}}
        
        return mrca.label, cladeness


def cladeness_clusters(self, labels, metadata = None, filter_criteria = None):
        '''Return the MRCAs of all subsets of nodes labeled by a label in ``labels``,
        along with the number of nodes in ``labels`` below the respective MRCA.
        Assumes unique labels: If multiple nodes are labeled by a given label,
        only the last (preorder traversal) will be obtained

        Args:
            ``labels`` (``set``): Set of leaf labels
            ``metadata`` (``dict``): Dictionary with leaf labels as keys and node metadata as values
            ``filter_criteria`` (``dict``): Dictionary with filter criteria

        Returns:
            ``Dict``: A dict with the labels of the MRCAs as keys and
            the share of nodes in ``labels`` below them as values.
        '''
        if not isinstance(labels,set):
            try:
                labels = set(labels)
            except:
                raise TypeError("Labels must be iterable.")
        if metadata is None and filter_criteria is not None:
            raise ValueError("Filter criteria supplied but no metadata available.")
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
                    num_valid_leaves[node] = 0
                    # apply filter criteria
                    if filter_criteria is None or node_meets_criteria(node, metadata, filter_criteria):
                        num_valid_leaves[node] = 1
                else:
                    num_valid_leaves[node] = sum(num_valid_leaves[c] for c in node.children)
        
        # compute cladeness scores
        cladeness = {i.label:{"size":mrca_count[i],"cladeness":mrca_count[i]/num_valid_leaves[i]} for i in sub_mrcas}
        
        return total_mrca.label, cladeness


def node_meets_criteria(node, metadata, filter_criteria):
    if node.label not in metadata: return False
    if "date_from" in filter_criteria:
        if (
            "date" not in metadata[node.label] or
            metadata[node.label]["date"] is None or
            filter_criteria["date_from"] > metadata[node.label]["date"]
        ): return False
    if "date_to" in filter_criteria:
        if (
            "date" not in metadata[node.label] or
            metadata[node.label]["date"] is None or
            filter_criteria["date_to"] < metadata[node.label]["date"]
        ): return False
    if "country" in filter_criteria:
        if (
            "country" not in metadata[node.label] or
            metadata[node.label]["country"] is None or
            filter_criteria["country"] != metadata[node.label]["country"]
        ): return False
    if "region" in filter_criteria:
        if (
            "region" not in metadata[node.label] or
            metadata[node.label]["region"] is None or
            filter_criteria["region"] != metadata[node.label]["region"]
        ): return False
    # only if all criteria passed
    return True


def get_non_overlapping(sorted_mrcas, parents, n):
    # select mrcas
    selected_mrcas = set()
    mrcas_exlcuded = set()
    descendants_excluded = set()

    for m in sorted_mrcas:
        if m not in mrcas_exlcuded and not any([p in descendants_excluded for p in parents[m]]):
            selected_mrcas.add(m)
            for p in parents[m]:
                mrcas_exlcuded.add(p)
            descendants_excluded.add(m)
            if len(selected_mrcas) == n: break
                
    return selected_mrcas


def mrca_root_children(tree, mrca_labels):
    mrca_children = {k:set() for k in mrca_labels}
    root_node = None
    for n in mrca_labels:
        has_parent = False
        for p in tree.node_lookup[n].traverse_ancestors(include_self=False):
            if p.label in mrca_labels:
                mrca_children[p.label].add(n)
                has_parent = True
                break
        if not has_parent: root_node = n
    return root_node, mrca_children


def select_clusters(tree, mrcas, n_sequences, n_clusters = 12, min_rel_size = 0.05):
    # filter for sufficient size
    filtered_mrcas = {k:m for k, m in mrcas.items() if m["size"]>=n_sequences*min_rel_size}

    mrca_labels = filtered_mrcas.keys()
    sorted_mrcas = [k for k,m in sorted(filtered_mrcas.items(), key=lambda item: (item[1]["cladeness"],item[1]["size"]), reverse=True)]
    parents = {m:[p.label for p in tree.node_lookup[m].traverse_ancestors(include_self=False) if p.label in mrca_labels] for m in mrca_labels}
    
    # select non-overlapping mrcas with high cladeness
    selected_mrcas = get_non_overlapping(sorted_mrcas, parents, n_clusters)

    # add the mrcas of the selected mrcas
    additional_mrcas = mrca_hierarchical(selected_mrcas, parents)

    return selected_mrcas.union(additional_mrcas)


def build_tree(i, mrcas, children):
    if len(children[i])==0:
        return {"node":i, "statistics":mrcas[i], "children":None}
    else:
        subt = list()
        for c in children[i]:
            subt_new = build_tree(c, mrcas, children)
            subt.append(subt_new)
        subt = {"node":i, "statistics":mrcas[i], "children":subt}
    return subt


def clusters(self, labels, n_clusters = 12, min_rel_size = 0.05, metadata = None, filter_criteria = None):
    total_mrca, mrcas = self.cladeness_clusters(labels, metadata, filter_criteria)
    selected_c = select_clusters(self, mrcas, n_sequences = len(labels), n_clusters = n_clusters, min_rel_size = min_rel_size)
    selected_c.add(total_mrca)
    root, children = mrca_root_children(self, selected_c)
    return build_tree(root, mrcas, children)
