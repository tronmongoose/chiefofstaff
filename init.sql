-- Create the plans table
CREATE TABLE IF NOT EXISTS plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_wallet VARCHAR(42) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    budget INTEGER NOT NULL,
    plan_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'generated' CHECK (status IN ('generated', 'confirmed', 'cancelled')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_plans_user_wallet ON plans(user_wallet);
CREATE INDEX IF NOT EXISTS idx_plans_created_at ON plans(created_at);
CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(status);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_plans_updated_at 
    BEFORE UPDATE ON plans 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
INSERT INTO plans (user_wallet, destination, budget, plan_data, status) VALUES
('0x1234567890123456789012345678901234567890', 'Paris', 2000, '{"flights": [{"from_location": "JFK", "to_location": "Paris", "airline": "DemoAir", "dates": "2024-08-01 to 2024-08-10", "price": 500.0}], "hotels": [{"name": "Hotel Demo", "location": "Paris", "price_per_night": 150.0, "nights": 7, "total": 1050.0}], "activities": ["Eiffel Tower visit", "Louvre Museum tour", "Seine River cruise"], "total_cost": 1750.0, "platform_fee": 35.0, "grand_total": 1785.0}', 'confirmed'),
('0x9876543210987654321098765432109876543210', 'Tokyo', 3000, '{"flights": [{"from_location": "LAX", "to_location": "Tokyo", "airline": "DemoAir", "dates": "2024-09-01 to 2024-09-10", "price": 800.0}], "hotels": [{"name": "Tokyo Hotel", "location": "Tokyo", "price_per_night": 200.0, "nights": 7, "total": 1400.0}], "activities": ["Senso-ji Temple", "Tokyo Skytree", "Shibuya Crossing"], "total_cost": 2400.0, "platform_fee": 48.0, "grand_total": 2448.0}', 'generated'); 