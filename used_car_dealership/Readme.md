## About
This project is about analysis of Used Cars for a dealership in US. The business need is to understand what factors make a car more or less expensive, and thereby price the car appropriately to achieve better bottomline.
We assume the dealership addresses the needs of common man primarily i.e standard set of make-model cars. Vintage or high end cars will be valued on an individual basis and not through this model.
To analyze, we use historical data composing different choices available for customers (indpendent variables) and their prices (dependent variable), received from the sales office.


## Findings :
The data provided has a lot of bad data such as price of a used car priced in billions, while the max sale price of any car was 142M. Other issues include Prices are 0 for some of the cars; lot of features do not have data. Based on our current analysis, we are unable to define a model that can help predict a car price better. Hence we request more time to try other ways to clean up the data, fill in missing values with right values and eventually get to a right model.

Based on the above data analysis, given the RMSE (and MSE) is more than 6K from couple of models, which in my opinion is still a high number with opportunity to further reduce by optimizing the data and hence the model. Couple of things to explore to continue to find the right model :
- Identify the right set of records, may be a quartile band, which may in turn help define a model for that set range of cars.
- Re-do the data preparation by using different encoders / imputers.


## Summary of Analysis :
1. Total # of records provided on file 426880
2. Columns `id` and `VIN` do not add value when purchasing a car. Hence these columns are dropped.
3. Column `size` has 306361 NaNs, which is more than 50% of the data. Hence we drop this column
4. Given the columns `state` and `region` capture geographic location, we use the more coarse level `state` column. The `region` column is dropped.
5. Based on the biz requirement above, we drop all the cars which are older than 1970. # of records dropped are 6487.
6. Also dropped are cars priced below $2000 or above 200K. The below 2K car prices, we believe is not worth a sales person time and space in the lot. The 200K cars are considered vintage and priced differently. Total # of records dropped are 53101
7. Odometer : Data has cars with year 2020 but more than 1M miles. Per G search (https://www.google.com/search?client=firefox-b-1-d&q=any+car+driven+million+mile), the most recent built car that crossed more than 1M miles is a 2013 car. Hence we drop all cars with odometer reading greater than 1M and year greater than 2013. # of records dropped are 91.
8. Drop rows that do not have a Year. # of records dropped are 1205

### Data Prep :
Now that we have largely dropped columns and rows that do not add value to our analysis, we prep the existing data as below :
1. Manufacturer: Empty values are filled with `unknown`
2. Model : Empty values are filled with `unknown` value.
3. Manufacturer and Model : Given the combination of the two is what provides a common data point for customer. For eg: We have Model 1500 from multiple manufacturers - Silverado, as well as a RAM, GMC. We use `---` as a separator between the 2 values.
4. Fuel : We fix some of the bad data by checking against Manufacturer-Model field. If Manufacturer-Model has `prius` or `hybrid` in it we update Fuel to be `hybrid`. We fill empty cells with `unknown`.
5. Paint Color : Empty cells are filled with `unknown` value. We then use Label Encoder to convert the values to numeric data.
6. Cylinders : After fixing some of the missing values, by leveraging Manufacturer-Model value, we still had 149893 records with empty values. Hence we dropped Cylinders column.
7. Title Status : Missing values are replaced with `unknown`. We use Ordinal Encoding to convert the values to numeric.
8. Condition : We normalize empty values based on title status using a map. We check the prices of cars without values and on looking at the stats (25 to 75 percentile; Min, Max and Mean), we believe on an average most of these cars are in atleast a `good` condition, which is about 1934 records.
9. Transmission : We have about 1734 NaNs. On comparing the stats against the other transmission types, the stats were closer to `automatic` type. Hence all NaNs were updated with `automatic`.
10. State : We use Target Encoder to convert this column to Numeric value.
11. We split the data into `train` and `test` with a ration of 75:25. We run James-Stein Encoder to convert the columns `Manuf-Model`, `type`, `fuel`, `drive` to numeric data type.
12. StandarScaler is used to normalize the data. PCA is run against this to reduce dimensionality and K-Means to cluster rows.