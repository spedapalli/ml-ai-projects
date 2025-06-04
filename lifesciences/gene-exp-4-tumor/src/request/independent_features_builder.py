from pydantic import ConfigDict, Field
# from pydantic.dataclasses import dataclass
import random
import pandas as pd
from pandas import DataFrame


class IndependentFeaturesBuilder :
    model_config = ConfigDict(arbitrary_types_allowed=True)
    vars_stat_desc_df:DataFrame = None
    # vars_stat_desc_df:DataFrame = Field(
    #     default_factory = lambda:pd.read_csv('./data/xgb_test_X_describe.csv', index_col=0)
    # )


    # Pydantic v2 recommendation to override this fn for post init setup
    def __init__(self, vars_stat_desc_df:DataFrame=None):
        if self.vars_stat_desc_df is None:
            self.vars_stat_desc_df = pd.read_csv('./data/xgb_test_X_describe.csv')
        else:
            self.vars_stat_desc_df = vars_stat_desc_df


    def get_all_independent_vars(self, input_vars :dict):
        all_input_vars_dict:dict = {}
        for index, row in self.vars_stat_desc_df.iterrows():
            gene_id = row['Unnamed: 0'] #TODO : Fix this column name
            if (gene_id in input_vars and input_vars[gene_id] != 0) :
                all_input_vars_dict[gene_id] = input_vars[gene_id]
            else :
                min = row['min']
                max = row['max']
                value = random.uniform(min, max)
                all_input_vars_dict[gene_id] = value

        return all_input_vars_dict

