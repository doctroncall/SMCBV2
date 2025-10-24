"""
MT5 Connection Manager
Handles secure connection to MetaTrader 5 with auto-reconnection and health monitoring
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
import time
from functools import wraps

# Lazy import of MetaTrader5 to prevent import errors on startup
# MT5 is only available on Windows and should only be imported when actually used
mt5 = None

def _ensure_mt5_imported():
    """Lazy import MetaTrader5 module"""
    global mt5
    if mt5 is None:
        try:
            import MetaTrader5 as _mt5
            mt5 = _mt5
        except ImportError as e:
            raise ImportError(
                "MetaTrader5 package is not installed or not available on this platform. "
                "Please install it using: pip install MetaTrader5\n"
                "Note: MetaTrader5 only works on Windows."
            ) from e
    return mt5

from config.settings import MT5Config


class MT5ConnectionError(Exception):
    """Custom exception for MT5 connection errors"""
    pass


class MT5Connection:
    """
    Manages MetaTrader 5 connection with auto-reconnection and health monitoring
    
    Features:
    - Secure credential management
    - Automatic reconnection on failure
    - Connection health monitoring
    - Rate limiting compliance
    - Comprehensive error handling
    """
    
    def __init__(
        self,
        login: Optional[int] = None,
        password: Optional[str] = None,
        server: Optional[str] = None,
        timeout: Optional[int] = None,
        path: Optional[str] = None,
        portable: bool = False
    ):
        """
        Initialize MT5 connection manager
        
        Args:
            login: MT5 account number (or use config)
            password: MT5 account password (or use config)
            server: MT5 broker server (or use config)
            timeout: Connection timeout in milliseconds
            path: Path to MT5 terminal (optional)
            portable: Use portable mode (optional)
        """
        self.login = login or MT5Config.LOGIN
        self.password = password or MT5Config.PASSWORD
        self.server = server or MT5Config.SERVER
        self.timeout = timeout or MT5Config.TIMEOUT
        self.path = path or MT5Config.PATH
        self.portable = portable or MT5Config.PORTABLE
        
        self._connected = False
        self._connection_attempts = 0
        self._max_attempts = 3
        self._last_connection_time = None
        self._last_error = None
        
        # Connection statistics
        self.stats = {
            "total_connections": 0,
            "failed_connections": 0,
            "reconnections": 0,
            "uptime_start": None,
            "last_ping": None
        }
    
    def _validate_credentials(self) -> bool:
        """Validate that all required credentials are provided"""
        missing = []
        if not self.login or self.login == 0:
            missing.append("LOGIN")
        if not self.password:
            missing.append("PASSWORD")
        if not self.server:
            missing.append("SERVER")
        
        if missing:
            self._last_error = f"Missing MT5 credentials: {', '.join(missing)}. Current values - Login: {self.login}, Server: {self.server}"
            return False
        return True
    
    def connect(self, retry: bool = True) -> bool:
        """
        Connect to MetaTrader 5
        
        Args:
            retry: Whether to retry on failure
            
        Returns:
            bool: True if connected successfully
            
        Raises:
            MT5ConnectionError: If connection fails after retries
        """
        # Ensure MT5 is imported
        _mt5 = _ensure_mt5_imported()
        
        # Validate credentials first
        if not self._validate_credentials():
            print(f"❌ Credential validation failed: {self._last_error}")
            raise MT5ConnectionError(self._last_error)
        
        for attempt in range(1, self._max_attempts + 1 if retry else 2):
            try:
                self._connection_attempts = attempt
                
                # Initialize MT5 WITH credentials
                if self.path:
                    if not _mt5.initialize(
                        path=self.path,
                        login=self.login,
                        password=self.password,
                        server=self.server,
                        timeout=self.timeout,
                        portable=self.portable
                    ):
                        raise MT5ConnectionError(f"MT5 initialization failed: {_mt5.last_error()}")
                else:
                    if not _mt5.initialize(
                        login=self.login,
                        password=self.password,
                        server=self.server,
                        timeout=self.timeout
                    ):
                        raise MT5ConnectionError(f"MT5 initialization failed: {_mt5.last_error()}")
                
                # Verify connection
                account_info = _mt5.account_info()
                if account_info is None:
                    raise MT5ConnectionError("Failed to retrieve account info")
                
                # Connection successful
                self._connected = True
                self._last_connection_time = datetime.now()
                self._last_error = None
                
                # Update statistics
                self.stats["total_connections"] += 1
                if attempt > 1:
                    self.stats["reconnections"] += 1
                if self.stats["uptime_start"] is None:
                    self.stats["uptime_start"] = datetime.now()
                
                return True
                
            except Exception as e:
                self._last_error = str(e)
                self._connected = False
                self.stats["failed_connections"] += 1
                
                if attempt < self._max_attempts and retry:
                    wait_time = attempt * 2  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                else:
                    raise MT5ConnectionError(
                        f"Failed to connect after {attempt} attempts. Last error: {self._last_error}"
                    )
        
        return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from MetaTrader 5
        
        Returns:
            bool: True if disconnected successfully
        """
        try:
            if mt5 is not None:
                mt5.shutdown()
            self._connected = False
            return True
        except Exception as e:
            self._last_error = f"Error during disconnect: {str(e)}"
            return False
    
    def reconnect(self) -> bool:
        """
        Reconnect to MetaTrader 5
        
        Returns:
            bool: True if reconnected successfully
        """
        self.disconnect()
        time.sleep(1)
        return self.connect(retry=True)
    
    def is_connected(self) -> bool:
        """
        Check if connected to MT5
        
        Returns:
            bool: Connection status
        """
        if not self._connected:
            return False
        
        if mt5 is None:
            return False
        
        try:
            # Verify connection is still alive
            account_info = mt5.account_info()
            if account_info is None:
                self._connected = False
                return False
            return True
        except Exception:
            self._connected = False
            return False
    
    def ping(self) -> Optional[int]:
        """
        Test connection latency
        
        Returns:
            Optional[int]: Ping time in milliseconds, None if failed
        """
        if not self.is_connected():
            return None
        
        if mt5 is None:
            return None
        
        try:
            start = time.time()
            mt5.symbol_info_tick("EURUSD")  # Quick test request
            end = time.time()
            
            ping_ms = int((end - start) * 1000)
            self.stats["last_ping"] = ping_ms
            return ping_ms
        except Exception:
            return None
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get account information
        
        Returns:
            Optional[Dict]: Account details or None if failed
        """
        if not self.is_connected():
            return None
        
        if mt5 is None:
            return None
        
        try:
            info = mt5.account_info()
            if info is None:
                return None
            
            return {
                "login": info.login,
                "server": info.server,
                "company": info.company,
                "balance": info.balance,
                "equity": info.equity,
                "margin": info.margin,
                "margin_free": info.margin_free,
                "margin_level": info.margin_level,
                "currency": info.currency,
                "leverage": info.leverage,
                "trade_mode": info.trade_mode,
                "name": info.name,
            }
        except Exception as e:
            self._last_error = f"Error getting account info: {str(e)}"
            return None
    
    def get_terminal_info(self) -> Optional[Dict[str, Any]]:
        """
        Get terminal information
        
        Returns:
            Optional[Dict]: Terminal details or None if failed
        """
        if not self.is_connected():
            return None
        
        if mt5 is None:
            return None
        
        try:
            info = mt5.terminal_info()
            if info is None:
                return None
            
            return {
                "connected": info.connected,
                "trade_allowed": info.trade_allowed,
                "tradeapi_disabled": info.tradeapi_disabled,
                "dlls_allowed": info.dlls_allowed,
                "maxbars": info.maxbars,
                "codepage": info.codepage,
                "build": info.build,
                "community_connection": info.community_connection,
                "community_balance": info.community_balance,
                "path": info.path,
                "data_path": info.data_path,
            }
        except Exception as e:
            self._last_error = f"Error getting terminal info: {str(e)}"
            return None
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get comprehensive connection status
        
        Returns:
            Dict: Connection status information
        """
        connected = self.is_connected()
        ping = self.ping() if connected else None
        
        uptime = None
        if self.stats["uptime_start"] and connected:
            uptime = datetime.now() - self.stats["uptime_start"]
        
        return {
            "connected": connected,
            "server": self.server,
            "login": str(self.login)[-4:].rjust(len(str(self.login)), '*'),  # Masked
            "last_connection": self._last_connection_time,
            "ping_ms": ping,
            "uptime": uptime,
            "total_connections": self.stats["total_connections"],
            "failed_connections": self.stats["failed_connections"],
            "reconnections": self.stats["reconnections"],
            "last_error": self._last_error,
            "connection_attempts": self._connection_attempts,
        }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check
        
        Returns:
            Dict: Health status with details
        """
        connected = self.is_connected()
        ping = self.ping() if connected else None
        account_info = self.get_account_info() if connected else None
        terminal_info = self.get_terminal_info() if connected else None
        
        # Determine health status
        if not connected:
            status = "critical"
            message = "Not connected to MT5"
        elif ping is None or ping > 1000:
            status = "warning"
            message = f"High latency: {ping}ms"
        elif terminal_info and not terminal_info.get("trade_allowed", False):
            status = "warning"
            message = "Trading not allowed on terminal"
        else:
            status = "healthy"
            message = "Connection healthy"
        
        return {
            "status": status,
            "message": message,
            "connected": connected,
            "ping_ms": ping,
            "account_info": account_info,
            "terminal_info": terminal_info,
            "statistics": self.stats,
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
    
    def __repr__(self) -> str:
        status = "Connected" if self.is_connected() else "Disconnected"
        return f"<MT5Connection server={self.server} status={status}>"


def ensure_connection(func):
    """
    Decorator to ensure MT5 connection before executing function
    Automatically reconnects if connection is lost
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # If no connection object is provided, assume global MT5 API is used
        if not hasattr(self, "connection") or self.connection is None:
            return func(self, *args, **kwargs)
        if not self.connection.is_connected():
            try:
                self.connection.reconnect()
            except MT5ConnectionError as e:
                raise MT5ConnectionError(f"Cannot execute {func.__name__}: {str(e)}")
        return func(self, *args, **kwargs)
    return wrapper


