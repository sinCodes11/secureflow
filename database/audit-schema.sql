-- SecureFlow Database Schema
-- Tables for audit logging, incident tracking, and metrics

-- Drop tables if they exist (for development)
DROP TABLE IF EXISTS incident_metrics CASCADE;
DROP TABLE IF EXISTS workflow_executions CASCADE;
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS incidents CASCADE;

-- Create incidents table
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(100) UNIQUE NOT NULL,
    workflow_name VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    status VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED')),
    source_system VARCHAR(50) NOT NULL, -- LogMind, CloudSentry, External
    source_ip INET,
    target_user VARCHAR(100),
    file_hash VARCHAR(256),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create audit_logs table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(100) NOT NULL,
    workflow VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' CHECK (status IN ('SUCCESS', 'FAILURE', 'PENDING')),
    details JSONB NOT NULL,
    execution_time_ms INTEGER,
    user_id VARCHAR(100), -- n8n user who triggered action
    api_endpoint VARCHAR(200),
    api_response_code INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

-- Create workflow_executions table for performance metrics
CREATE TABLE workflow_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workflow_name VARCHAR(100) NOT NULL,
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    trigger_type VARCHAR(50) NOT NULL, -- webhook, schedule, manual
    status VARCHAR(20) NOT NULL DEFAULT 'RUNNING' CHECK (status IN ('RUNNING', 'SUCCESS', 'ERROR', 'TIMEOUT')),
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    nodes_executed INTEGER DEFAULT 0,
    nodes_failed INTEGER DEFAULT 0,
    input_data JSONB,
    output_data JSONB,
    error_details JSONB,
    resource_usage JSONB
);

-- Create incident_metrics table for SLA tracking
CREATE TABLE incident_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(100) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- time_to_ack, time_to_respond, time_to_resolve
    metric_value_seconds INTEGER NOT NULL,
    sla_threshold_seconds INTEGER NOT NULL,
    sla_met BOOLEAN NOT NULL,
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

-- Create indexes for performance
CREATE INDEX idx_incidents_incident_id ON incidents(incident_id);
CREATE INDEX idx_incidents_workflow_name ON incidents(workflow_name);
CREATE INDEX idx_incidents_created_at ON incidents(created_at);
CREATE INDEX idx_incidents_severity ON incidents(severity);
CREATE INDEX idx_incidents_status ON incidents(status);

CREATE INDEX idx_audit_logs_incident_id ON audit_logs(incident_id);
CREATE INDEX idx_audit_logs_workflow ON audit_logs(workflow);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

CREATE INDEX idx_workflow_executions_workflow_name ON workflow_executions(workflow_name);
CREATE INDEX idx_workflow_executions_start_time ON workflow_executions(start_time);
CREATE INDEX idx_workflow_executions_status ON workflow_executions(status);

CREATE INDEX idx_incident_metrics_incident_id ON incident_metrics(incident_id);
CREATE INDEX idx_incident_metrics_metric_type ON incident_metrics(metric_type);

-- Create materialized view for incident statistics
CREATE MATERIALIZED VIEW incident_statistics AS
SELECT 
    workflow_name,
    severity,
    status,
    COUNT(*) as total_incidents,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_resolution_time_seconds,
    MIN(created_at) as earliest_incident,
    MAX(created_at) as latest_incident
FROM incidents 
GROUP BY workflow_name, severity, status;

-- Create materialized view for workflow performance
CREATE MATERIALIZED VIEW workflow_performance AS
SELECT 
    workflow_name,
    COUNT(*) as total_executions,
    COUNT(*) FILTER (WHERE status = 'SUCCESS') as successful_executions,
    COUNT(*) FILTER (WHERE status = 'ERROR') as failed_executions,
    ROUND(COUNT(*) FILTER (WHERE status = 'SUCCESS') * 100.0 / NULLIF(COUNT(*), 0), 2) as success_rate_percent,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MIN(execution_time_ms) as min_execution_time_ms,
    MAX(execution_time_ms) as max_execution_time_ms,
    AVG(nodes_executed) as avg_nodes_executed
