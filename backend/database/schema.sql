-- ==========================================
-- RAKSHAKAI - DATABASE SCHEMA
-- PostgreSQL schema for scam call defense system
-- ==========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- USERS TABLE
-- ==========================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    name VARCHAR(255),
    device_id VARCHAR(255),
    device_type VARCHAR(20) CHECK (device_type IN ('android', 'ios')),
    push_token VARCHAR(500),
    
    -- Settings
    alert_sounds BOOLEAN DEFAULT true,
    vibration_alerts BOOLEAN DEFAULT true,
    push_notifications BOOLEAN DEFAULT true,
    auto_handoff_threshold DECIMAL(3,2) DEFAULT 0.85,
    enable_ai_baiting BOOLEAN DEFAULT true,
    ai_persona VARCHAR(50) DEFAULT 'confused_senior',
    privacy_level VARCHAR(20) DEFAULT 'standard' CHECK (privacy_level IN ('strict', 'standard', 'permissive')),
    enable_audio_encryption BOOLEAN DEFAULT true,
    auto_report_to_authorities BOOLEAN DEFAULT false,
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_premium BOOLEAN DEFAULT false,
    subscription_expiry TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_device ON users(device_id);

-- ==========================================
-- CALLS TABLE
-- ==========================================
CREATE TABLE calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- User reference
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    device_id VARCHAR(255),
    
    -- Call details
    phone_number VARCHAR(20) NOT NULL,
    direction VARCHAR(10) CHECK (direction IN ('incoming', 'outgoing')),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER DEFAULT 0,
    
    -- Status
    status VARCHAR(50) DEFAULT 'connected' CHECK (
        status IN ('incoming', 'connected', 'monitoring', 'threat_detected', 'ai_handoff', 'ended', 'reported')
    ),
    ended_reason VARCHAR(50),
    
    -- Threat analysis
    threat_level VARCHAR(20) DEFAULT 'safe' CHECK (threat_level IN ('safe', 'low', 'medium', 'high', 'critical')),
    max_threat_score DECIMAL(4,3) DEFAULT 0.000,
    was_scam BOOLEAN DEFAULT false,
    
    -- AI engagement
    ai_engaged BOOLEAN DEFAULT false,
    ai_persona VARCHAR(50),
    ai_engagement_duration_seconds INTEGER DEFAULT 0,
    
    -- Audio storage
    audio_file_path VARCHAR(500),
    audio_file_hash VARCHAR(64),
    audio_retention_until TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_calls_user ON calls(user_id);
CREATE INDEX idx_calls_phone ON calls(phone_number);
CREATE INDEX idx_calls_status ON calls(status);
CREATE INDEX idx_calls_threat ON calls(threat_level);
CREATE INDEX idx_calls_started ON calls(started_at);
CREATE INDEX idx_calls_scam ON calls(was_scam) WHERE was_scam = true;

-- ==========================================
-- TRANSCRIPTS TABLE
-- ==========================================
CREATE TABLE transcripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    
    -- Transcript entry
    sequence_number INTEGER NOT NULL,
    speaker VARCHAR(20) CHECK (speaker IN ('caller', 'user', 'ai_agent')),
    text TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Analysis
    threat_score DECIMAL(4,3),
    keywords_detected JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(call_id, sequence_number)
);

-- Indexes
CREATE INDEX idx_transcripts_call ON transcripts(call_id);
CREATE INDEX idx_transcripts_speaker ON transcripts(speaker);

-- ==========================================
-- EXTRACTED ENTITIES TABLE (Intelligence)
-- ==========================================
CREATE TABLE extracted_entities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    
    -- Entity details
    entity_type VARCHAR(50) NOT NULL CHECK (
        entity_type IN ('upi_id', 'bank_account', 'phone_number', 'email', 'aadhaar', 'pan', 'credit_card', 'otp', 'ifsc_code', 'name', 'location', 'amount')
    ),
    original_value TEXT NOT NULL,
    masked_value TEXT NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    context TEXT,
    position_in_transcript INTEGER,
    
    -- Verification
    verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(255),
    verified_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_entities_call ON extracted_entities(call_id);
CREATE INDEX idx_entities_type ON extracted_entities(entity_type);
CREATE INDEX idx_entities_value ON extracted_entities(masked_value);
CREATE INDEX idx_entities_confidence ON extracted_entities(confidence);

-- ==========================================
-- EVIDENCE PACKAGES TABLE
-- ==========================================
CREATE TABLE evidence_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_id VARCHAR(255) UNIQUE NOT NULL,
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    
    -- Package details
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'rakshak_system',
    
    -- Content flags
    includes_audio BOOLEAN DEFAULT true,
    includes_transcript BOOLEAN DEFAULT true,
    includes_intelligence BOOLEAN DEFAULT true,
    
    -- Integrity
    audio_file_hash VARCHAR(64),
    package_hash VARCHAR(64),
    signature_algorithm VARCHAR(20) DEFAULT 'SHA256',
    signature_hash VARCHAR(128),
    signed_at TIMESTAMP,
    signed_by VARCHAR(255),
    
    -- Chain of custody
    chain_of_custody JSONB DEFAULT '[]'::jsonb,
    
    -- Law enforcement
    case_id VARCHAR(50),
    reported_at TIMESTAMP,
    report_status VARCHAR(50) DEFAULT 'pending' CHECK (
        report_status IN ('pending', 'submitted', 'under_review', 'acknowledged', 'resolved', 'rejected')
    ),
    law_enforcement_notes TEXT
);

-- Indexes
CREATE INDEX idx_evidence_call ON evidence_packages(call_id);
CREATE INDEX idx_evidence_package ON evidence_packages(package_id);
CREATE INDEX idx_evidence_status ON evidence_packages(report_status);
CREATE INDEX idx_evidence_case ON evidence_packages(case_id);

