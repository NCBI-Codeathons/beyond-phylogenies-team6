def split_in_found_and_not_found(tree_label_set, labels):
    found = []
    not_found = []
    for label in labels:
        if label in tree_label_set:
            found.append(label)
        else:
            not_found.append(label)
    return found, not_found
