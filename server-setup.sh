#!/bin/bash

# Digital Ocean Server Setup Script for DocTracer
# Run this script on your fresh Ubuntu droplet

set -e

echo "🚀 Setting up Digital Ocean server for DocTracer"
echo "================================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Update system
print_status "Updating system packages..."
apt update && apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
apt install -y curl wget git htop ufw fail2ban

# Install Docker
print_status "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
print_status "Installing Docker Compose..."
DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
print_status "Creating application directory..."
mkdir -p /opt/doctracer
cd /opt/doctracer

# Create doctracer user
print_status "Creating doctracer user..."
if ! id "doctracer" &>/dev/null; then
    adduser --disabled-password --gecos "" doctracer
    usermod -aG docker doctracer
    usermod -aG sudo doctracer
fi

# Set up firewall
print_status "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 5000/tcp
ufw allow 7474/tcp
ufw --force enable

# Configure fail2ban
print_status "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl start fail2ban

# Set up log rotation for Docker
print_status "Configuring Docker log rotation..."
cat > /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker

# Create backup directory
print_status "Creating backup directory..."
mkdir -p /opt/doctracer/backups
chown -R doctracer:doctracer /opt/doctracer

# Set up system monitoring
print_status "Setting up system monitoring..."
cat > /opt/doctracer/monitor.sh << 'EOF'
#!/bin/bash
# Simple monitoring script
LOG_FILE="/var/log/doctracer-monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE - WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 90 ]; then
    echo "$DATE - WARNING: Memory usage is ${MEM_USAGE}%" >> $LOG_FILE
fi

# Check if Docker containers are running
if ! docker ps | grep -q doctracer; then
    echo "$DATE - ERROR: DocTracer containers not running" >> $LOG_FILE
fi
EOF

chmod +x /opt/doctracer/monitor.sh
chown doctracer:doctracer /opt/doctracer/monitor.sh

# Add monitoring to crontab
print_status "Setting up monitoring cron job..."
(crontab -u doctracer -l 2>/dev/null; echo "*/5 * * * * /opt/doctracer/monitor.sh") | crontab -u doctracer -

# Create swap file if not exists (for small droplets)
if [ ! -f /swapfile ]; then
    print_status "Creating swap file..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

# Optimize system for Docker
print_status "Optimizing system for Docker..."
echo 'vm.max_map_count=262144' >> /etc/sysctl.conf
sysctl -p

print_status "Server setup completed! 🎉"
echo ""
echo "Next steps:"
echo "1. Clone your DocTracer repository to /opt/doctracer"
echo "2. Create and configure your .env file"
echo "3. Run the deployment script"
echo ""
echo "Example commands:"
echo "  cd /opt/doctracer"
echo "  git clone https://github.com/yourusername/doctracer.git ."
echo "  cp .env.production .env"
echo "  nano .env  # Edit with your values"
echo "  ./deploy.sh"
echo ""
echo "System information:"
echo "  Docker version: $(docker --version)"
echo "  Docker Compose version: $(docker-compose --version)"
echo "  Available memory: $(free -h | awk 'NR==2{print $2}')"
echo "  Available disk: $(df -h / | awk 'NR==2{print $4}')"