

def get_list_of_items_in_both_lists(src_list: list, lookup_list: list):
    """
    For every item in the param `src_list`, the function looks up param `lookup_list` and if it exists is
    included in the list returned by the function.
    @return list
    """
    features_with_nan_in_pca = []
    for feature in src_list:
        if (feature in lookup_list) :
            features_with_nan_in_pca.append(feature)
            # print(f"{feature} with NaN values is included in PCA shortlisted features")

    return features_with_nan_in_pca