FROM workflow_executions
WHERE start_time >= NOW() - INTERVAL '30 days'
GROUP BY workflow_name;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for incidents table
CREATE TRIGGER update_incidents_updated_at 
    BEFORE UPDATE ON incidents 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function to calculate SLA metrics
CREATE OR REPLACE FUNCTION calculate_sla_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Calculate time to acknowledge (creation to first audit log)
    IF NEW.status = 'IN_PROGRESS' AND OLD.status = 'OPEN' THEN
        INSERT INTO incident_metrics (incident_id, metric_type, metric_value_seconds, sla_threshold_seconds, sla_met)
        SELECT 
            NEW.incident_id,
            'time_to_ack',
            EXTRACT(EPOCH FROM (NOW() - NEW.created_at))::INTEGER,
            120, -- 2 minutes SLA
            EXTRACT(EPOCH FROM (NOW() - NEW.created_at)) <= 120;
    END IF;
    
    -- Calculate time to resolve (creation to resolved)
    IF NEW.status = 'RESOLVED' AND OLD.status != 'RESOLVED' THEN
        NEW.resolved_at = NOW();
        
        INSERT INTO incident_metrics (incident_id, metric_type, metric_value_seconds, sla_threshold_seconds, sla_met)
        SELECT 
            NEW.incident_id,
            'time_to_resolve',
            EXTRACT(EPOCH FROM (NEW.resolved_at - NEW.created_at))::INTEGER,
            3600, -- 1 hour SLA
            EXTRACT(EPOCH FROM (NEW.resolved_at - NEW.created_at)) <= 3600;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for SLA calculation
CREATE TRIGGER calculate_incident_sla_metrics
    BEFORE UPDATE ON incidents
    FOR EACH ROW
    EXECUTE FUNCTION calculate_sla_metrics();

-- Grant permissions to secureflow user
GRANT SELECT, INSERT, UPDATE, DELETE ON incidents TO secureflow;
GRANT SELECT, INSERT, UPDATE, DELETE ON audit_logs TO secureflow;
GRANT SELECT, INSERT, UPDATE, DELETE ON workflow_executions TO secureflow;
GRANT SELECT, INSERT, UPDATE, DELETE ON incident_metrics TO secureflow;

GRANT SELECT ON incident_statistics TO secureflow;
GRANT SELECT ON workflow_performance TO secureflow;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO secureflow;

-- Create refresh functions for materialized views
CREATE OR REPLACE FUNCTION refresh_statistics()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY incident_statistics;
    REFRESH MATERIALIZED VIEW CONCURRENTLY workflow_performance;
END;
$$ LANGUAGE plpgsql;

-- Grant permission to refresh views
GRANT EXECUTE ON FUNCTION refresh_statistics() TO secureflow;

-- Add sample data for demonstration (optional)
INSERT INTO incidents (incident_id, workflow_name, severity, source_system, metadata) VALUES
('INC-001', 'malware_detection', 'CRITICAL', 'LogMind', '{"file_hash": "a1b2c3d4", "source_ip": "192.168.1.100"}'),
('INC-002', 'brute_force_mitigation', 'HIGH', 'CloudSentry', '{"target_user": "admin", "failed_attempts": 12}'),
('INC-003', 'phishing_analysis', 'MEDIUM', 'External', '{"sender_email": "phisher@evil.com"}');

INSERT INTO audit_logs (incident_id, workflow, action, details, execution_time_ms) VALUES
('INC-001', 'malware_detection', 'endpoint_isolation', '{"endpoint_id": "srv-001", "reason": "Malware detected"}', 2500),
('INC-002', 'brute_force_mitigation', 'ip_blocking', '{"blocked_ip": "192.168.1.100", "duration": "24h"}', 1200),
('INC-003', 'phishing_analysis', 'email_quarantine', '{"quarantined_emails": 15, "sender_blocked": true}', 1800);

COMMIT;