# Singleton pattern for global connection management
class MT5ConnectionManager:
    """Singleton manager for global MT5 connection"""
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MT5ConnectionManager, cls).__new__(cls)
        return cls._instance
    
    def get_connection(self) -> MT5Connection:
        """Get or create MT5 connection instance"""
        if self._connection is None:
            self._connection = MT5Connection()
        return self._connection
    
    def reset_connection(self):
        """Reset connection instance"""
        if self._connection:
            self._connection.disconnect()
        self._connection = None


# Convenience function
def get_mt5_connection() -> MT5Connection:
    """Get global MT5 connection instance"""
    manager = MT5ConnectionManager()
    return manager.get_connection()


if __name__ == "__main__":
    # Test connection
    print("🔌 Testing MT5 Connection...")
    
    try:
        conn = MT5Connection()
        conn.connect()
        
        print(f"✓ Connected: {conn.is_connected()}")
        print(f"✓ Ping: {conn.ping()}ms")
        
        account = conn.get_account_info()
        if account:
            print(f"✓ Account: {account['login']} | Balance: {account['balance']} {account['currency']}")
        
        status = conn.get_connection_status()
        print(f"✓ Status: {status}")
        
        health = conn.health_check()
        print(f"✓ Health: {health['status']} - {health['message']}")
        
        conn.disconnect()
        print("✓ Disconnected successfully")
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
