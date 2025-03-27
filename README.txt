Milestone 2:

Ciaran: Users Guru: responsible for Account / Purchases
Eddie: Products Guru: responsible for Products
Dylan: Carts Guru: responsible for Cart / Order
Kethan: Sellers Guru: responsible for Inventory / Order Fulfillment
Aaron: Social Guru: responsible for Feedback / Messaging

Ciaran
1. Created Figma mockup for our website
2. Articulated Users, Carts, and Social page designs

Dylan: 
1. created ERD diagram to visually show database schema
2. Wrote code for create.sql and load.sql based on our collectively agreed upon schema
3. Created .csv files for each table in our schema

Kethan:
1. Designed outline for the Sellers pages
2. Looked over the Figma mockup and advocated for changes in the UX of sellers

Eddie
1. page design flow for products 

Aaron:
1. synthesized all the information from the database and page design into a cohesive report

Milestone 3: 

Sellers Guru:
  app/models/user.py - the query to get the information for the sellers’ products
  
  app/templates/base.html + app/templates/sales.html - addition to navbars with sales included
  
  app/templates/seller_products.html - using the template table put in all our information regarding products for sale
  
  app/users.py - routing for the sales tab; only available when both logged in and a seller
