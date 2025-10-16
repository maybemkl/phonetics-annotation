# AWS Deployment Guide

## Prerequisites

1. **Prodigy License**: You need a valid Prodigy license
2. **AWS Account**: With appropriate permissions for EC2, RDS, etc.
3. **SSH Key Pair**: For accessing your EC2 instance

## Instance Recommendations

### **Recommended: t4g.small**
- **2 vCPUs, 2 GiB RAM**
- **Cost**: ~$12/month
- **Perfect for**: Prodigy annotation work

### **Alternative: t4g.micro**
- **2 vCPUs, 1 GiB RAM** 
- **Cost**: ~$6/month
- **Good for**: Light annotation work

## Installation Steps

### 1. Launch EC2 Instance
```bash
# Use Ubuntu 22.04 LTS (ARM64 for t4g instances)
# Configure security group to allow:
# - SSH (port 22) from your IP
# - HTTP (port 80) from anywhere
# - Custom TCP (port 8080) from anywhere
```

### 2. Connect to Instance
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

### 3. Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git curl
```

### 4. Install Prodigy
```bash
# Download Prodigy installer from your account
# Follow the installation instructions from prodi.gy
# This will vary based on your license type
```

### 5. Install Python Dependencies
```bash
# Clone your repository
git clone <your-repo-url>
cd phonetics-annotation

# Install Python dependencies
pip3 install -r requirements.txt

# Install spaCy model
python3 -m spacy download en_core_web_sm
```

### 6. Set Up Data
```bash
# Upload your data files
# - patterns.jsonl
# - balanced_sample_*.jsonl
# - pattern_exceptions.txt
```

### 7. Configure Prodigy
```bash
# Use the AWS configuration
python3 run_prodigy.py prodigy_config_aws.yaml
```

## Security Considerations

### **Authentication (Recommended)**
Set up basic authentication:
```bash
export PRODIGY_BASIC_AUTH_USER="your_username"
export PRODIGY_BASIC_AUTH_PASS="your_password"
```

### **Session Management**
```bash
export PRODIGY_ALLOWED_SESSIONS="session1,session2,session3"
```

### **Database (Production)**
For production, use RDS PostgreSQL instead of SQLite:
```yaml
# In prodigy_config_aws.yaml
db: postgresql
db_settings:
  host: "your-rds-endpoint.amazonaws.com"
  port: 5432
  user: "prodigy_user"
  password: "your_password"
  database: "prodigy_db"
```

## Monitoring

### **CloudWatch Logs**
Set up CloudWatch for logging:
```bash
# Install CloudWatch agent
sudo apt install -y amazon-cloudwatch-agent
```

### **Health Checks**
Monitor Prodigy availability:
```bash
curl -f http://localhost:8080/health || echo "Prodigy down"
```

## Cost Optimization

- **Use Spot Instances** for development
- **Stop instances** when not in use
- **Use t4g.micro** for light workloads
- **Set up auto-shutdown** for non-production hours

## Troubleshooting

### **Port Issues**
```bash
# Check if port 8080 is open
sudo netstat -tlnp | grep 8080
```

### **Permission Issues**
```bash
# Fix file permissions
sudo chown -R ubuntu:ubuntu /home/ubuntu/phonetics-annotation
```

### **Memory Issues**
```bash
# Monitor memory usage
free -h
htop
```

## Backup Strategy

1. **Database backups** (if using RDS)
2. **Annotation data** (export from Prodigy)
3. **Configuration files** (version control)
4. **Pattern files** (version control)
