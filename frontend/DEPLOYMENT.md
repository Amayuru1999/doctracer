# Deploy to Vercel - Frontend + Backend

This guide will help you deploy both the frontend and backend to Vercel as a single project.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Git Repository**: Your code should be in a Git repository (GitHub, GitLab, etc.)
3. **Node.js**: Version 18+ installed locally
4. **Vercel CLI**: Install with `npm i -g vercel`

## Step 1: Prepare Your Project

### 1.1 Install Dependencies
```bash
cd frontend
npm install
```

### 1.2 Build the Frontend
```bash
npm run build
```

## Step 2: Deploy to Vercel

### 2.1 Using Vercel CLI (Recommended)

```bash
# Login to Vercel
vercel login

# Deploy from the frontend directory
cd frontend
vercel

# Follow the prompts:
# - Set up and deploy: Yes
# - Which scope: Select your account
# - Link to existing project: No
# - Project name: doctracer-frontend (or your preferred name)
# - Directory: ./ (current directory)
# - Override settings: No
```

### 2.2 Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

## Step 3: Configure Environment Variables

In your Vercel project dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add the following variables:

```
VITE_API_BASE=https://your-project-name.vercel.app
NEO4J_URI=your_neo4j_connection_string
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

## Step 4: Configure Python Runtime

Vercel will automatically detect the Python backend in the `/api` folder and deploy it as serverless functions.

### 4.1 Verify API Endpoints

After deployment, test these endpoints:

- `https://your-project.vercel.app/api/tree` - Government structure data
- `https://your-project.vercel.app/api/summary` - Summary statistics
- `https://your-project.vercel.app/api/departments` - Department changes
- `https://your-project.vercel.app/api/health` - Health check

## Step 5: Update Frontend Configuration

### 5.1 Production API Base

Update your frontend environment variables to point to the production API:

```bash
# In Vercel dashboard, set:
VITE_API_BASE=https://your-project-name.vercel.app
```

### 5.2 Redeploy

After setting environment variables, redeploy:

```bash
vercel --prod
```

## Step 6: Custom Domain (Optional)

1. In Vercel dashboard, go to **Settings** → **Domains**
2. Add your custom domain
3. Update DNS records as instructed
4. Update `VITE_API_BASE` to use your custom domain

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (18+ required)
   - Verify all dependencies are installed
   - Check for TypeScript errors

2. **API Not Working**
   - Verify environment variables are set
   - Check Vercel function logs
   - Ensure API routes are in `/api` folder

3. **CORS Issues**
   - Backend includes CORS middleware
   - Frontend uses relative API paths

### Debugging

1. **Check Vercel Function Logs**
   - Go to **Functions** tab in dashboard
   - Click on function to see logs

2. **Test API Locally**
   ```bash
   cd frontend/api
   python index.py
   # Test at http://localhost:8000
   ```

3. **Verify Environment Variables**
   - Check Vercel dashboard
   - Ensure variables are set for production

## Production Considerations

1. **Database Connection**
   - Use production Neo4j instance
   - Set proper connection pooling
   - Implement retry logic

2. **Security**
   - Add authentication if needed
   - Rate limiting
   - Input validation

3. **Monitoring**
   - Set up Vercel Analytics
   - Monitor function performance
   - Set up alerts for errors

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/runtimes/python)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Project Structure After Deployment

```
your-project.vercel.app/
├── / (Frontend - React + Vite)
├── /api (Backend - FastAPI)
│   ├── /tree
│   ├── /summary
│   ├── /departments
│   └── /filter
└── /health
```

Your frontend and backend are now deployed as a single Vercel project with automatic scaling and global CDN!
