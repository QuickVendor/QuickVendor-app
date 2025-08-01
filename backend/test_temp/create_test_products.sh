#!/bin/bash

# QuickVendor Product Creation Test Script
# Usage: ./create_test_products.sh <user_token> <store_type>
# Store types: fashion, electronics, demo

set -e

# Configuration
API_BASE="http://localhost:8000/api/products"
TOKEN="$1"
STORE_TYPE="$2"

if [ -z "$TOKEN" ] || [ -z "$STORE_TYPE" ]; then
    echo "Usage: $0 <user_token> <store_type>"
    echo "Store types: fashion, electronics, demo"
    exit 1
fi

echo "🚀 Creating test products for $STORE_TYPE store..."

case "$STORE_TYPE" in
    "fashion")
        echo "👗 Creating fashion products..."
        
        # Designer Handbag
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Designer Leather Handbag" \
            -F "price=89.99" \
            -F "description=Premium genuine leather handbag with gold-tone hardware. Perfect for professional and casual occasions." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Sunglasses
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Trendy Sunglasses" \
            -F "price=25.50" \
            -F "description=UV400 protection sunglasses with polarized lenses. Stylish frames suitable for all face shapes." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Gold Necklace
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Statement Gold Necklace" \
            -F "price=35.75" \
            -F "description=Bold chunky chain necklace in gold finish. Makes a perfect statement piece for any outfit." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Silk Scarf (Out of stock)
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Silk Scarf Collection" \
            -F "price=45.00" \
            -F "description=Set of 3 premium silk scarves in different patterns. Versatile accessory for multiple styling options." \
            -F "is_available=false" | jq '.name // .detail'
        
        # Vintage Watch
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Vintage Style Watch" \
            -F "price=120.00" \
            -F "description=Classic analog watch with leather strap. Water-resistant with Japanese movement mechanism." \
            -F "is_available=true" | jq '.name // .detail'
        ;;
        
    "electronics")
        echo "📱 Creating electronics products..."
        
        # Wireless Earbuds
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Wireless Bluetooth Earbuds" \
            -F "price=79.99" \
            -F "description=True wireless earbuds with active noise cancellation. 6-hour battery life with charging case." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Phone Stand
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Smartphone Stand Adjustable" \
            -F "price=18.99" \
            -F "description=Multi-angle aluminum phone stand compatible with all smartphones and small tablets." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Power Bank
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Fast Charging Power Bank 20000mAh" \
            -F "price=55.50" \
            -F "description=High-capacity portable charger with USB-C PD and wireless charging. LED battery indicator." \
            -F "is_available=true" | jq '.name // .detail'
        
        # USB Cable
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=USB-C to Lightning Cable 2m" \
            -F "price=15.99" \
            -F "description=MFi certified charging cable with braided nylon design. Fast charging and data sync support." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Bluetooth Speaker (Out of stock)
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Bluetooth Speaker Waterproof" \
            -F "price=45.75" \
            -F "description=Portable Bluetooth speaker with IPX7 waterproof rating. 12-hour battery life and deep bass." \
            -F "is_available=false" | jq '.name // .detail'
        
        # Wireless Charging Pad
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Wireless Charging Pad" \
            -F "price=25.99" \
            -F "description=10W fast wireless charger compatible with all Qi-enabled devices. LED charging indicator." \
            -F "is_available=true" | jq '.name // .detail'
        ;;
        
    "demo")
        echo "☕ Creating demo products..."
        
        # Coffee Beans
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Premium Coffee Beans" \
            -F "price=25.99" \
            -F "description=High-quality arabica coffee beans from Ethiopia. Medium roast with chocolate and citrus notes." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Dark Chocolate
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Artisan Dark Chocolate" \
            -F "price=15.50" \
            -F "description=Handcrafted dark chocolate with 70% cocoa content. Made with organic ingredients." \
            -F "is_available=true" | jq '.name // .detail'
        
        # Honey (Out of stock)
        curl -s -X POST "$API_BASE/" \
            -H "Authorization: Bearer $TOKEN" \
            -F "name=Organic Wildflower Honey" \
            -F "price=18.75" \
            -F "description=Pure wildflower honey from local beekeepers. Raw and unprocessed for maximum flavor." \
            -F "is_available=false" | jq '.name // .detail'
        ;;
        
    *)
        echo "❌ Invalid store type. Use: fashion, electronics, or demo"
        exit 1
        ;;
esac

echo "✅ Products created successfully!"
echo "📊 Check your vendor dashboard to see the new products"
echo "🌐 Visit your storefront to see public product display"
