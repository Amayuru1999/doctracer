# Government Structure Frontend

A modern React-based frontend for tracking and visualizing government structure changes, built with Vite, TypeScript, and Tailwind CSS.

## 🚀 Features

- **Interactive Tree Visualization**: Colorful tile-based layout for ministries
- **Department Management**: Click tiles to view departments in popup modals
- **Real-time Data**: Live updates from backend API
- **Responsive Design**: Works on all devices and screen sizes
- **Modern UI**: Beautiful gradients, animations, and glassmorphism effects

## 🛠️ Tech Stack

- **Frontend**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS + Custom CSS
- **Icons**: Lucide React
- **Routing**: React Router DOM
- **Build Tool**: Vite
- **Deployment**: Vercel

## 📦 Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd doctracer/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🚀 Deployment

### Quick Deploy to Vercel

```bash
# Run the deployment script
./deploy.sh

# Or deploy manually
vercel --prod
```

### Manual Deployment

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel --prod
   ```

### Environment Variables

Set these in your Vercel dashboard:

```env
VITE_API_BASE=https://your-project.vercel.app
NEO4J_URI=your_neo4j_connection_string
NEO4J_USER=your_neo4j_username
NEO4J_PASSWORD=your_neo4j_password
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── TreeVisualization.tsx  # Ministry tiles
│   │   ├── DepartmentChanges.tsx  # Department changes
│   │   └── Header.tsx       # Navigation header
│   ├── contexts/            # React contexts
│   │   └── DataContext.tsx  # Data management
│   ├── assets/              # Static assets
│   └── main.tsx             # App entry point
├── api/                     # Backend API (FastAPI)
│   ├── index.py             # Main API file
│   └── requirements.txt     # Python dependencies
├── public/                  # Public assets
├── dist/                    # Build output
└── vercel.json             # Vercel configuration
```

## 🌐 API Endpoints

The backend provides these endpoints:

- `GET /api/tree` - Government structure data
- `GET /api/summary` - Summary statistics
- `GET /api/departments` - Department changes
- `GET /api/filter` - Filtered data
- `GET /api/health` - Health check

## 🎨 UI Components

### Ministry Tiles
- **Colorful Gradients**: Each ministry gets a unique color scheme
- **Interactive**: Click to view departments
- **Status Indicators**: Visual status representation
- **Hover Effects**: Smooth animations and feedback

### Department Modal
- **Popup Interface**: Clean modal for department details
- **Responsive Design**: Works on all screen sizes
- **Status Badges**: Clear status and type indicators

### Dashboard
- **Statistics Cards**: Node counts and change summaries
- **Quick Actions**: Navigation to different sections
- **Real-time Data**: Live updates from API

## 🔒 Security

- CORS enabled for cross-origin requests
- Input validation on all API endpoints
- Environment variable protection
- Secure API routing

## 📱 Responsive Design

- **Mobile First**: Optimized for mobile devices
- **Breakpoints**: Tailwind CSS responsive utilities
- **Touch Friendly**: Optimized for touch interactions
- **Cross Browser**: Works on all modern browsers

## 🚀 Performance

- **Code Splitting**: Automatic chunk optimization
- **Lazy Loading**: Components loaded on demand
- **Optimized Builds**: Minified and compressed assets
- **CDN**: Global content delivery network

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version (18+ required)
   - Clear node_modules and reinstall
   - Check TypeScript errors

2. **API Not Working**
   - Verify environment variables
   - Check Vercel function logs
   - Ensure API routes are accessible

3. **Styling Issues**
   - Clear browser cache
   - Check Tailwind CSS compilation
   - Verify CSS imports

### Debug Mode

```bash
# Enable debug logging
DEBUG=* npm run dev

# Check Vercel logs
vercel logs
```

## 📚 Documentation

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vercel Documentation](https://vercel.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Create an issue on GitHub
- **Documentation**: Check DEPLOYMENT.md for deployment help
- **Community**: Join our discussion forum

---

**Built with ❤️ for Government Transparency**
