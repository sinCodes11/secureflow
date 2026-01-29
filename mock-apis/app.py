from flask import Flask, request, jsonify
import os
import json
import random
import uuid
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

# Configuration
API_KEYS = {
    'virustotal': os.getenv('VIRUSTOTAL_API_KEY', 'demo_virustotal_key_2026'),
    'abuseipdb': os.getenv('ABUSEIPDB_API_KEY', 'demo_abuseipdb_key_2026'),
    'shodan': os.getenv('SHODAN_API_KEY', 'demo_shodan_key_2026'),
    'vectorguard': os.getenv('VECTORGUARD_API_KEY', 'demo_vectorguard_key_2026')
}

WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'secureflow_webhook_secret_2026')

def verify_api_key(required_service):
    """Verify API key in request headers"""
    key_map = {
        'virustotal': 'x-apikey',
        'abuseipdb': 'Key',
        'shodan': 'X-API-Key',
        'vectorguard': 'Authorization'
    }
    
    header_name = key_map.get(required_service)
    if not header_name:
        return True  # No key required
    
    provided_key = request.headers.get(header_name)
    expected_key = API_KEYS.get(required_service)
    
    if expected_key and provided_key:
        return provided_key.endswith(expected_key.split('_')[-1])
    return True  # Allow demo mode

def generate_threat_data():
    """Generate realistic threat intelligence data"""
    return {
        'malicious': random.choice([True, False]),
        'suspicious': random.choice([True, False]),
        'confidence': round(random.uniform(0.3, 0.95), 2),
        'engines_detected': random.randint(0, 15),
        'last_seen': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
        'threat_types': random.sample(['trojan', 'malware', 'phishing', 'botnet', 'ransomware'], k=random.randint(1, 3))
    }

# VirusTotal Mock API
@app.route('/api/virustotal', methods=['POST'])
@app.route('/api/virustotal/url', methods=['POST'])
def virustotal_api():
    if not verify_api_key('virustotal'):
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    
    if 'resource' in data:  # File hash lookup
        return jsonify({
            'data': {
                'id': hashlib.sha256(data['resource'].encode()).hexdigest(),
                'type': 'file',
                'attributes': {
                    'sha256': data['resource'],
                    'positive': random.randint(0, 10),
                    'total': 70,
                    'scan_date': datetime.now().isoformat(),
                    'first_submission_date': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                    'last_submission_date': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                    'reputation': random.randint(-100, 100),
                    'threat_names': random.sample(['Trojan.Generic', 'W32.AutoRun', 'Malware.heur'], k=random.randint(0, 2))
                }
            }
        })
    
    elif 'url' in data:  # URL lookup
        threat = generate_threat_data()
        return jsonify({
            'data': {
                'id': hashlib.sha256(data['url'].encode()).hexdigest(),
                'type': 'url',
                'attributes': {
                    'url': data['url'],
                    'last_final_url': data['url'],
                    'positives': random.randint(0, 5),
                    'total': 88,
                    'scan_date': datetime.now().isoformat(),
                    'domain': data['url'].split('/')[2] if len(data['url'].split('/')) > 2 else 'unknown.com',
                    'categories': {'malicious': threat['malicious']}
                }
            }
        })
    
    return jsonify({'error': 'Invalid request'}), 400

# AbuseIPDB Mock API
@app.route('/api/abuseipdb', methods=['GET'])
def abuseipdb_api():
    if not verify_api_key('abuseipdb'):
        return jsonify({'error': 'Invalid API key'}), 401
    
    ip_address = request.args.get('ipAddress')
    if not ip_address:
        return jsonify({'error': 'IP address required'}), 400
    
    return jsonify({
        'data': {
            'ipAddress': ip_address,
            'isPublic': True,
            'ipVersion': 4,
            'isWhitelisted': False,
            'abuseConfidenceScore': random.randint(0, 100),
            'countryCode': random.choice(['US', 'CN', 'RU', 'BR', 'IN', 'DE']),
            'countryName': random.choice(['United States', 'China', 'Russia', 'Brazil', 'India', 'Germany']),
            'usageType': random.choice(['Data Center/Web Hosting/Transit', 'ISP/MOB', 'Commercial', 'Education']),
            'isp': random.choice(['Amazon AWS', 'Google Cloud', 'Digital Ocean', 'Verizon', 'Comcast']),
            'domain': random.choice(['aws.amazon.com', 'google.com', 'digitalocean.com', 'verizon.com']),
            'totalReports': random.randint(0, 50),
            'numDistinctUsers': random.randint(0, 10),
            'lastReportedAt': (datetime.now() - timedelta(hours=random.randint(1, 168))).isoformat() if random.random() > 0.5 else None
        }
    })

