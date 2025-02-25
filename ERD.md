# Mini-Amazon Schema Diagram (Compact, Condensed)

Below is a Mermaid diagram showing exact column-to-column relationships in a more compact, top-to-bottom layout.

```mermaid
%%{init: {"flowchart": {"nodeSpacing": 15, "rankSpacing": 15}}}%%
flowchart LR

%% ------------------ USERS ------------------
subgraph USERS [USERS]
    U_user_id((user_id PK))
    U_email[email]
    U_full_name[full_name]
    U_address[address]
    U_password[password]
    U_balance[balance]
    U_is_seller[is_seller]
end

%% ---------------- PRODUCT_CATEGORIES ----------------
subgraph PROD_CATS [PRODUCT_CATEGORIES]
    PC_category_id((category_id PK))
    PC_category_name[category_name]
    PC_description[description]
end

%% ---------------- PRODUCTS ----------------
subgraph PRODUCTS [PRODUCTS]
    P_product_id((product_id PK))
    P_category_id[category_id FK]
    P_name[name]
    P_description[description]
    P_image_url[image_url]
    P_created_by[created_by FK]
    P_created_at[created_at]
end

%% ---------------- SELLER_INVENTORY ----------------
subgraph SELLER_INV [SELLER_INVENTORY]
    SI_inventory_id((inventory_id PK))
    SI_seller_id[seller_id FK]
    SI_product_id[product_id FK]
    SI_price[price]
    SI_quantity[quantity]
    SI_last_updated[last_updated]
end

%% ---------------- CARTS ----------------
subgraph CARTS [CARTS]
    C_cart_id((cart_id PK))
    C_user_id[user_id FK]
    C_updated_at[updated_at]
end

%% ---------------- CART_ITEMS ----------------
subgraph CART_ITEMS [CART_ITEMS]
    CI_cart_item_id((cart_item_id PK))
    CI_cart_id[cart_id FK]
    CI_seller_id[seller_id FK]
    CI_product_id[product_id FK]
    CI_quantity[quantity]
    CI_unit_price[unit_price]
    CI_added_at[added_at]
end

%% ---------------- ORDERS ----------------
subgraph ORDERS [ORDERS]
    O_order_id((order_id PK))
    O_buyer_id[buyer_id FK]
    O_order_date[order_date]
    O_total_amount[total_amount]
    O_fulfillment_status[fulfillment_status]
end

%% ---------------- ORDER_ITEMS ----------------
subgraph ORDER_ITEMS [ORDER_ITEMS]
    OI_order_item_id((order_item_id PK))
    OI_order_id[order_id FK]
    OI_seller_id[seller_id FK]
    OI_product_id[product_id FK]
    OI_quantity[quantity]
    OI_unit_price[unit_price]
    OI_fulfillment_status[fulfillment_status]
    OI_fulfillment_date[fulfillment_date]
end

%% ---------------- PRODUCT_REVIEWS ----------------
subgraph PROD_REVIEWS [PRODUCT_REVIEWS]
    PR_review_id((review_id PK))
    PR_product_id[product_id FK]
    PR_user_id[user_id FK]
    PR_rating[rating]
    PR_review_text[review_text]
    PR_review_date[review_date]
end

%% ---------------- SELLER_REVIEWS ----------------
subgraph SELLER_REVIEWS [SELLER_REVIEWS]
    SR_review_id((review_id PK))
    SR_seller_id[seller_id FK]
    SR_user_id[user_id FK]
    SR_rating[rating]
    SR_review_text[review_text]
    SR_review_date[review_date]
end

%% ---------------- MESSAGE_THREADS ----------------
subgraph MSG_THREADS [MESSAGE_THREADS]
    MT_thread_id((thread_id PK))
    MT_buyer_id[buyer_id FK]
    MT_seller_id[seller_id FK]
    MT_order_id[order_id FK]
    MT_created_at[created_at]
end

%% ---------------- MESSAGES ----------------
subgraph MESSAGES [MESSAGES]
    M_message_id((message_id PK))
    M_thread_id[thread_id FK]
    M_sender_id[sender_id FK]
    M_message_text[message_text]
    M_sent_at[sent_at]
end

%% ---------------- RELATIONSHIPS ----------------
P_category_id --> PC_category_id
P_created_by --> U_user_id
SI_seller_id --> U_user_id
SI_product_id --> P_product_id
C_user_id --> U_user_id
CI_cart_id --> C_cart_id
CI_seller_id --> U_user_id
CI_product_id --> P_product_id
O_buyer_id --> U_user_id
OI_order_id --> O_order_id
OI_seller_id --> U_user_id
OI_product_id --> P_product_id
PR_product_id --> P_product_id
PR_user_id --> U_user_id
SR_seller_id --> U_user_id
SR_user_id --> U_user_id
MT_buyer_id --> U_user_id
MT_seller_id --> U_user_id
MT_order_id --> O_order_id
M_thread_id --> MT_thread_id
M_sender_id --> U_user_id
