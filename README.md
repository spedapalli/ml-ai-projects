# ml-ai
Code associated to some of the ML / AI Projects I work on during my spare time. Each folder is a ML or an AI project of its own. Below is a brief outline of each project.

### lifesciences/mental-health-counseling
The model, a pre-trained one, classifies Patient's current feelings based on their input.

Key highlights : 
- UI and backend. Initial exploration and testing of the model was done in Jupyter notebook. Later on transitioned to building backend application.
- Uses a pre-trained model
- Ops : Supports docker builds and deploy to AWS, all scripted out.

![lifesciences/mental-health-counseling](lifesciences/mental-health-counseling/)

### lifesciences/gene-exp-4-tumor : 
A Classification problem that studies 5 types of cancers and their underlying gene expressions.

Key Highlights : 
- UI and backend
- A number of models are trained to identify best performing model, which is stored as a .pkl file in AWS S3.
- Above .pkl file is used on backed to classify / predict tumor given gene expressions as input
- Ops : Can be run independentally or using Docker container


![lifesciences/gene-exp-4-tumor](lifesciences/gene-exp-4-tumor/)

### RAG : 
RAG Applications.

![PdfIngester](RAG/PdfIngester/)


### bank-direct-marketing : 
A Classification problem in identifying which customers are more likely to purchase which product(s).

Analysis is done in Jupyter notebook.

![bank-direct-marketing](./bank-direct-marketing/)

### used-car-dealership : 
A regression problem used to determin the price of an used car. The challenge part of this application is the data, which is not only incomplete but also bad at many places.

![used-car-dealership](./used-car-dealership/)

### amazon-coupons : 
An early-on project in process of learning ML / AI models. Goal is to identify what type of coupons to customers have most value. 

Analysis is done in a Jupyter notebook.

![amazon-coupons](./amazon-coupons/)