# Shodan Mock API
@app.route('/api/shodan', methods=['POST'])
def shodan_api():
    if not verify_api_key('shodan'):
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    ip_address = data.get('ip_address') or data.get('target')
    
    return jsonify({
        'ip': ip_address,
        'country_code': random.choice(['US', 'CN', 'RU', 'JP', 'DE']),
        'country_name': random.choice(['United States', 'China', 'Russia', 'Japan', 'Germany']),
        'city': random.choice(['New York', 'Beijing', 'Moscow', 'Tokyo', 'Berlin']),
        'org': random.choice(['Amazon AWS', 'Google Cloud', 'Microsoft Azure', 'Digital Ocean']),
        'isp': random.choice(['Amazon AWS', 'Google Cloud', 'Microsoft Azure', 'Digital Ocean']),
        'ports': random.sample([22, 80, 443, 3389, 5432, 3306, 8080], k=random.randint(2, 5)),
        'vulns': random.sample(['CVE-2021-44228', 'CVE-2021-34527', 'CVE-2020-1472'], k=random.randint(0, 2)),
        'hostnames': [f"host-{uuid.uuid4().hex[:8]}.example.com"],
        'last_update': (datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
        'asn': f"AS{random.randint(1000, 99999)} {random.choice(['Amazon AWS', 'Google Cloud', 'Microsoft Azure'])}"
    })

# VectorGuard Mock API
@app.route('/api/vectorguard', methods=['POST'])
def vectorguard_api():
    if not verify_api_key('vectorguard'):
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    query = data.get('query', '')
    
    return jsonify({
        'query': query,
        'results': [
            {
                'cve_id': f"CVE-202{random.randint(0, 9):01d}-{random.randint(1000, 9999)}",
                'description': f"Security vulnerability related to {query[:20]}...",
                'severity': random.choice(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']),
                'cvss_score': round(random.uniform(4.0, 9.9), 1),
                'published_date': (datetime.now() - timedelta(days=random.randint(1, 365))).isoformat(),
                'affected_products': random.sample(['Apache', 'nginx', 'OpenSSL', 'Linux Kernel'], k=random.randint(1, 3)),
                'mitigation': "Update to latest version",
                'references': [f"https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-202{random.randint(0, 9):01d}-{random.randint(1000, 9999)}"]
            }
        ],
        'total_results': random.randint(5, 50),
        'query_time': round(random.uniform(0.1, 0.8), 3)
    })

# Webhook receivers for LogMind and CloudSentry
@app.route('/webhooks/logmind', methods=['POST'])
@app.route('/webhooks/cloudsentry', methods=['POST'])
def webhook_receiver():
    # Verify webhook secret
    if request.headers.get('X-Webhook-Secret') != WEBHOOK_SECRET:
        return jsonify({'error': 'Invalid webhook secret'}), 401
    
    data = request.get_json()
    data['received_at'] = datetime.now().isoformat()
    data['webhook_id'] = str(uuid.uuid4())
    
    return jsonify({
        'status': 'received',
        'webhook_id': data['webhook_id'],
        'processed_at': datetime.now().isoformat()
    })

# Mock remediation APIs
@app.route('/api/oci/isolate', methods=['POST'])
@app.route('/api/firewall/block-ip', methods=['POST'])
@app.route('/api/auth/lock-account', methods=['POST'])
@app.route('/api/dlp/blocked-downloads', methods=['POST'])
@app.route('/api/forensics/preserve-evidence', methods=['POST'])
@app.route('/api/email/quarantine', methods=['POST'])
@app.route('/api/email/block-sender', methods=['POST'])
@app.route('/api/users/notify-targets', methods=['POST'])
@app.route('/api/auth/force-mfa', methods=['POST'])
@app.route('/api/auth/terminate-session', methods=['POST'])
def remediation_apis():
    data = request.get_json()
    action_id = str(uuid.uuid4())
    
    return jsonify({
        'status': 'success',
        'action_id': action_id,
        'action': data.get('action', 'unknown'),
        'executed_at': datetime.now().isoformat(),
        'estimated_completion': (datetime.now() + timedelta(seconds=random.randint(5, 30))).isoformat(),
        'confidence': random.uniform(0.85, 0.99)
    })

# Mock notification APIs
@app.route('/slack/alerts', methods=['POST'])
def slack_api():
    return jsonify({
        'ok': True,
        'channel': request.json.get('channel'),
        'ts': str(datetime.now().timestamp()),
        'message': {'text': 'Alert posted successfully'}
    })

@app.route('/api/notify/security-team', methods=['POST'])
@app.route('/api/users/notify-security-team', methods=['POST'])
@app.route('/api/user/send-verification-alert', methods=['POST'])
def notification_apis():
    data = request.get_json()
    return jsonify({
        'status': 'sent',
        'notification_id': str(uuid.uuid4()),
        'recipients': data.get('recipients', ['security-team@company.com']),
        'sent_at': datetime.now().isoformat()
    })

# Mock analysis APIs
@app.route('/api/network/traffic-analysis', methods=['POST'])
@app.route('/api/user/behavior-analysis', methods=['POST'])
@app.route('/api/email/sender-analysis', methods=['POST'])
@app.route('/api/email/content-analysis', methods=['POST'])
@app.route('/api/geo/location-analysis', methods=['POST'])
@app.route('/api/device/fingerprint-analysis', methods=['POST'])
@app.route('/api/user/behavior-pattern', methods=['POST'])
def analysis_apis():
    data = request.get_json()
    
    return jsonify({
        'analysis_id': str(uuid.uuid4()),
        'anomaly_score': round(random.uniform(0.1, 0.95), 2),
        'suspicious_indicators': random.randint(0, 10),
        'confidence': round(random.uniform(0.6, 0.98), 2),
        'analysis_time': datetime.now().isoformat(),
        'risk_level': random.choice(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
        'recommendations': random.sample([
            'Immediate investigation required',
            'Monitor for further activity',
            'Block source IP address',
            'Require additional authentication'
        ], k=random.randint(1, 3))
    })

# Mock compliance APIs
@app.route('/api/oci/storage/make-private', methods=['POST'])
@app.route('/api/oci/network/fix-security-list', methods=['POST'])
@app.route('/api/oci/iam/enable-mfa', methods=['POST'])
def oci_remediation_apis():
    data = request.get_json()
    
    return jsonify({
        'status': 'remediated',
        'resource_id': data.get('resource_id') or data.get('bucket_name') or data.get('security_list_id'),
        'action': data.get('action'),
        'executed_at': datetime.now().isoformat(),
        'compartment_id': data.get('compartment_id'),
        'region': data.get('region', 'us-ashburn-1'),
        'verification_status': 'passed'
    })

@app.route('/api/oci/compliance/scan-results', methods=['POST'])
def compliance_scan():
    data = request.get_json()
    
    return jsonify({
        'scan_id': str(uuid.uuid4()),
        'resource_id': data.get('resource_id'),
        'compliance_status': 'compliant',
        'scan_time': datetime.now().isoformat(),
        'findings': [],
        'risk_score': random.uniform(0.0, 0.2)  # Low risk after remediation
    })

@app.route('/api/security/awareness-update', methods=['POST'])
def awareness_update():
    data = request.get_json()
    
    return jsonify({
        'status': 'updated',
        'update_id': str(uuid.uuid4()),
        'campaign_type': data.get('threat_type'),
        'added_to_training': True,
        'distribution_list': 'all_employees',
        'updated_at': datetime.now().isoformat()
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'services': {
            'virustotal': 'operational',
            'abuseipdb': 'operational',
            'shodan': 'operational',
            'vectorguard': 'operational'
        }
    })

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    return jsonify({
        'title': 'SecureFlow Mock APIs',
        'version': '1.0.0',
        'description': 'Mock APIs for threat intelligence and remediation services',
        'endpoints': {
            'threat_intel': [
                'POST /api/virustotal - File hash and URL analysis',
                'GET /api/abuseipdb - IP reputation check',
                'POST /api/shodan - Host intelligence',
                'POST /api/vectorguard - Threat intelligence query'
            ],
            'remediation': [
                'POST /api/oci/isolate - Endpoint isolation',
                'POST /api/firewall/block-ip - IP blocking',
                'POST /api/auth/lock-account - Account lockout',
                'POST /api/email/quarantine - Email quarantine'
            ],
            'analysis': [
                'POST /api/network/traffic-analysis - Network traffic analysis',
                'POST /api/user/behavior-analysis - User behavior analysis',
                'POST /api/geo/location-analysis - Geolocation analysis'
            ]
        }
    })

if __name__ == '__main__':
    # Debug mode disabled for security - set DEBUG=true in environment for development
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=8000, debug=debug_mode)