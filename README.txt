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



Milestone 4:

LINK TO DEMO VIDEO: https://www.youtube.com/watch?v=M6dVreg1eeg

Eddie - Carts Guru: 
app/cart.py: Added checkout route to display cart checkout page.
app/models/cart.py: Added checkout_cart method to handle checkout logic.
app/templates/cart.html: Updated all button functionality from previous add to cart, trash, and checkout logic.
app/templates/checkout.html: New template displaying cart items and totals.

Aaron - Social Guru:
app/models/review.py: create and edit reviews, delete reviews and fetch user reviews
app/models/product.py: show reviews on product page as well as statistics on reviews
app/users.py: delete and edit a review
I made the video and report for this milestone


Dylan - Products Guru:
app/models/product.py: Enhanced product filtering with rating functionality, improved product details retrieval, fixed inventory handling.
- Added min_rating parameter to get_all method for filtering products by rating
- Fixed product details retrieval to work for both in-stock and out-of-stock products
- Improved inventory calculations and price handling
- Enhanced error handling and logging
- Standardized SQL queries with proper NULL handling
- Fixed aggregation of review statistics
- Improved seller information retrieval in product details

app/templates/product_details.html: Improved product details page layout and functionality.
- Enhanced layout and spacing for better user experience
- Added proper handling of empty states
- Improved display of product information
- Added rating display and filtering functionality
- Fixed product availability display
- Enhanced seller information presentation
- Improved review display section
- Added proper error handling for missing products

app/templates/index.html: Enhanced home page layout and functionality.
- Improved Top Deals section layout
- Fixed price calculation for original prices
- Added proper handling of decimal arithmetic
- Enhanced product card presentation
- Improved spacing and grid layout
- Added proper error handling for empty states
- Fixed product availability display
- Enhanced visual hierarchy of product information
- Added proper handling of product ratings

app/index.py: Updated product details route handling and home page functionality.
- Enhanced error handling for product not found cases
- Improved product details retrieval logic
- Added proper redirection for invalid product IDs
- Fixed route handling for both in-stock and out-of-stock products
- Fixed decimal arithmetic for price calculations
- Added proper type conversion for numeric values
- Enhanced product listing logic for Top Deals
- Improved error handling for empty product lists


Kethan - Users Guru:
modified myaccount.html to be able to update all user field, modify the current balance, and view past orders. I added order_details.html to display the specifics of past orders. Finally modified user.py in /apps to add respective routes, and user.py in /models to add appropriate SQL queries. 

Ciaran - Sellers Guru
app/users.py: Added search on orders to fulfill as well as orders to fulfill table. Added fulfill order function. Added way to update inventory, add product, and delete product from sellers page. 
app/models/user.py: added queries for creating new product, updating inventory, removing from inventory, getting inventory items, and getting a sellers’ orders + items. Also allows seller to mark order as fulfilled.
app/templates/add_product.html: added html to be able to add a new product from a sellers’ view
app/templates/seller_products.html: expand on first table of products for sale, allowing to add/subtract quantity and delete an item. Also added new orders to fulfill, listing orders chronologically and allowing a user to search for specifics, as well as mark an order as fulfilled.
app/templates/sales.html: matched base.html template for same look throughout
