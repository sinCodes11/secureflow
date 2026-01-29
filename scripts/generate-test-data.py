#!/usr/bin/env python3
"""
SecureFlow Test Data Generator
Generates realistic test data for testing n8n workflows
"""

import json
import uuid
import random
import sys
import os
import hashlib
import string
from datetime import datetime, timedelta

class MockFaker:
    """Mock faker class for generating test data"""
    
    @staticmethod
    def sha256():
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    @staticmethod
    def ipv4():
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    
    @staticmethod
    def user_name():
        return f"user{random.randint(1000,9999)}"
    
    @staticmethod
    def email():
        usernames = ["admin", "user", "support", "test", "demo"]
        domains = ["example.com", "test.org", "demo.net", "company.io"]
        return f"{random.choice(usernames)}{random.randint(1,999)}@{random.choice(domains)}"
    
    @staticmethod
    def domain_name():
        domains = ["example.com", "test.org", "demo.net", "company.io", "suspicious-site.net"]
        return random.choice(domains)
    
    @staticmethod
    def url():
        domains = ["example.com", "test.org", "demo.net", "suspicious-site.net"]
        paths = ["", "/login", "/download", "/click", "/verify"]
        return f"http://{random.choice(domains)}{random.choice(paths)}"
    
    @staticmethod
    def sentence(nb_words=8):
        words = ["suspicious", "urgent", "verify", "account", "security", "alert", "notification", "update", "payment", "invoice"]
        selected = random.sample(words, min(nb_words, len(words)))
        return " ".join(selected).capitalize() + "."
    
    @staticmethod
    def country():
        countries = ["United States", "China", "Russia", "Brazil", "India", "Germany", "Japan", "Canada"]
        return random.choice(countries)
    
    @staticmethod
    def city():
        cities = ["New York", "Beijing", "Moscow", "São Paulo", "Mumbai", "Berlin", "Tokyo", "Toronto"]
        return random.choice(cities)
    
    @staticmethod
    def latitude():
        return round(random.uniform(-90, 90), 6)
    
    @staticmethod
    def longitude():
        return round(random.uniform(-180, 180), 6)
    
    @staticmethod
    def user_agent():
        agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        return random.choice(agents)

