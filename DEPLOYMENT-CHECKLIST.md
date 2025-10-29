# DocTracer Deployment Checklist

This checklist ensures a smooth deployment of DocTracer to Digital Ocean.

## 📋 Pre-Deployment (Local Machine)

### ✅ Code Preparation
- [ ] All features working locally with `docker-compose -f docker-compose.prod.yml up -d`
- [ ] Both base and amendment gazettes loading correctly
- [ ] Frontend connecting to backend API (CORS configured)
- [ ] No TypeScript compilation errors
- [ ] All Docker containers building successfully

### ✅ Repository Setup
- [ ] Code pushed to GitHub repository
- [ ] `.env.production` template created
- [ ] `deploy-digitalocean.sh` script ready
- [ ] `README-DEPLOYMENT.md` documentation complete
- [ ] `.gitignore` updated for production files

## 🚀 Digital Ocean Deployment

### ✅ Server Setup
- [ ] Digital Ocean droplet created (minimum 2GB RAM, 2 vCPUs)
- [ ] Ubuntu 20.04 or 22.04 LTS installed
- [ ] SSH access configured
- [ ] Non-root user created (`doctracer`)

### ✅ One-Command Deployment
```bash
# Run this on your Digital Ocean droplet
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/doctracer/main/deploy-digitalocean.sh | bash
```

### ✅ Manual Configuration
- [ ] Edit `.env` file with production values:
  - [ ] `NEO4J_PASSWORD` - Set secure password
  - [ ] `API_URL` - Set to your domain/IP
  - [ ] `SECRET_KEY` - Generate secure random string
  - [ ] `JWT_SECRET_KEY` - Generate secure random string

### ✅ Service Verification
- [ ] All Docker containers running: `docker-compose -f docker-compose.prod.yml ps`
- [ ] Neo4j healthy and accessible
- [ ] Backend API responding: `curl http://localhost:5001/gazettes`
- [ ] Frontend serving: `curl http://localhost:80`

## 🔍 Data Verification

### ✅ Database Content
- [ ] **4 Base Gazettes** loaded: `1897/15`, `2153/12`, `2289/43`, `2412/08`
- [ ] **3 Amendment Gazettes** loaded: `1905/4`, `2159/15`, `2297/78`
- [ ] Dashboard shows correct counts: `curl http://localhost:5001/dashboard/summary`
- [ ] Amendment relationships working: `curl http://localhost:5001/amendments`

### ✅ API Endpoints
- [ ] `/gazettes` - Returns all gazettes
- [ ] `/dashboard/summary` - Shows gazette counts
- [ ] `/amendments` - Lists amendment gazettes
- [ ] `/gazettes/{id}/structure` - Returns gazette structure

## 🌐 Access Verification

### ✅ Public Access
- [ ] **Frontend**: `http://YOUR_DROPLET_IP:80` loads correctly
- [ ] **API**: `http://YOUR_DROPLET_IP:5001` responds
- [ ] **Neo4j Browser**: `http://YOUR_DROPLET_IP:7474` accessible
- [ ] Dashboard displays gazette data
- [ ] Interactive visualization works

### ✅ Functionality Test
- [ ] Can enter gazette ID (e.g., `1897/15`) and see visualization
- [ ] Ministers, departments, and laws display correctly
- [ ] Amendment tracking shows changes
- [ ] All navigation links working

## 🔒 Security & Performance

### ✅ Security
- [ ] Firewall configured (ports 22, 80, 443, 5001, 7474)
- [ ] Strong Neo4j password set
- [ ] Secure secret keys generated
- [ ] No sensitive data in logs

### ✅ Performance
- [ ] Frontend loads in < 5 seconds
- [ ] API responses in < 3 seconds
- [ ] Memory usage reasonable (`free -h`)
- [ ] Disk space sufficient (`df -h`)

## 🔄 Maintenance Setup

### ✅ Backup Strategy
- [ ] Backup script tested: `./backup.sh`
- [ ] Backup directory created: `./data/backups/`
- [ ] Scheduled backups configured (optional)

### ✅ Monitoring
- [ ] Docker logs accessible: `docker-compose -f docker-compose.prod.yml logs`
- [ ] System monitoring available: `htop`
- [ ] Health check endpoints working

## 🎉 Final Sign-off

### ✅ Complete Deployment
- [ ] **Frontend**: ✅ Working at `http://YOUR_IP:80`
- [ ] **Backend**: ✅ API responding at `http://YOUR_IP:5001`
- [ ] **Database**: ✅ Neo4j accessible at `http://YOUR_IP:7474`
- [ ] **Data**: ✅ 7 gazettes loaded (4 base + 3 amendments)
- [ ] **Visualization**: ✅ Interactive graphs working
- [ ] **Documentation**: ✅ README-DEPLOYMENT.md complete

### ✅ Success Criteria Met
- [ ] All services running and healthy
- [ ] Complete dataset loaded and accessible
- [ ] Frontend-backend communication working
- [ ] Public access confirmed
- [ ] Basic security measures in place

---

## 📞 Quick Commands for Management

```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Update application
git pull && docker-compose -f docker-compose.prod.yml up -d --build

# Create backup
./backup.sh
```

---

**✅ Deployment Complete!**
- **Date**: ___________
- **Deployed By**: ___________
- **Server IP**: ___________
- **Status**: Production Ready 🚀