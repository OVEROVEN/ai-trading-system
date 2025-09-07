-- Initialize TimescaleDB and create database for AI Trading System
-- This script sets up the database with time-series optimizations

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS trading_db;

-- Connect to the trading database
\c trading_db;

-- Create TimescaleDB extension for time-series data
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create additional useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUIDs
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- For query performance monitoring

-- Create hypertables for time-series data after tables are created
-- This will be run after SQLAlchemy creates the tables

-- Function to create hypertables (called after table creation)
CREATE OR REPLACE FUNCTION create_hypertables() RETURNS void AS $$
BEGIN
    -- Convert stock_prices to hypertable
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables 
        WHERE hypertable_name = 'stock_prices'
    ) THEN
        PERFORM create_hypertable('stock_prices', 'timestamp', 
                                chunk_time_interval => INTERVAL '1 day',
                                if_not_exists => TRUE);
    END IF;

    -- Convert technical_indicators to hypertable  
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables 
        WHERE hypertable_name = 'technical_indicators'
    ) THEN
        PERFORM create_hypertable('technical_indicators', 'timestamp',
                                chunk_time_interval => INTERVAL '1 day',
                                if_not_exists => TRUE);
    END IF;

    -- Convert trading_signals to hypertable
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables 
        WHERE hypertable_name = 'trading_signals'
    ) THEN
        PERFORM create_hypertable('trading_signals', 'timestamp',
                                chunk_time_interval => INTERVAL '1 day', 
                                if_not_exists => TRUE);
    END IF;

    -- Convert ai_analysis to hypertable
    IF NOT EXISTS (
        SELECT 1 FROM timescaledb_information.hypertables 
        WHERE hypertable_name = 'ai_analysis'
    ) THEN
        PERFORM create_hypertable('ai_analysis', 'timestamp',
                                chunk_time_interval => INTERVAL '1 day',
                                if_not_exists => TRUE);
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Create continuous aggregates for common queries
CREATE OR REPLACE FUNCTION create_continuous_aggregates() RETURNS void AS $$
BEGIN
    -- Daily OHLCV aggregates
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_ohlcv
    WITH (timescaledb.continuous) AS
    SELECT 
        symbol,
        time_bucket('1 day', timestamp) AS day,
        first(open, timestamp) AS open,
        max(high) AS high,
        min(low) AS low,
        last(close, timestamp) AS close,
        sum(volume) AS volume,
        count(*) AS tick_count
    FROM stock_prices
    GROUP BY symbol, day;

    -- Hourly indicator averages
    CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_indicators
    WITH (timescaledb.continuous) AS
    SELECT
        symbol,
        time_bucket('1 hour', timestamp) AS hour,
        avg(rsi) AS avg_rsi,
        avg(macd) AS avg_macd,
        avg(bb_upper) AS avg_bb_upper,
        avg(bb_lower) AS avg_bb_lower,
        count(*) AS sample_count
    FROM technical_indicators
    WHERE rsi IS NOT NULL
    GROUP BY symbol, hour;

    -- Daily signal summary
    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_signals
    WITH (timescaledb.continuous) AS
    SELECT
        symbol,
        time_bucket('1 day', timestamp) AS day,
        signal_type,
        count(*) AS signal_count,
        avg(strength) AS avg_strength,
        max(strength) AS max_strength
    FROM trading_signals
    GROUP BY symbol, day, signal_type;

END;
$$ LANGUAGE plpgsql;

-- Create data retention policies
CREATE OR REPLACE FUNCTION create_retention_policies() RETURNS void AS $$
BEGIN
    -- Keep stock prices for 2 years
    SELECT add_retention_policy('stock_prices', INTERVAL '2 years', if_not_exists => TRUE);
    
    -- Keep technical indicators for 1 year
    SELECT add_retention_policy('technical_indicators', INTERVAL '1 year', if_not_exists => TRUE);
    
    -- Keep trading signals for 6 months
    SELECT add_retention_policy('trading_signals', INTERVAL '6 months', if_not_exists => TRUE);
    
    -- Keep AI analysis for 1 year
    SELECT add_retention_policy('ai_analysis', INTERVAL '1 year', if_not_exists => TRUE);
END;
$$ LANGUAGE plpgsql;

-- Create compression policies for better storage efficiency
CREATE OR REPLACE FUNCTION create_compression_policies() RETURNS void AS $$
BEGIN
    -- Compress stock prices older than 7 days
    SELECT add_compression_policy('stock_prices', INTERVAL '7 days', if_not_exists => TRUE);
    
    -- Compress technical indicators older than 3 days
    SELECT add_compression_policy('technical_indicators', INTERVAL '3 days', if_not_exists => TRUE);
    
    -- Compress trading signals older than 1 day
    SELECT add_compression_policy('trading_signals', INTERVAL '1 day', if_not_exists => TRUE);
    
    -- Compress AI analysis older than 7 days
    SELECT add_compression_policy('ai_analysis', INTERVAL '7 days', if_not_exists => TRUE);
END;
$$ LANGUAGE plpgsql;

-- Create useful views for common queries
CREATE OR REPLACE VIEW latest_prices AS
SELECT DISTINCT ON (symbol) 
    symbol,
    timestamp,
    open,
    high, 
    low,
    close,
    volume,
    market
FROM stock_prices
ORDER BY symbol, timestamp DESC;

CREATE OR REPLACE VIEW latest_indicators AS
SELECT DISTINCT ON (symbol)
    symbol,
    timestamp,
    rsi,
    macd,
    macd_signal,
    bb_upper,
    bb_lower,
    sma_20,
    sma_50
FROM technical_indicators
ORDER BY symbol, timestamp DESC;

CREATE OR REPLACE VIEW active_signals AS
SELECT *
FROM trading_signals
WHERE timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_timestamp_desc 
ON stock_prices (symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_timestamp_desc
ON technical_indicators (symbol, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_trading_signals_symbol_type_timestamp
ON trading_signals (symbol, signal_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_ai_analysis_symbol_recommendation
ON ai_analysis (symbol, recommendation, timestamp DESC);

-- Performance monitoring views
CREATE OR REPLACE VIEW performance_stats AS
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public'
ORDER BY tablename, attname;

-- Grant permissions (adjust as needed)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO trading_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO trading_user;

-- Create a function to refresh all continuous aggregates
CREATE OR REPLACE FUNCTION refresh_continuous_aggregates() RETURNS void AS $$
BEGIN
    CALL refresh_continuous_aggregate('daily_ohlcv', NULL, NULL);
    CALL refresh_continuous_aggregate('hourly_indicators', NULL, NULL);
    CALL refresh_continuous_aggregate('daily_signals', NULL, NULL);
END;
$$ LANGUAGE plpgsql;

-- Setup complete message
DO $$
BEGIN
    RAISE NOTICE 'TimescaleDB database setup completed successfully!';
    RAISE NOTICE 'Remember to call create_hypertables() after creating tables';
    RAISE NOTICE 'Then call create_continuous_aggregates() and create_retention_policies()';
END
$$;