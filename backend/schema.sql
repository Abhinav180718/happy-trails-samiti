CREATE TABLE members (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    flat_number VARCHAR(50),
    mobile VARCHAR(30),
    email VARCHAR(255),
    role VARCHAR(30) NOT NULL DEFAULT 'member',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sponsorships (
    id BIGSERIAL PRIMARY KEY,
    sponsor_name VARCHAR(150) NOT NULL,
    flat_number VARCHAR(50),
    mobile VARCHAR(30),
    category VARCHAR(100),
    committed_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    received_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    remarks TEXT,
    created_by BIGINT REFERENCES members(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    transaction_ref VARCHAR(40) UNIQUE NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('income','expense')),
    category VARCHAR(100) NOT NULL,
    name_or_vendor VARCHAR(150) NOT NULL,
    flat_number VARCHAR(50),
    amount NUMERIC(12,2) NOT NULL,
    payment_mode VARCHAR(50),
    utr VARCHAR(150),
    remarks TEXT,
    created_by BIGINT REFERENCES members(id),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payment_proofs (
    id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    uploaded_by BIGINT REFERENCES members(id),
    uploaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses (
    id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT UNIQUE NOT NULL REFERENCES transactions(id) ON DELETE CASCADE,
    vendor VARCHAR(150),
    invoice_number VARCHAR(100),
    invoice_file_path TEXT,
    remarks TEXT
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    member_id BIGINT REFERENCES members(id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_sponsorships_flat ON sponsorships(flat_number);
