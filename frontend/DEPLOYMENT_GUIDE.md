# 🚀 Frontend Deployment Guide

This guide will help you deploy your React frontend to either Vercel or Railway platforms.

## 📋 Prerequisites

- Node.js 18+ installed
- Git repository with your code
- GitHub account (for automatic deployments)

---

## 🌟 Option 1: Vercel Deployment (Recommended)

Vercel is the best choice for React applications with excellent free tier and automatic deployments.

### Method A: Quick Deploy (Automated)

1. **Run the deployment script:**
   ```bash
   cd frontend
   ./deploy.sh
   ```

2. **Follow the prompts:**
   - Login to Vercel when prompted
   - Choose your project settings
   - Wait for deployment to complete

### Method B: Manual Deploy

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   cd frontend
   vercel --prod
   ```

### Method C: GitHub Integration (Recommended for Production)

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy frontend"
   git push origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Select the `frontend` folder as root directory
   - Deploy!

### Environment Variables for Vercel

Set these in your Vercel dashboard (Project Settings → Environment Variables):

```env
VITE_API_BASE=https://your-project-name.vercel.app
NEO4J_URI=your_neo4j_connection_string
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

---

## 🚂 Option 2: Railway Deployment

Railway offers a generous free tier and is great for full-stack applications.

### Method A: Railway CLI

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize and Deploy:**
   ```bash
   cd frontend
   railway init
   railway up
   ```

### Method B: GitHub Integration

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

2. **Connect to Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `frontend` folder
   - Deploy!

### Environment Variables for Railway

Set these in your Railway dashboard (Project → Variables):

```env
VITE_API_BASE=https://your-project-name.railway.app
NEO4J_URI=your_neo4j_connection_string
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

---

## 🔧 Configuration Files

Your project already includes the necessary configuration files:

- `vercel.json` - Vercel deployment configuration
- `railway.json` - Railway deployment configuration
- `package.json` - Build scripts and dependencies
- `vite.config.ts` - Vite build configuration

---

## 🚀 Build Process

Both platforms will automatically:

1. **Install dependencies:** `npm install`
2. **Build the project:** `npm run build`
3. **Serve the static files:** From `dist/` directory

### Build Commands

```bash
# Development
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 🌐 Custom Domain (Optional)

### Vercel
1. Go to Project Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

### Railway
1. Go to Project → Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed

---

## 📊 Monitoring & Analytics

### Vercel
- Built-in analytics dashboard
- Performance monitoring
- Real-time logs

### Railway
- Application logs
- Resource usage monitoring
- Health checks

---

## 🔄 Automatic Deployments

Both platforms support automatic deployments:

- **Vercel:** Deploys on every push to main branch
- **Railway:** Deploys on every push to main branch

### Branch-based Deployments

- **Vercel:** Creates preview deployments for feature branches
- **Railway:** Can be configured for branch-based deployments

---

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures:**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm run build
   ```

2. **Environment Variables:**
   - Ensure all required variables are set
   - Check variable names (case-sensitive)
   - Restart deployment after adding variables

3. **API Connection Issues:**
   - Verify API base URL is correct
   - Check CORS settings
   - Ensure backend is deployed and accessible

4. **Static File Issues:**
   - Check if `dist/` folder is generated
   - Verify build output directory
   - Check for TypeScript errors

### Debug Commands

```bash
# Check build locally
npm run build
npm run preview

# Check for TypeScript errors
npx tsc --noEmit

# Check for linting errors
npm run lint
```

---

## 📈 Performance Optimization

### Vite Configuration
Your `vite.config.ts` already includes:
- Code splitting
- Minification with Terser
- Manual chunks for better caching

### Additional Optimizations
- Enable gzip compression (automatic on both platforms)
- Use CDN for static assets (automatic on both platforms)
- Optimize images and assets

---

## 🔒 Security

### Environment Variables
- Never commit sensitive data to Git
- Use platform-specific environment variable systems
- Rotate API keys regularly

### CORS Configuration
Your `vercel.json` includes CORS headers for API routes.

---

## 📞 Support

### Vercel
- [Documentation](https://vercel.com/docs)
- [Community](https://github.com/vercel/vercel/discussions)
- [Support](https://vercel.com/support)

### Railway
- [Documentation](https://docs.railway.app)
- [Community](https://discord.gg/railway)
- [Support](https://railway.app/support)

---

## 🎉 Success!

Once deployed, your frontend will be available at:
- **Vercel:** `https://your-project-name.vercel.app`
- **Railway:** `https://your-project-name.railway.app`

Your government structure visualization app is now live! 🚀
