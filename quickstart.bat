@echo off
REM DocTracer Quick Start Script for Windows
REM This script will set up and run the entire DocTracer application

echo 🚀 DocTracer Quick Start Script
echo ================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose and try again.
    pause
    exit /b 1
)

echo ✅ Docker and Docker Compose are available

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # Neo4j Configuration
        echo NEO4J_URI=bolt://localhost:7687
        echo NEO4J_USER=neo4j
        echo NEO4J_PASSWORD=password123
        echo.
        echo # Flask Configuration
        echo FLASK_ENV=development
        echo FLASK_DEBUG=1
        echo FLASK_APP=doctracer
        echo.
        echo # API Configuration
        echo API_URL=http://localhost:5000
    ) > .env
    echo ✅ Created .env file
) else (
    echo ✅ .env file already exists
)

REM Create frontend .env file if it doesn't exist
if not exist frontend\.env (
    echo 📝 Creating frontend .env file...
    (
        echo # API Configuration
        echo VITE_API_URL=http://localhost:5000
        echo VITE_APP_TITLE=DocTracer
        echo VITE_DEV_MODE=true
    ) > frontend\.env
    echo ✅ Created frontend .env file
) else (
    echo ✅ Frontend .env file already exists
)

REM Create web visualizer .env file if it doesn't exist
if not exist backend\web_visualizer\.env (
    echo 📝 Creating web visualizer .env file...
    (
        echo # Neo4j Configuration
        echo NEO4J_URI=bolt://localhost:7687
        echo NEO4J_USER=neo4j
        echo NEO4J_PASSWORD=password123
        echo.
        echo # Flask Configuration
        echo FLASK_HOST=0.0.0.0
        echo FLASK_PORT=5001
        echo FLASK_DEBUG=True
    ) > backend\web_visualizer\.env
    echo ✅ Created web visualizer .env file
) else (
    echo ✅ Web visualizer .env file already exists
)

REM Stop any existing containers
echo 🛑 Stopping any existing containers...
docker-compose down >nul 2>&1

REM Build and start services
echo 🔨 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 15 /nobreak >nul

REM Check service health
echo 🏥 Checking service health...

REM Check Neo4j
curl -s http://localhost:7474 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Neo4j is running at http://localhost:7474
) else (
    echo ❌ Neo4j is not responding
)

REM Check Backend
curl -s http://localhost:5000/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API is running at http://localhost:5000
) else (
    echo ⏳ Backend API is starting up...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:5000/api/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Backend API is now running at http://localhost:5000
    ) else (
        echo ❌ Backend API is not responding
    )
)

REM Check Web Visualizer
curl -s http://localhost:5001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Web Visualizer is running at http://localhost:5001
) else (
    echo ⏳ Web Visualizer is starting up...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:5001/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Web Visualizer is now running at http://localhost:5001
    ) else (
        echo ❌ Web Visualizer is not responding
    )
)

REM Check Frontend
curl -s http://localhost:5173 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running at http://localhost:5173
) else (
    echo ⏳ Frontend is starting up...
    timeout /t 10 /nobreak >nul
    curl -s http://localhost:5173 >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✅ Frontend is now running at http://localhost:5173
    ) else (
        echo ❌ Frontend is not responding
    )
)

echo.
echo 🎉 DocTracer is now running!
echo.
echo 📱 Access Points:
echo    Frontend: http://localhost:5173
echo    Backend API: http://localhost:5000
echo    Web Visualizer: http://localhost:5001
echo    Neo4j Browser: http://localhost:7474
echo.
echo 🔑 Neo4j Credentials:
echo    Username: neo4j
echo    Password: password123
echo.
echo 📚 Next Steps:
echo    1. Open http://localhost:5173 in your browser for the main app
echo    2. Open http://localhost:5001 for the web visualizer
echo    3. Check the README.md for detailed usage instructions
echo.
echo 🛑 To stop the services, run: docker-compose down
echo 🔄 To restart, run: docker-compose restart
echo 📊 To view logs, run: docker-compose logs -f
echo.
echo Happy Tracking! 🎯📊
pause
