-- Initialize PostgreSQL database for SecureFlow
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create main secureflow user with proper permissions
-- Note: SUPERUSER removed for security - user only needs application-level permissions
GRANT CREATE ON SCHEMA public TO secureflow;