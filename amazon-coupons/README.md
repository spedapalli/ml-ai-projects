## Amazon Coupons :
This data comes to us from the UCI Machine Learning repository and was collected via a survey on Amazon Mechanical Turk. The survey describes different driving scenarios including the destination, current time, weather, passenger, etc., and then ask the person whether he will accept the coupon if he is the driver. Answers that the user will drive there ‘right away’ or ‘later before the coupon expires’ are labeled as ‘Y = 1’ and answers ‘no, I do not want the coupon’ are labeled as ‘Y = 0’.  There are five different types of coupons -- less expensive restaurants (under \$20), coffee houses, carry out & take away, bar, and more expensive restaurants (\$20 - $50).


#### Analysis :
The data was analyzed using different Python libraries, slicing the data using various methods including `.query`, `.loc`, `Bracket selection`, `Lambda function` and many more.

#### Code :
[Jupyter Notebook](./prompt.ipynb)

#### Summary of findings :
- Customers who go to the bars more frequently tend to redeem coupons more, especially customers who are less than 30 yrs old - ~72% more likely.
- Customers whose annual income is less than 50K, are more likely to redeem coupons at Restaurants where bill is <$20.
- The 2 types of coupons most redeemed are "Restaurants < $20" and "Carryout & Takeaway". These coupons are largely redeemed by customers in income range "12500 to 24999", "25000 - 37499".
- The most issued coupons were for Coffee Bar and incidentally their redemption was <50%.
- Weather / Temp seem to have little effect on coupon redemption. Note that the number of coupons issued on hotter (80 degrees) days are more than at other temperatures.
- Interestingly enough, Customers without children are more likely to redeem coupon than Customers with Children.

#### Next Steps :
- It would be interesting to further slice data across the 2 types of coupons to understand better the demographics of the population, very similar to how Bar coupon was analyzed.