-- ==========================================
-- SCAMMER PROFILES TABLE
-- ==========================================
CREATE TABLE scammer_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    profile_id VARCHAR(255) UNIQUE NOT NULL,
    
    -- Identifiers
    phone_numbers TEXT[] DEFAULT '{}',
    upi_ids TEXT[] DEFAULT '{}',
    bank_accounts TEXT[] DEFAULT '{}',
    emails TEXT[] DEFAULT '{}',
    
    -- Profile info
    known_aliases TEXT[] DEFAULT '{}',
    operating_locations TEXT[] DEFAULT '{}',
    scam_types TEXT[] DEFAULT '{}',
    
    -- Statistics
    first_seen_at TIMESTAMP,
    last_seen_at TIMESTAMP,
    call_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    reported_count INTEGER DEFAULT 0,
    
    -- Risk assessment
    risk_level VARCHAR(20) DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    risk_score DECIMAL(4,3) DEFAULT 0.000,
    
    -- Network analysis
    associated_profiles UUID[] DEFAULT '{}',
    network_id VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_scammer_phones ON scammer_profiles USING GIN(phone_numbers);
CREATE INDEX idx_scammer_upi ON scammer_profiles USING GIN(upi_ids);
CREATE INDEX idx_scammer_risk ON scammer_profiles(risk_level);
CREATE INDEX idx_scammer_active ON scammer_profiles(is_active) WHERE is_active = true;

-- ==========================================
-- CALL-SCAMMER LINK TABLE
-- ==========================================
CREATE TABLE call_scammer_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    call_id UUID REFERENCES calls(id) ON DELETE CASCADE,
    scammer_profile_id UUID REFERENCES scammer_profiles(id) ON DELETE CASCADE,
    confidence DECIMAL(3,2) NOT NULL,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    linked_by VARCHAR(255) DEFAULT 'system',
    
    UNIQUE(call_id, scammer_profile_id)
);

-- Indexes
CREATE INDEX idx_link_call ON call_scammer_links(call_id);
CREATE INDEX idx_link_scammer ON call_scammer_links(scammer_profile_id);

-- ==========================================
-- AUDIT LOG TABLE
-- ==========================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_description TEXT,
    
    -- Actor
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_type VARCHAR(20) DEFAULT 'user' CHECK (actor_type IN ('user', 'system', 'admin', 'api')),
    actor_ip VARCHAR(45),
    
    -- Target
    target_type VARCHAR(50),
    target_id UUID,
    
    -- Data
    old_values JSONB,
    new_values JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_event ON audit_logs(event_type);
CREATE INDEX idx_audit_target ON audit_logs(target_type, target_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at);

-- ==========================================
-- DASHBOARD STATS MATERIALIZED VIEW
-- ==========================================
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM calls) as total_calls_monitored,
    (SELECT COUNT(*) FROM calls WHERE threat_level IN ('high', 'critical')) as threats_detected,
    (SELECT COUNT(*) FROM calls WHERE was_scam = true) as scams_confirmed,
    (SELECT COUNT(*) FROM calls WHERE ai_engaged = true) as ai_engagements,
    (SELECT COUNT(*) FROM evidence_packages) as evidence_packages_created,
    (SELECT COUNT(*) FROM extracted_entities) as entities_extracted,
    (SELECT COUNT(*) FROM scammer_profiles) as unique_scammers_identified,
    (SELECT AVG(max_threat_score) FROM calls WHERE max_threat_score > 0) as avg_threat_score,
    CURRENT_TIMESTAMP as refreshed_at;

-- Index on materialized view
CREATE INDEX idx_dashboard_refresh ON dashboard_stats(refreshed_at);

-- ==========================================
-- FUNCTIONS AND TRIGGERS
-- ==========================================

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update trigger to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_calls_updated_at BEFORE UPDATE ON calls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scammer_profiles_updated_at BEFORE UPDATE ON scammer_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Refresh dashboard stats function
CREATE OR REPLACE FUNCTION refresh_dashboard_stats()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW dashboard_stats;
END;
$$ LANGUAGE plpgsql;

-- Log audit event function
CREATE OR REPLACE FUNCTION log_audit_event(
    p_event_type VARCHAR,
    p_event_description TEXT,
    p_user_id UUID,
    p_actor_type VARCHAR,
    p_target_type VARCHAR,
    p_target_id UUID,
    p_old_values JSONB,
    p_new_values JSONB
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO audit_logs (
        event_type,
        event_description,
        user_id,
        actor_type,
        target_type,
        target_id,
        old_values,
        new_values
    ) VALUES (
        p_event_type,
        p_event_description,
        p_user_id,
        p_actor_type,
        p_target_type,
        p_target_id,
        p_old_values,
        p_new_values
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- ==========================================
-- INITIAL DATA
-- ==========================================

-- Insert default admin user (for development)
INSERT INTO users (phone_number, name, is_active)
VALUES ('+919999999999', 'Rakshak Admin', true)
ON CONFLICT (phone_number) DO NOTHING;

-- Insert sample scammer profile (for development)
INSERT INTO scammer_profiles (
    profile_id,
    phone_numbers,
    upi_ids,
    scam_types,
    first_seen_at,
    last_seen_at,
    risk_level,
    risk_score
) VALUES (
    'SCAM-001',
    ARRAY['+91 98765 43210', '+91 87654 32109'],
    ARRAY['scammer@paytm', 'fraud@okaxis'],
    ARRAY['kyc_fraud', 'bank_impersonation'],
    CURRENT_TIMESTAMP - INTERVAL '30 days',
    CURRENT_TIMESTAMP,
    'high',
    0.92
)
ON CONFLICT (profile_id) DO NOTHING;
