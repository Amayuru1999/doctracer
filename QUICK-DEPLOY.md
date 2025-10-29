# 🚀 DocTracer - Quick Digital Ocean Deployment

## One-Command Deployment

### Step 1: Create Digital Ocean Droplet
- **Size**: 2GB RAM, 2 vCPUs (minimum)
- **OS**: Ubuntu 22.04 LTS
- **Region**: Choose closest to your users

### Step 2: SSH into Your Droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Create Non-Root User
```bash
adduser doctracer
usermod -aG sudo doctracer
su - doctracer
```

### Step 4: Deploy DocTracer
```bash
curl -fsSL https://raw.githubusercontent.com/Amayuru1999/doctracer/main/deploy-digitalocean.sh | bash
```

### Step 5: Configure Environment
The script will open `.env` file for editing. Update these values:
```bash
NEO4J_PASSWORD=your_secure_password_here
API_URL=http://YOUR_DROPLET_IP:5001
SECRET_KEY=your_very_secure_secret_key_here
JWT_SECRET_KEY=your_very_secure_jwt_secret_here
```

## 🎉 That's It!

Your DocTracer application will be running at:
- **Frontend**: http://YOUR_DROPLET_IP:80
- **API**: http://YOUR_DROPLET_IP:5001  
- **Neo4j**: http://YOUR_DROPLET_IP:7474

## 📊 What You Get

- ✅ **4 Base Gazettes** loaded automatically
- ✅ **3 Amendment Gazettes** loaded automatically  
- ✅ **Interactive visualization** with government structure
- ✅ **Complete API** for data access
- ✅ **Neo4j graph database** with relationships
- ✅ **Automated backups** configured
- ✅ **Production security** settings

## 🔧 Management Commands

```bash
# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs  
docker-compose -f docker-compose.prod.yml logs

# Restart
docker-compose -f docker-compose.prod.yml restart

# Update
git pull && docker-compose -f docker-compose.prod.yml up -d --build

# Backup
./backup.sh
```

## 🆘 Need Help?

Check the detailed guides:
- [README-DEPLOYMENT.md](README-DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT-CHECKLIST.md](DEPLOYMENT-CHECKLIST.md) - Step-by-step checklist

---

**Repository**: https://github.com/Amayuru1999/doctracer
**Deployment Time**: ~5 minutes
**Minimal Server Work**: Just run one command! 🎯