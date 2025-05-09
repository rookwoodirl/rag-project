-- Create tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    ticket_category VARCHAR(50) NOT NULL,
    ticket_number VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    valid_to TIMESTAMP WITH TIME ZONE NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create index on ticket_number for faster lookups
CREATE INDEX IF NOT EXISTS idx_tickets_ticket_number ON tickets(ticket_number);

-- Create index on ticket category
CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(ticket_category);

-- Create index for active tickets
CREATE INDEX IF NOT EXISTS idx_tickets_active ON tickets(is_active);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at timestamp
CREATE TRIGGER update_tickets_updated_at
BEFORE UPDATE ON tickets
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Add a unique constraint for active ticket numbers (allowing multiple versions)
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_active_tickets 
ON tickets(ticket_number, ticket_category) 
WHERE is_active = TRUE;

-- Create a view for the current active tickets
CREATE OR REPLACE VIEW active_tickets AS
SELECT * FROM tickets
WHERE is_active = TRUE
AND (valid_to IS NULL OR valid_to > CURRENT_TIMESTAMP)
AND valid_from <= CURRENT_TIMESTAMP;

-- Create ticket_comments table
CREATE TABLE IF NOT EXISTS ticket_comments (
    id SERIAL PRIMARY KEY,
    ticket_category VARCHAR(50) NOT NULL,
    ticket_number VARCHAR(20) NOT NULL,
    author VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    links JSONB NULL,
    attached_documents JSONB NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for ticket_comments
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_number ON ticket_comments(ticket_number);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_category ON ticket_comments(ticket_category);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_author ON ticket_comments(author);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_timestamp ON ticket_comments(timestamp);

-- Create composite index for faster ticket comment lookups
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket ON ticket_comments(ticket_category, ticket_number);

-- Create trigger to update updated_at column for comments
CREATE TRIGGER update_ticket_comments_updated_at
BEFORE UPDATE ON ticket_comments
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column(); 