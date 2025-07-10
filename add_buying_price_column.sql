-- Add buying_price column to orderitems table
-- This preserves historical buying price data even if admin changes product buying price later

ALTER TABLE orderitems 
ADD COLUMN buying_price NUMERIC(10, 2);

-- Update existing order items with current product buying prices
-- This ensures existing orders have buying price data
UPDATE orderitems 
SET buying_price = products.buyingprice 
FROM products 
WHERE orderitems.productid = products.id;

-- Make the column NOT NULL after populating existing data
ALTER TABLE orderitems 
ALTER COLUMN buying_price SET NOT NULL; 