class TestDataGenerator:
    def __init__(self):
        self.workflow_types = [
            'malware_detection',
            'brute_force_mitigation',
            'data_exfiltration',
            'cloud_misconfiguration',
            'phishing_analysis',
            'suspicious_login'
        ]
        self.fake = MockFaker()
        
    def generate_malware_detection_data(self):
        """Generate test data for malware detection workflow"""
        return {
            "incident_id": f"MAL-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["critical", "high", "medium"]),
            "file_hash": self.fake.sha256(),
            "source_ip": self.fake.ipv4(),
            "instance_id": f"i-{uuid.uuid4().hex[:8]}",
            "detection_method": random.choice(["edr", "heuristic", "signature"]),
            "file_path": f"/var/tmp/malicious_{uuid.uuid4().hex[:6]}.exe",
            "file_size": random.randint(1024, 10485760),
            "user_id": self.fake.user_name(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_brute_force_data(self):
        """Generate test data for brute force mitigation workflow"""
        return {
            "incident_id": f"BF-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["high", "medium"]),
            "source_ip": self.fake.ipv4(),
            "target_user": self.fake.user_name(),
            "failed_attempts": random.randint(5, 50),
            "attack_duration": random.randint(1, 60),
            "attack_type": random.choice(["ssh", "rdp", "web", "ftp"]),
            "successful_login": random.choice([True, False]),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_data_exfiltration_data(self):
        """Generate test data for data exfiltration workflow"""
        return {
            "incident_id": f"EXF-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["critical", "high"]),
            "user_id": self.fake.user_name(),
            "source_ip": self.fake.ipv4(),
            "destination_ip": self.fake.ipv4(),
            "destination_country": self.fake.country(),
            "data_volume_gb": round(random.uniform(0.5, 50.0), 2),
            "protocol": random.choice(["http", "https", "ftp", "sftp", "custom"]),
            "file_types": random.sample(["pdf", "docx", "xlsx", "csv", "sql"], k=random.randint(1, 4)),
            "detection_method": random.choice(["network_monitoring", "dlp", "anomaly_detection"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_cloud_misconfiguration_data(self):
        """Generate test data for cloud misconfiguration workflow"""
        return {
            "incident_id": f"CLOUD-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["high", "medium", "low"]),
            "misconfiguration_type": random.choice([
                "public_storage_bucket",
                "overly_permissive_security_list", 
                "missing_mfa",
                "unencrypted_volume",
                "public_ip_assignment"
            ]),
            "resource_id": f"ocid1.{random.choice(['bucket', 'instance', 'securitylist'])}.oc1..{uuid.uuid4().hex}",
            "resource_type": random.choice(["storage", "compute", "network", "identity"]),
            "compartment_id": f"ocid1.compartment.oc1..{uuid.uuid4().hex}",
            "region": random.choice(["us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1"]),
            "compliance_standard": random.choice(["CIS", "NIST", "SOC2", "PCI-DSS"]),
            "discovery_method": random.choice(["automated_scan", "manual_review", "compliance_audit"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_phishing_analysis_data(self):
        """Generate test data for phishing analysis workflow"""
        return {
            "incident_id": f"PHISH-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["high", "medium", "low"]),
            "sender_email": self.fake.email(),
            "sender_domain": self.fake.domain_name(),
            "subject": self.fake.sentence(),
            "email_id": f"msg-{uuid.uuid4().hex[:16]}",
            "suspicious_url": self.fake.url(),
            "recipients": [self.fake.email() for _ in range(random.randint(1, 10))],
            "attachment_count": random.randint(0, 3),
            "malicious_links": random.randint(0, 5),
            "confidence_score": round(random.uniform(0.3, 0.95), 2),
            "detection_engine": random.choice(["rule_based", "ml_model", "reputation_analysis"]),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_suspicious_login_data(self):
        """Generate test data for suspicious login investigation workflow"""
        return {
            "incident_id": f"LOGIN-{uuid.uuid4().hex[:8].upper()}",
            "severity": random.choice(["high", "medium", "low"]),
            "user_id": self.fake.user_name(),
            "source_ip": self.fake.ipv4(),
            "session_id": f"sess-{uuid.uuid4().hex[:16]}",
            "risk_score": round(random.uniform(0.2, 0.95), 2),
            "auth_method": random.choice(["password", "mfa", "sso", "api_key"]),
            "user_agent": self.fake.user_agent(),
            "device_fingerprint": self.fake.sha256()[:32],
            "location": {
                "country": self.fake.country(),
                "city": self.fake.city(),
                "latitude": self.fake.latitude(),
                "longitude": self.fake.longitude()
            },
            "login_time": datetime.now().isoformat(),
            "anomaly_indicators": random.sample([
                "new_country",
                "new_device", 
                "unusual_time",
                "multiple_failures",
                "rapid_succession"
            ], k=random.randint(1, 3))
        }
    
    def generate_all_workflow_data(self, count=1):
        """Generate test data for all workflow types"""
        test_data = {}
        
        for _ in range(count):
            test_data['malware_detection'] = self.generate_malware_detection_data()
            test_data['brute_force_mitigation'] = self.generate_brute_force_data()
            test_data['data_exfiltration'] = self.generate_data_exfiltration_data()
            test_data['cloud_misconfiguration'] = self.generate_cloud_misconfiguration_data()
            test_data['phishing_analysis'] = self.generate_phishing_analysis_data()
            test_data['suspicious_login'] = self.generate_suspicious_login_data()
        
        return test_data
    
    def save_to_files(self, output_dir="test-data"):
        """Save test data to individual JSON files"""
        os.makedirs(output_dir, exist_ok=True)
        
        workflows_data = self.generate_all_workflow_data(5)
        
        for workflow_name, data in workflows_data.items():
            filename = f"{output_dir}/{workflow_name}_test.json"
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Generated test data for {workflow_name}: {filename}")
    
    def generate_webhook_test_script(self):
        """Generate a shell script to test all webhook endpoints"""
        script_content = '''#!/bin/bash
# SecureFlow Webhook Test Script
# Tests all n8n workflow webhooks with generated test data

set -e

# Configuration
N8N_URL="http://localhost:5678"
TEST_DATA_DIR="test-data"
LOG_FILE="webhook-test-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Test webhook function
test_webhook() {
    local workflow_name=$1
    local webhook_path=$2
    local test_file="$TEST_DATA_DIR/${workflow_name}_test.json"
    
    if [ ! -f "$test_file" ]; then
        print_error "Test file not found: $test_file"
        return 1
    fi
    
    print_status "Testing $workflow_name webhook..."
    
    # Send POST request to n8n webhook
    response=$(curl -s -w "\\n%{http_code}" \\
        -X POST \\
        -H "Content-Type: application/json" \\
        -d @"$test_file" \\
        "$N8N_URL/webhook/$webhook_path")
    
    # Extract HTTP code and response body
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n -1)
    
    # Evaluate response
    if [ "$http_code" -eq 200 ]; then
        print_success "$workflow_name webhook responded successfully (HTTP $http_code)"
        echo "Response: $response_body" | tee -a "$LOG_FILE"
    else
        print_error "$workflow_name webhook failed (HTTP $http_code)"
        echo "Response: $response_body" | tee -a "$LOG_FILE"
        return 1
    fi
    
    echo "---" | tee -a "$LOG_FILE"
}

# Main execution
echo -e "${BLUE}=== SecureFlow Webhook Test Script ===${NC}"
echo "Log file: $LOG_FILE"
echo

# Check if n8n is running
if ! curl -s "$N8N_URL" > /dev/null; then
    print_error "n8n is not accessible at $N8N_URL"
    print_error "Please ensure n8n is running: docker-compose up -d n8n"
    exit 1
fi

# Test all webhooks
test_webhook "malware_detection" "malware-detection"
test_webhook "brute_force_mitigation" "brute-force"
test_webhook "data_exfiltration" "data-exfiltration"
test_webhook "cloud_misconfiguration" "cloud-misconfig"
test_webhook "phishing_analysis" "phishing-analysis"
test_webhook "suspicious_login" "suspicious-login"

print_success "All webhook tests completed!"
echo "Detailed log available at: $LOG_FILE"
'''
        
        with open('scripts/test-webhooks.sh', 'w') as f:
            f.write(script_content)
        
        os.chmod('scripts/test-webhooks.sh', 0o755)
        print("Generated webhook test script: scripts/test-webhooks.sh")

def main():
    if len(sys.argv) > 1:
        count = int(sys.argv[1])
    else:
        count = 5
    
    print(f"Generating {count} test data samples for each workflow...")
    
    generator = TestDataGenerator()
    
    # Generate test data files
    generator.save_to_files()
    
    # Generate webhook test script
    generator.generate_webhook_test_script()
    
    print("\nTest data generation completed!")
    print("Files generated:")
    print("- test-data/*.json: Individual test data files")
    print("- scripts/test-webhooks.sh: Webhook testing script")
    print("\nTo test workflows:")
    print("1. Start SecureFlow: ./scripts/setup.sh")
    print("2. Import workflows into n8n")
    print("3. Run webhook tests: ./scripts/test-webhooks.sh")

if __name__ == "__main__":
    main()