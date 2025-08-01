# Product Details Page Testing Guide

## Overview
The QuickVendor application now supports detailed product views that customers can access by clicking on products in the storefront. This guide covers testing the new functionality.

## New Features Added
1. **Product Details Page** - Individual product pages with full details
2. **Multi-Image Gallery** - Support for up to 5 images per product with navigation
3. **Clickable Product Cards** - Products in storefront now link to detail pages
4. **Enhanced Navigation** - Back to store functionality

## URL Structure
- **Storefront**: `/store/{username}`
- **Product Details**: `/store/{username}/product/{productId}`

## Testing Steps

### 1. Storefront Navigation
1. Visit a real storefront: `http://localhost:5175/store/sarah.fashion`
2. Verify products are displayed with:
   - Product images (clickable)
   - Product names (clickable)
   - Prices
   - "View Details" button
   - "Buy Now" WhatsApp button
3. Click on any product image, name, or "View Details" button
4. Verify navigation to the product details page

### 2. Product Details Page Features
**URL**: `http://localhost:5175/store/{username}/product/{productId}`

**Header Section:**
- Back to store button with vendor name
- Vendor name display

**Image Gallery:**
- Main product image display
- Image navigation arrows (if multiple images)
- Image indicator dots (if multiple images)
- Thumbnail grid (if multiple images)
- Click thumbnails to change main image

**Product Information:**
- Product name
- Price display
- Stock status indicator
- Product description
- WhatsApp contact button
- Store information card

**Actions:**
- WhatsApp button opens with pre-filled message
- "View All Products" returns to storefront
- Click tracking is recorded

### 3. Multi-Image Testing
To test multi-image functionality:

1. **Create a product with multiple images:**
   - Login to vendor dashboard: `http://localhost:5175/dashboard`
   - Add a new product with 2-5 images
   - Save the product

2. **View in storefront:**
   - Navigate to the storefront
   - Click on the multi-image product
   - Test image navigation:
     - Click left/right arrows
     - Click thumbnail images
     - Click indicator dots

### 4. End-to-End Testing Workflow

**Step 1: Create Test Data**
```bash
# Login to dashboard
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"

# Create product with multiple images
curl -X POST "http://localhost:8000/api/products/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "name=Test Multi-Image Product" \
  -F "price=99.99" \
  -F "description=A product with multiple images for testing" \
  -F "is_available=true" \
  -F "image_1=@/path/to/image1.jpg" \
  -F "image_2=@/path/to/image2.jpg" \
  -F "image_3=@/path/to/image3.jpg"
```

**Step 2: Test Frontend Flow**
1. Visit: `http://localhost:5175/store/test`
2. Click on the test product
3. Verify URL: `http://localhost:5175/store/test/product/{productId}`
4. Test all image navigation features
5. Click WhatsApp button and verify message format
6. Return to store and verify navigation

### 5. Error Handling Testing

**Test Invalid URLs:**
- `http://localhost:5175/store/nonexistent/product/123` - Should show "Product Not Found"
- `http://localhost:5175/store/sarah.fashion/product/invalid` - Should show error

**Test Unavailable Products:**
- Create a product and set `is_available=false`
- Try to access directly - should show "Product Not Available"

### 6. Mobile Responsiveness
Test on different screen sizes:
- Desktop (1200px+)
- Tablet (768px-1199px)
- Mobile (320px-767px)

Verify:
- Image gallery adapts to screen size
- Buttons remain accessible
- Text remains readable
- Navigation works on touch devices

### 7. Performance Testing
- Check image loading times
- Verify lazy loading on storefront
- Test with slow network connection
- Verify click tracking doesn't delay navigation

## Expected Behaviors

### Image Gallery
- **Single Image**: No navigation controls shown
- **Multiple Images**: Navigation arrows, dots, and thumbnails displayed
- **Image Loading**: Fallback to placeholder if image fails to load
- **Responsive**: Gallery adapts to screen size

### Navigation
- **Back Button**: Returns to storefront with vendor name
- **Breadcrumb**: Shows current location
- **WhatsApp**: Opens with pre-formatted message
- **Click Tracking**: Increments product view count

### Error States
- **Product Not Found**: Clear error message with back button
- **Network Error**: Graceful error handling
- **Loading States**: Spinner while fetching data

## API Endpoints Used
- `GET /api/store/{username}` - Get storefront data including products
- `POST /api/products/{productId}/track-click` - Track product views

## Files Modified
- `src/App.tsx` - Added product details route
- `src/components/ProductDetailsPage.tsx` - New component (created)
- `src/components/StorefrontPage.tsx` - Added clickable product cards
- `src/apiService.ts` - Added required API functions

## Success Criteria
✅ Product cards are clickable in storefront
✅ Product details page loads with correct data
✅ Multi-image gallery works (navigation, thumbnails)
✅ WhatsApp integration works from details page
✅ Navigation between storefront and details works
✅ Click tracking functions correctly
✅ Error handling works for invalid URLs
✅ Mobile responsive design
✅ No console errors or TypeScript compilation issues

## Troubleshooting

**Images not loading:**
- Check if backend uploads directory is accessible
- Verify image URLs in API response
- Check CORS settings for image serving

**Navigation not working:**
- Verify React Router setup in App.tsx
- Check route order (more specific routes first)
- Ensure Link components are properly imported

**API calls failing:**
- Check backend server is running on port 8000
- Verify VITE_API_BASE_URL environment variable
- Check network requests in browser dev tools
