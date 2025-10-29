# DocTracer - Digital Ocean Deployment Guide

This guide will help you deploy DocTracer on Digital Ocean with minimal server-side configuration.

## 🚀 Quick Deployment

### Prerequisites
- Digital Ocean Droplet (minimum 2GB RAM, 2 vCPUs recommended)
- Ubuntu 20.04 or 22.04 LTS
- Domain name (optional but recommended)

### One-Command Deployment

1. **SSH into your Digital Ocean droplet:**
   ```bash
   ssh root@your-droplet-ip
   ```

2. **Create a non-root user (if not already done):**
   ```bash
   adduser doctracer
   usermod -aG sudo doctracer
   su - doctracer
   ```

3. **Run the deployment script:**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/doctracer/main/deploy-digitalocean.sh | bash
   ```

That's it! The script will:
- Install Docker and Docker Compose
- Clone the repository
- Set up environment variables
- Configure firewall
- Build and start the application

## 🔧 Manual Deployment Steps

If you prefer manual deployment:

### 1. Install Dependencies
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo apt install -y git
```

### 2. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/doctracer.git
cd doctracer
```

### 3. Configure Environment
```bash
# Copy production environment template
cp .env.production .env

# Edit environment variables
nano .env
```

**Important:** Update these values in `.env`:
- `NEO4J_PASSWORD`: Set a secure password
- `API_URL`: Set to your domain or IP
- `SECRET_KEY`: Generate a secure random string
- `JWT_SECRET_KEY`: Generate a secure random string

### 4. Configure Firewall
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5001/tcp
sudo ufw allow 7474/tcp
```

### 5. Deploy Application
```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🌐 Access Your Application

After deployment, access your application at:

- **Frontend:** `http://your-droplet-ip:80`
- **API:** `http://your-droplet-ip:5001`
- **Neo4j Browser:** `http://your-droplet-ip:7474`

## 🔒 Security Recommendations

### 1. Change Default Passwords
```bash
# Edit .env file and update:
nano .env
# - NEO4J_PASSWORD
# - SECRET_KEY
# - JWT_SECRET_KEY
```

### 2. Set Up SSL/HTTPS (Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Update API_URL in .env to use HTTPS
```

### 3. Configure Nginx (Optional)
For better performance and SSL termination, set up Nginx as a reverse proxy.

## 🔄 Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.prod.yml logs

# Specific service
docker-compose -f docker-compose.prod.yml logs backend
```

### Restart Services
```bash
docker-compose -f docker-compose.prod.yml restart
```

### Update Application
```bash
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

### Stop Services
```bash
docker-compose -f docker-compose.prod.yml down
```

## 💾 Backup and Restore

### Create Backup
```bash
./backup.sh
```

### Restore from Backup
```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore Neo4j database
docker-compose -f docker-compose.prod.yml up -d neo4j
docker-compose -f docker-compose.prod.yml exec neo4j neo4j-admin database load --from-path=/backups neo4j backup_name.dump --overwrite-destination

# Restart all services
docker-compose -f docker-compose.prod.yml up -d
```

## 🐛 Troubleshooting

### Check Service Status
```bash
docker-compose -f docker-compose.prod.yml ps
```

### View Service Logs
```bash
docker-compose -f docker-compose.prod.yml logs [service-name]
```

### Restart Specific Service
```bash
docker-compose -f docker-compose.prod.yml restart [service-name]
```

### Check System Resources
```bash
# Memory usage
free -h

# Disk usage
df -h

# Docker system info
docker system df
```

### Common Issues

1. **Port already in use:**
   ```bash
   sudo netstat -tulpn | grep :5001
   sudo kill -9 <process-id>
   ```

2. **Permission denied:**
   ```bash
   sudo chown -R $USER:$USER ~/doctracer
   ```

3. **Out of memory:**
   - Upgrade to a larger droplet
   - Reduce Neo4j memory settings in docker-compose.prod.yml

## 📊 Monitoring

### System Monitoring
```bash
# Install htop for system monitoring
sudo apt install htop
htop
```

### Docker Monitoring
```bash
# Container stats
docker stats

# System usage
docker system df
```

### Application Health
```bash
# Test API endpoint
curl http://localhost:5001/gazettes

# Test frontend
curl http://localhost:80
```

## 🔄 Updates and Maintenance

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update application
cd ~/doctracer
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

### Scheduled Backups
Add to crontab for daily backups:
```bash
crontab -e
# Add this line for daily backup at 2 AM:
0 2 * * * cd ~/doctracer && ./backup.sh
```

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify environment variables in `.env`
3. Ensure all ports are open in firewall
4. Check system resources (memory, disk space)

## 🎉 Success!

Your DocTracer application should now be running on Digital Ocean with:
- ✅ 4 Base Gazettes loaded
- ✅ 3 Amendment Gazettes loaded
- ✅ Interactive visualization
- ✅ Full API access
- ✅ Neo4j graph database
- ✅ Automated backups
- ✅ Production-ready configuration