# REF: https://applyingml.com/resources/patterns/

# Using Decorator pattern to generate test data
# #TODO : Copy pasted code from above, Revisit and cleanup


import pytest
import numpy as np

from src.data_prep.prep_titanic import load_df, prep_df, split_df, get_feats_and_labels
from src.tree.decision_tree import DecisionTree
from src.tree.random_forest import RandomForest

# Returns data for training and evaluating our models
@pytest.fixture
def dummy_dataset():
    df = load_df()
    df = prep_df(df)

    train, test = split_df(df)
    X_train, y_train = get_feats_and_labels(train)
    X_test, y_test = get_feats_and_labels(test)
    return X_train, y_train, X_test, y_test

# Returns a trained DecisionTree that is evaluated on implementation and behavior
@pytest.fixture
def dummy_decision_tree(dummy_dataset):
    X_train, y_train, _, _ = dummy_dataset
    dt = DecisionTree(depth_limit=5)
    dt.fit(X_train, y_train)
    return dt

# Returns a trained RandomForest that is evaluated on implementation and behavior
@pytest.fixture
def dummy_random_forest(dummy_dataset):
    X_train, y_train, _, _ = dummy_dataset
    rf = RandomForest(num_trees=8, depth_limit=5, col_subsampling=0.8, row_subsampling=0.8)
    rf.fit(X_train, y_train)
    return rf