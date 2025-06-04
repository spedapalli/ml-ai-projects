from unittest import TestCase
from request.independent_features_builder import IndependentFeaturesBuilder

class Test_IndependentFeatures (TestCase):

    def test_get_all_independent_vars(self):
        input_vars: dict = {}
        ind = IndependentFeaturesBuilder()
        consolidated_values = ind.get_all_independent_vars(input_vars)
        assert (consolidated_values != None)
        assert (len(consolidated_values) == 18604)

