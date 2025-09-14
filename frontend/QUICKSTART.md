# DocTracer Frontend - Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ installed
- Backend API running on port 5001

### Quick Start
1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173`

## 📱 Features

- **Dashboard**: Overview with statistics and quick actions
- **Tree Visualization**: Interactive D3.js tree view of government structure
- **Department Changes**: Detailed view of all modifications
- **Responsive Design**: Works on desktop and mobile
- **Real-time Data**: Connects to your backend API

## 🔧 Configuration

The frontend automatically connects to `http://localhost:5001` for the API. If you need to change this:

1. Create a `.env` file in the frontend directory
2. Add: `VITE_API_BASE=http://your-api-url:port`

## 🏗️ Build for Production

```bash
npm run build
```

This creates a `dist/` folder with optimized production files.

## 🎨 Customization

- **Colors**: Edit `src/index.css` for custom color schemes
- **Components**: All components are in `src/components/`
- **Styling**: Uses custom CSS classes instead of Tailwind utilities

## 🐛 Troubleshooting

- **Build errors**: Run `npm install` to ensure all dependencies are installed
- **API connection**: Verify your backend is running on port 5001
- **Port conflicts**: Change the port in `vite.config.ts` if needed

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   ├── contexts/           # React contexts
│   ├── App.tsx            # Main app
│   └── index.css          # Styles
├── public/                 # Static assets
├── package.json           # Dependencies
└── vite.config.ts         # Vite configuration
```

## 🔗 API Endpoints

The frontend expects these API endpoints:
- `GET /api/tree` - Government structure tree
- `GET /api/summary` - Change statistics
- `GET /api/departments` - Department changes
- `GET /api/filter` - Filtered data

## 🚀 Ready to Go!

Your modern Vite + React + TypeScript frontend is now ready! The application provides a beautiful, responsive interface for tracking government structure changes with interactive visualizations and real-time data updates.
