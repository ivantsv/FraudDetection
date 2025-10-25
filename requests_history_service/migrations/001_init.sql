CREATE TABLE IF NOT EXISTS transactions_history (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(255) NOT NULL,
    "timestamp" TIMESTAMP NOT NULL,
    sender_account VARCHAR(255) NOT NULL CHECK (char_length(sender_account) >= 5),
    receiver_account VARCHAR(255) NOT NULL CHECK (char_length(receiver_account) >= 5),
    amount DOUBLE PRECISION NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(100) NOT NULL,
    merchant_category VARCHAR(100) NOT NULL,
    location VARCHAR(255) NOT NULL,
    device_used VARCHAR(100) NOT NULL,
    payment_channel VARCHAR(100) NOT NULL,
    ip_address INET NOT NULL,
    device_hash VARCHAR(255) NOT NULL CHECK (char_length(device_hash) >= 8),
    correlation_id VARCHAR(255) NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_transactions_transaction_id
    ON transactions_history (transaction_id);

CREATE INDEX IF NOT EXISTS idx_transactions_sender
    ON transactions_history (sender_account);

CREATE INDEX IF NOT EXISTS idx_transactions_receiver
    ON transactions_history (receiver_account);

CREATE INDEX IF NOT EXISTS idx_transactions_correlation
    ON transactions_history (correlation_id);

CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
    ON transactions_history ("timestamp" DESC);