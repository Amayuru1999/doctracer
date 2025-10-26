# Frontend Setup Guide

This guide will help you set up the DocTracer frontend application, a React-based web interface for visualizing government structure and tracking changes in gazettes.

## 📋 Prerequisites

- **Node.js 18+** - Download from [nodejs.org](https://nodejs.org/)
- **npm** or **yarn** - Package manager (comes with Node.js)
- **Git** - For version control

## 🚀 Quick Start

### 1. Navigate to Frontend Directory

```bash
cd frontend
```

### 2. Install Dependencies

```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### 3. Environment Configuration

Create a `.env` file in the frontend directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:5000
VITE_APP_TITLE=DocTracer

# Development Configuration
VITE_DEV_MODE=true
```

### 4. Start Development Server

```bash
# Development mode
npm run dev

# Or using yarn
yarn dev
```

The application will be available at: **http://localhost:5173**

## 🛠️ Development Commands

### Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

### Build for Production

```bash
# Create production build
npm run build

# Preview production build locally
npm run preview
```

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard.tsx    # Main dashboard
│   │   ├── NetworkGraph.tsx # Network visualization
│   │   ├── TreeView.tsx     # Tree structure view
│   │   └── ...
│   ├── contexts/            # React contexts
│   │   ├── AppContext.tsx   # Global app state
│   │   └── DataContext.tsx  # Data management
│   ├── services/            # API services
│   │   └── api.ts           # API client
│   ├── types/               # TypeScript types
│   │   └── index.ts         # Type definitions
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # App entry point
│   └── index.css            # Global styles
├── public/                  # Static assets
├── package.json             # Dependencies and scripts
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS config
└── tsconfig.json            # TypeScript config
```

## 🎨 Technologies Used

- **React 18** - Frontend framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **React Force Graph** - Network visualization
- **Lucide React** - Icon library

## 🔧 Configuration

### Vite Configuration

The project uses Vite for fast development and building. Key configuration in `vite.config.ts`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

### Tailwind CSS

Tailwind CSS is configured for utility-first styling. Configuration in `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#3b82f6',
        secondary: '#64748b',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

### TypeScript Configuration

TypeScript is configured for strict type checking. Key settings in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## 🌐 API Integration

### Backend API Connection

The frontend connects to the backend API through the `VITE_API_URL` environment variable:

```typescript
// src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const api = {
  // Get government structure
  getStructure: () => fetch(`${API_BASE_URL}/api/structure`),
  
  // Get changes between gazettes
  getChanges: (oldId: string, newId: string) => 
    fetch(`${API_BASE_URL}/api/changes?old=${oldId}&new=${newId}`),
  
  // Get analytics data
  getAnalytics: () => fetch(`${API_BASE_URL}/api/analytics`),
};
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:5000` |
| `VITE_APP_TITLE` | Application title | `DocTracer` |
| `VITE_DEV_MODE` | Development mode flag | `true` |

## 🎯 Key Features

### 1. Interactive Dashboard
- Overview of government structure
- Real-time statistics
- Quick navigation to different views

### 2. Network Visualization
- Interactive force-directed graph
- Zoom and pan capabilities
- Node and edge highlighting
- Search and filter functionality

### 3. Tree View
- Hierarchical government structure
- Expandable/collapsible nodes
- Department and ministry details

### 4. Analytics Dashboard
- Change tracking over time
- Statistical analysis
- Export capabilities

## 🧪 Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Test Structure

```
src/
├── __tests__/              # Test files
│   ├── components/         # Component tests
│   ├── services/          # Service tests
│   └── utils/             # Utility tests
```

## 🚀 Deployment

### Production Build

```bash
# Create production build
npm run build

# The build output will be in the `dist/` directory
```

### Docker Deployment

```bash
# Build Docker image
docker build -t doctracer-frontend .

# Run container
docker run -p 5173:5173 doctracer-frontend
```

### Static Hosting

The built application can be deployed to any static hosting service:

- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod --dir=dist`
- **AWS S3**: Upload `dist/` contents to S3 bucket
- **GitHub Pages**: Use GitHub Actions for deployment

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Kill process using port 5173
lsof -ti:5173 | xargs kill -9

# Or use a different port
npm run dev -- --port 3000
```

#### 2. Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for TypeScript errors
npm run type-check
```

#### 3. API Connection Issues

```bash
# Verify backend is running
curl http://localhost:5000/api/health

# Check environment variables
echo $VITE_API_URL
```

#### 4. Styling Issues

```bash
# Rebuild Tailwind CSS
npm run build:css

# Check Tailwind configuration
npx tailwindcss --help
```

### Performance Optimization

#### 1. Bundle Analysis

```bash
# Analyze bundle size
npm run build:analyze

# Check for large dependencies
npm run audit
```

#### 2. Code Splitting

```typescript
// Lazy load components
const NetworkGraph = lazy(() => import('./components/NetworkGraph'));
const TreeView = lazy(() => import('./components/TreeView'));
```

#### 3. Image Optimization

```bash
# Optimize images
npm run optimize:images

# Use WebP format for better compression
```

## 📚 Development Guidelines

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries
- Write meaningful component names

### Component Structure

```typescript
// Example component structure
interface ComponentProps {
  title: string;
  data: DataType[];
  onAction: (item: DataType) => void;
}

export const Component: React.FC<ComponentProps> = ({ 
  title, 
  data, 
  onAction 
}) => {
  // Component logic
  return (
    <div className="component-container">
      {/* Component JSX */}
    </div>
  );
};
```

### State Management

- Use React Context for global state
- Use local state for component-specific data
- Implement proper state updates
- Handle loading and error states

## 🔗 Related Documentation

- [Backend Setup Guide](./backend-setup.md)
- [Neo4j Data Loading Guide](./neo4j-setup.md)
- [API Documentation](./api-documentation.md)
- [Deployment Guide](./deployment.md)

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review the [GitHub Issues](https://github.com/yourusername/doctracer/issues)
3. Check the [API documentation](./api-documentation.md)
4. Verify backend connectivity

---

**Happy Coding! 🚀**
