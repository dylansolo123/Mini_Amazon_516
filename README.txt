Milestone 2:

Kethan: Users Guru: responsible for Account / Purchases
Dylan: Products Guru: responsible for Products
Eddie: Carts Guru: responsible for Cart / Order
Ciara: Sellers Guru: responsible for Inventory / Order Fulfillment
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

Ciaran - Sellers Guru:
  app/models/user.py - the query to get the information for the sellers’ products
  
  app/templates/base.html + app/templates/sales.html - addition to navbars with sales included
  
  app/templates/seller_products.html - using the template table put in all our information regarding products for sale
  
  app/users.py - routing for the sales tab; only available when both logged in and a seller

Eddie - Carts Guru:
File	Description
app/models/cart.py - New Cart model with methods for cart item management
app/cart.py	- New Blueprint and routes for cart operations
app/init.py	- Integration of the new cart Blueprint
app/models/product.py - Updates to include seller information in product queries


Dylan - Products Guru:

app/templates/index.html - Changed Nav bar for products to point to actual products page
app/models/product.py - Created the get_top_k_expensive(k) SQL query method that joins Products with Seller_Inventory and Users tables, groups by product details, filters for products with prices and stock, orders by price in descending order, and limits the results to k products.
app/templates/products.html- Made a HTML template that accepts a number input 'k' and shows the filtered products in a table format with their IDs, names, prices, seller information, and "Add to Cart" buttons.
db/generated/gen.py - Augmented the gen.py file to create generated data for our new CSV files/data schema

Kethan - Users Guru:
Modified base.html (nav bar) to link to my orders drop down to order.html. 
Created and orders route in index.py to get all orders by a user.