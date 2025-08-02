# QuickVendor Frontend

This is the frontend for the QuickVendor application. It is built using React and Vite.

## Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

   The development server will be available at `http://localhost:5173`.

## Production Build

1. **Build the application:**
   ```bash
   npm run build
   ```

2. The production build will be in the `dist` directory.

## Deployment

### Using Render

1. Ensure the `render.yaml` configuration is correct.
2. Deploy the project using the Render dashboard or CLI.

### Using Netlify

1. Ensure the `_redirects` file in the `public` directory is present.
2. Connect the repository to your Netlify account and deploy.

### Using Vercel

1. Ensure the `vercel.json` configuration is correct.
2. Deploy using the Vercel CLI or dashboard.

## Environment Variables

Make sure to set the `VITE_API_BASE_URL` environment variable in your deployment platform.
