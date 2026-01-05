"""
Database module for stock data caching and configuration management.
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from contextlib import contextmanager


DB_PATH = 'fat_wallet.db'


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables."""
    with get_db() as conn:
        cursor = conn.cursor()

        # Stock data cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date)
            )
        ''')

        # Watchlist table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT UNIQUE NOT NULL,
                name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Configuration table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Signal history table (for tracking when signals were sent)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                price REAL,
                rpp_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insert default configuration
        default_config = [
            ('check_interval', '900'),
            ('rpp_buy_threshold', '10'),
            ('rpp_sell_threshold', '90'),
            ('admin_user_id', '1937651844')
        ]

        for key, value in default_config:
            cursor.execute('''
                INSERT OR IGNORE INTO config (key, value)
                VALUES (?, ?)
            ''', (key, value))

        # Insert default watchlist
        default_watchlist = [
            ('NVDA', 'Nvidia'),
            ('GOOGL', 'Google'),
            ('ASML', 'ASML'),
            ('AAPL', 'Apple'),
            ('AMZN', 'Amazon'),
            ('ADS.DE', 'Adidas'),
            ('V', 'Visa'),
            ('KO', 'Coca-Cola')
        ]

        for ticker, name in default_watchlist:
            cursor.execute('''
                INSERT OR IGNORE INTO watchlist (ticker, name)
                VALUES (?, ?)
            ''', (ticker, name))

        conn.commit()

    print("✓ Database initialized")


def get_config(key):
    """Get a configuration value."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM config WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result[0] if result else None


def set_config(key, value):
    """Set a configuration value."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, str(value)))
        conn.commit()


def get_watchlist():
    """Get all tickers in the watchlist."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT ticker, name FROM watchlist ORDER BY ticker')
        return cursor.fetchall()


def add_to_watchlist(ticker, name=None):
    """Add a ticker to the watchlist."""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO watchlist (ticker, name)
                VALUES (?, ?)
            ''', (ticker.upper(), name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def remove_from_watchlist(ticker):
    """Remove a ticker from the watchlist."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM watchlist WHERE ticker = ?', (ticker.upper(),))
        deleted = cursor.rowcount
        conn.commit()
        return deleted > 0


def save_stock_data(ticker, df):
    """Save stock data to the database."""
    with get_db() as conn:
        for idx, row in df.iterrows():
            date_str = idx.strftime('%Y-%m-%d')
            conn.execute('''
                INSERT OR REPLACE INTO stock_data
                (ticker, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                date_str,
                row['Open'],
                row['High'],
                row['Low'],
                row['Close'],
                row['Volume']
            ))
        conn.commit()


def get_cached_stock_data(ticker, days=180):
    """Get cached stock data for a ticker."""
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    with get_db() as conn:
        query = '''
            SELECT date, open, high, low, close, volume
            FROM stock_data
            WHERE ticker = ? AND date >= ?
            ORDER BY date
        '''
        df = pd.read_sql_query(query, conn, params=(ticker, cutoff_date))

        if df.empty:
            return None

        # Convert date to datetime and set as index
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Rename columns to match yfinance format
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

        return df


def get_last_cached_date(ticker):
    """Get the most recent date we have cached data for."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT MAX(date) FROM stock_data WHERE ticker = ?
        ''', (ticker,))
        result = cursor.fetchone()
        return result[0] if result[0] else None


def needs_update(ticker):
    """Check if cached data needs updating (older than 1 day)."""
    last_date = get_last_cached_date(ticker)

    if not last_date:
        return True

    last_date_obj = datetime.strptime(last_date, '%Y-%m-%d')
    today = datetime.now()

    # Update if last cached date is not today and market might be open
    return (today - last_date_obj).days >= 1


def save_signal(ticker, signal_type, price, rpp_score):
    """Save a signal to history."""
    with get_db() as conn:
        conn.execute('''
            INSERT INTO signal_history (ticker, signal_type, price, rpp_score)
            VALUES (?, ?, ?, ?)
        ''', (ticker, signal_type, price, rpp_score))
        conn.commit()


def get_signal_history(ticker=None, days=30):
    """Get signal history."""
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    with get_db() as conn:
        if ticker:
            query = '''
                SELECT ticker, signal_type, price, rpp_score, created_at
                FROM signal_history
                WHERE ticker = ? AND created_at >= ?
                ORDER BY created_at DESC
            '''
            cursor = conn.execute(query, (ticker, cutoff_date))
        else:
            query = '''
                SELECT ticker, signal_type, price, rpp_score, created_at
                FROM signal_history
                WHERE created_at >= ?
                ORDER BY created_at DESC
            '''
            cursor = conn.execute(query, (cutoff_date,))

        return cursor.fetchall()
