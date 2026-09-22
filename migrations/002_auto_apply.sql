-- 002_auto_apply.sql: Enhance applications table with method, response payload, and query indices

ALTER TABLE applications ADD COLUMN apply_method TEXT DEFAULT 'playwright_form';
ALTER TABLE applications ADD COLUMN response_payload TEXT DEFAULT '{}';

CREATE INDEX IF NOT EXISTS idx_applications_applied_at ON applications(applied_at);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_applications_auto_status ON applications(auto_apply_status);
