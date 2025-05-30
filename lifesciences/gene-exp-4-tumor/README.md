### Analysis of Gene Expressions for 5 types of Tumors

**Author**
Samba Pedapalli

#### Executive summary
Pan-Cancer analysis is a study of different types of cancer to understand the underlying mechanisms of Cancer, and thereby develop effective treatments.

The intent of this project is to analyse gene expressions for below 5 types of tumors. In identifying these expressions, we may be able to diagnose a patient early and potentially recommend for further tests / validation.
- BRCA (Breast Cancer): Family of Genes (BRCA1 and BRCA2) are known as tumor suppresors. But mutation in these genes cause cancer.
- KIRC (Kidney Renal Clear Cell Carcinoma):
- COAD (Colon Adenocarcinoma)
- LUAD (Lung Adenocarcinoma)
- PRAD (Prostate Adenocarcinoma)


#### Rationale
Why should anyone care about this question?
Between 2000 and 2021, US cancer rates increased by 36.3%, per [USAFacts](https://usafacts.org/articles/how-have-cancer-rates-changed-over-time/) and this seems to be trend globally too. The economic burden is estimated to reach $25.2 trillion between 2020 and 2050, globally.
Cancer comes in different forms and at different parts of the body. A key fundamental unit of living body is Gene. Studying Gene's expressions for different types of cancers can help us diagnose different types of cancers, its progression and predict outcomes early as well as guide on the choice of therapies to use (chemo, drugs). Thus, giving the patient a higher chance of survival and reducing the overall its economic impact.

From a ML / AI perspective, this dataset has close to 20531 columns, with only 801 instances (samples). In other words, the dataset features are much larger than the number of rows and hence dataset and the the training of models need to be handled differently.


#### Research Question
The relation between tumors and Gene expressions to 5 types of cancers.

#### Data Sources
The dataset used here is from https://archive.ics.uci.edu/dataset/401/gene+expression+cancer+rna+seq, which in turn points to the original source of the dataset at https://www.synapse.org/#!Synapse:syn4301332. The gene names are dummified here, while the original names could be obtained from https://www.ncbi.nlm.nih.gov/gene, per this discussion thread https://www.synapse.org/Synapse:syn300013/discussion/threadId=5455&replyId=29619.

In the dataset used for this project, we have two files :
data.csv : A collection of 801 samples (rows), with 20531 gene expressions (columns).
labels.csv : A mapping of each record/sample to the tumor type.

#### Methodology
What methods are you using to answer the question?
We follow the standard CRISP-DM (CRoss Industry Standard Process for Data Mining) methodology :
- Understand the Business Requirement : As stated in above sections
- Understanding the data :
    - Below is the distribution of
    - Data does not have any NaNs and all the values are numerical.
    - We do have 267 features with 0 values.
    - We also realize 1660 features' have data that only falls in the 4th quartile, aka outliers.
    - Given the large number of dimensions, understanding the correlation between these features is challenging. We rely on PCA process, as noted in next step.
    - Below is the distribution of target class / labels, across the 801 records :

        | Class | Count |
        | ----- | ----- |
        | BRCA | 300 |
        | KIRC | 146 |
        | LUAD | 141 |
        | PRAD | 136 |
        | COAD | 78 |

- Prepping the data :
    - We split the data into 2 datasets - `training` and `test`. When doing so, we use the Stratify strategy, given the uneven distribution of Classes across records, as shown in above table. This helps us ensure a balanced distribution of each Class of records, across the 2 datasets.
    - We drop the features with all 0 values.
    - We also drop the features with values in 4th quartile i.e outliers that do not seem to provide much significance to the analysis, to ensure data is ready to be ingested by the PCA model. We are left with 18604 features / columns / dimensions.
    - We then reduce the number of dimensions / features to 640, using PCA.

- Evaluation : We evaluate the above models using various methods - accuracy score, F1 score and plot a Confusion Matrix heat map.
- Modeling : Given, we are trying to identify the relationship of Gene expressions to 5 different types of tumors, we consider this to be a classification problem. We evaluate 2 Ensemble classifier models - *RandomForest* and *XGBoost*.
- Model is persisted for future usage, using [joblib](https://joblib.readthedocs.io/en/stable/) toolset

#### Results

Based on the below accuracy score, although the 'RandomForest without PCA' model provides the best accuracy, we think there may be overfitting here given the model mis-classified only 1 record. As our goal here is to provide initial diagnosis to help guide the patient to recommend for further testing, we will be conservative over being too optimistic. Hence, we recommend the **XGBoost with PCA** model, which is the next most accurate model.

| Model / Metrics | Accuracy Score |
| --------------- | -------------- |
| Random Forest without PCA | 99.378881% |
| Random Forest with PCA | 88.1987577% |
| XGBoost with PCA | 90.6832298 |

NOTE: All the scores are results obtained on `test` data, after the model was trained on `train` dataset.

##### Classification Report :
| Model / Metrics | class | precision | recall | f1-score |
| --------------- | ----- | --------- | ------ | -------- |
| Random Forest without PCA | BRCA | 0.98 | 1.00 | 0.99 |
| Random Forest without PCA | COAD | 1.00 | 1.00 | 1.00 |
| Random Forest without PCA | KIRC | 1.00 | 1.00 | 1.00 |
| Random Forest without PCA | LUAD | 1.00 | 0.96 | 0.98 |
| Random Forest without PCA | PRAD | 1.00 | 1.00 | 1.00 |
|  |
| Random Forest with PCA | BRCA | 0.77 | 1.00 | 0.87 |
| Random Forest with PCA | COAD | 1.00 | 0.69 | 0.81 |
| Random Forest with PCA | KIRC | 1.00 | 0.93 | 0.97 |
| Random Forest with PCA | LUAD | 1.00 | 0.64 | 0.78 |
| Random Forest with PCA | PRAD | 0.96 | 0.93 | 0.94 |
| |
| XGBoost with PCA       | BRCA | 0.98 | 1.00 | 0.99 |
| XGBoost with PCA       | COAD | 0.93 | 0.88 | 0.90 |
| XGBoost with PCA       | KIRC | 1.00 | 0.97 | 0.98 |
| XGBoost with PCA       | LUAD | 1.00 | 0.68 | 0.81 |
| XGBoost with PCA       | PRAD | 1.00 | 0.96 | 0.98 |

##### Confusion Matrix Heatmap :
![Random Forest without PCA](./images/RForestWithoutPCA_ConfMatrix.png)

![Random Forest with PCA](./images/RFWithPCA_ConfMatrix.png)

![XGBoost with PCA](./images/XGBoostWithPCA_ConfMatrix.png)

##### Gene expressions contribution to the model :
![Random Forest with PCA](./images/RF_Gene_Contribs_2Model.png)

![XGBoost with PCA](./images/XGB_Gene_Contribs_2Model.png)

##### Individual Gene Contributions for each Class / Tumor :
Random Forest with PCA : Given the file is large, request to run the model to see this output. Output is written to file ./data-analysis/RForest_Gene_exp_contrib_2each_Tumor.csv.

#### Next steps
- Modeling & Evaluation :
    -- Evaluate XGBoost without PCA and how it performs on the complete set of dimensions
    -- Use dimension reduction techniques that preserve interpretability, such as factor analysis
    -- Use other feature selection methods (RFE, SelectKBest) instead of PCA and run the models again.
    -- Use Neural models to evaluate how they perform against the above
- Tech Debt / Refactoring :
    - Use Value Object design pattern to return values from functions, for reuse.
    - Retool functions (eg: run_pca_xxxx() ) to intake params and return values

#### Outline of project

- [Run RandomForest without PCA](./gene-exp-4-tumor-direct-rforest.ipynb)
- [Run RandomForest and XGBoost without PCA](./gene-exp-4-tumor.ipynb)
- Dataset : Is stored in the folder [TCGA-PANCAN-HiSeq-801*20531](./TCGA-PANCAN-HiSeq-801x20531/)
- [images](./images/) : Plots generated by the models are stored in this directory.
- [models](./models/) : Models used in the analysis are persisted to this directory
- This project has been created using [`uv` package tool](https://github.com/astral-sh/uv) and hence includes [requirements.txt](requirements.txt), to help setup the right env and run the file.
- data-analysis : This folder is created when the steps in the IPYNB notebooks are run. This dir is used as a place holder for analysis and hence not checked into Git.

#### Running the Application :
- To run the Jupyter notebooks please follow the standard process of opening the file and executing each step in there.
- To run the Application aka with web interface, follow below steps :
    - Open a terminal and `cd` to the directory `gene-exp-4-tumor`. Run the cmd `uvicorn --app-dir ./src main:app --reload --host 127.0.0.1 --port 8000` Note the URL and port are optional and these values shown here are default values.
    - Open browser and access the URL http://127.0.0.1:8000.


##### Contact and Further Information
Contact : samba.pedapalli@gmail.com

Pan-Cancer analysis is done by studying a large number of tumor samples to identify commonalities and differences in each cancer Genomic and Cellular alterations.

TCGA (The Cancer Genome Atlas) : An organiztion......

Gene Expression : Process by which genetic information encoded in DNA is used to create RNA molecules which in direct the production of proteins, which perform key functions within the Cell, including division, growth and other processes.
RNA-Seq : Technology that measures the expression of all genes in a sample