"""
Health Monitor
Continuous monitoring of system components and resources
"""
import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from config.settings import HealthConfig
from src.utils.logger import get_logger

logger = get_logger()


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class HealthMonitor:
    """
    Monitor system health across all components
    
    Monitors:
    - MT5 connection status
    - System resources (CPU, RAM, Disk)
    - Data pipeline health
    - ML model performance
    - Database connectivity
    - Application responsiveness
    """
    
    def __init__(self):
        """Initialize health monitor"""
        self.config = HealthConfig
        self.logger = logger
        
        # Health check results cache
        self._last_check = None
        self._check_history = []
        self._max_history = 100
        
        # Component health trackers
        self._component_health = {}
        
        # Alert thresholds
        self.cpu_warning = self.config.CPU_WARNING_THRESHOLD
        self.cpu_critical = self.config.CPU_CRITICAL_THRESHOLD
        self.memory_warning = self.config.MEMORY_WARNING_THRESHOLD
        self.memory_critical = self.config.MEMORY_CRITICAL_THRESHOLD
        self.disk_warning = self.config.DISK_WARNING_THRESHOLD
        self.disk_critical = self.config.DISK_CRITICAL_THRESHOLD
    
    def check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage
        
        Returns:
            Dict with resource metrics and status
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = self._assess_threshold(
                cpu_percent,
                self.cpu_warning,
                self.cpu_critical
            )
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_status = self._assess_threshold(
                memory_percent,
                self.memory_warning,
                self.memory_critical
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_status = self._assess_threshold(
                disk_percent,
                self.disk_warning,
                self.disk_critical
            )
            
            # Overall status
            statuses = [cpu_status, memory_status, disk_status]
            if HealthStatus.CRITICAL in statuses:
                overall_status = HealthStatus.CRITICAL
            elif HealthStatus.WARNING in statuses:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.HEALTHY
            
            return {
                'status': overall_status.value,
                'cpu': {
                    'percent': cpu_percent,
                    'status': cpu_status.value,
                    'cores': psutil.cpu_count(),
                },
                'memory': {
                    'percent': memory_percent,
                    'used_mb': memory.used / (1024 * 1024),
                    'total_mb': memory.total / (1024 * 1024),
                    'available_mb': memory.available / (1024 * 1024),
                    'status': memory_status.value,
                },
                'disk': {
                    'percent': disk_percent,
                    'used_gb': disk.used / (1024 ** 3),
                    'total_gb': disk.total / (1024 ** 3),
                    'free_gb': disk.free / (1024 ** 3),
                    'status': disk_status.value,
                },
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking system resources: {str(e)}", category="health")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e)
            }
    
    def check_mt5_connection(self, connector=None) -> Dict[str, Any]:
        """
        Check MT5 connection health
        
        Args:
            connector: MT5Connector instance from mt5_connector.py (optional)
            
        Returns:
            Dict with connection health
        """
        try:
            if connector is None:
                from src.mt5.connection import get_mt5_connection
                connector = get_mt5_connection()
            
            # Get connection status
            is_connected = connector.is_connected()
            
            if not is_connected:
                return {
                    'status': HealthStatus.CRITICAL.value,
                    'connected': False,
                    'message': 'MT5 not connected',
                    'timestamp': datetime.now()
                }
            
            # Test connection quality with MT5 API
            try:
                import MetaTrader5 as mt5
                start = time.time()
                account_info = mt5.account_info()
                ping_ms = (time.time() - start) * 1000
                
                if account_info:
                    # Assess ping
                    if ping_ms > 1000:
                        ping_status = HealthStatus.CRITICAL
                    elif ping_ms > 500:
                        ping_status = HealthStatus.WARNING
                    else:
                        ping_status = HealthStatus.HEALTHY
                    
                    return {
                        'status': ping_status.value,
                        'connected': True,
                        'ping_ms': round(ping_ms, 2),
                        'account': {
                            'login': account_info.login,
                            'server': connector.server,
                            'balance': account_info.balance,
                        },
                        'timestamp': datetime.now()
                    }
                else:
                    self.logger.warning("Health Check: MT5 Connection (WARNING): Connected but no account info", category="health")
                    return {
                        'status': HealthStatus.WARNING.value,
                        'connected': True,
                        'ping_ms': round(ping_ms, 2),
                        'message': 'Connected but account info unavailable',
                        'timestamp': datetime.now()
                    }
            except Exception as ping_err:
                self.logger.error(f"Health Check: MT5 ping test failed: {str(ping_err)}", category="health")
                return {
                    'status': HealthStatus.WARNING.value,
                    'connected': True,
                    'message': f'Connected but ping test failed: {str(ping_err)}',
                    'timestamp': datetime.now()
                }
            
        except Exception as e:
            self.logger.error(f"Error checking MT5 connection: {str(e)}", category="health")
            return {
                'status': HealthStatus.CRITICAL.value,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def check_data_pipeline(self, repository=None) -> Dict[str, Any]:
        """
        Check data pipeline health
        
        Args:
            repository: DatabaseRepository instance (optional)
            
        Returns:
            Dict with pipeline health
        """
        try:
            if repository is None:
                from src.database.repository import get_repository
                repository = get_repository()
            
            # Check database connectivity
            symbols = repository.get_all_symbols()
            
            # Check recent data
            if symbols:
                test_symbol = symbols[0]
                recent_data = repository.get_candles(
                    test_symbol.name,
                    "H1",
                    start_date=datetime.now() - timedelta(hours=24),
                    limit=24
                )
                
                data_freshness = len(recent_data) if recent_data is not None else 0
                
                # Assess data freshness
                if data_freshness >= 20:
                    status = HealthStatus.HEALTHY
                elif data_freshness >= 10:
                    status = HealthStatus.WARNING
                else:
                    status = HealthStatus.CRITICAL
            else:
                status = HealthStatus.WARNING
                data_freshness = 0
            
            return {
                'status': status.value,
                'database_connected': True,
                'symbols_count': len(symbols),
                'recent_data_bars': data_freshness,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking data pipeline: {str(e)}", category="health")
            return {
                'status': HealthStatus.CRITICAL.value,
                'database_connected': False,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def check_ml_model(self, repository=None) -> Dict[str, Any]:
        """
        Check ML model health
        
        Args:
            repository: DatabaseRepository instance (optional)
            
        Returns:
            Dict with model health
        """
        try:
            if repository is None:
                from src.database.repository import get_repository
                repository = get_repository()
            
            # Get active model
            active_model = repository.get_active_model()
            
            if not active_model:
                return {
                    'status': HealthStatus.WARNING.value,
                    'model_loaded': False,
                    'message': 'No active model',
                    'timestamp': datetime.now()
                }
            
            # Check model accuracy
            accuracy = active_model.test_accuracy or 0.0
            
            # Assess accuracy
            if accuracy >= 0.70:
                status = HealthStatus.HEALTHY
            elif accuracy >= self.config.ACCURACY_WARNING_THRESHOLD:
                status = HealthStatus.WARNING
            else:
                status = HealthStatus.CRITICAL
            
            # Check training freshness
            training_age = (datetime.now() - active_model.training_date).total_seconds() / 3600
            
            return {
                'status': status.value,
                'model_loaded': True,
                'version': active_model.version,
                'accuracy': accuracy,
                'training_age_hours': training_age,
                'training_samples': active_model.training_samples,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Error checking ML model: {str(e)}", category="health")
            return {
                'status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def perform_health_check(
        self,
        connector=None,
        repository=None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive health check
        
        Args:
            connector: MT5Connector instance from mt5_connector.py (optional)
            repository: DatabaseRepository instance (optional)
            
        Returns:
            Dict with complete health status
        """
        try:
            self.logger.info("Performing comprehensive health check", category="health")
            
            # Check all components
            system_health = self.check_system_resources()
            mt5_health = self.check_mt5_connection(connector)
            pipeline_health = self.check_data_pipeline(repository)
            model_health = self.check_ml_model(repository)
            
            # Determine overall health
            component_statuses = [
                system_health.get('status'),
                mt5_health.get('status'),
                pipeline_health.get('status'),
                model_health.get('status')
            ]
            
            if HealthStatus.CRITICAL.value in component_statuses:
                overall_status = HealthStatus.CRITICAL
            elif HealthStatus.WARNING.value in component_statuses:
                overall_status = HealthStatus.WARNING
            else:
                overall_status = HealthStatus.HEALTHY
            
            # Generate detailed summary with specific issues
            issues = []
            
            # System resource issues
            if system_health.get('status') != HealthStatus.HEALTHY.value:
                issue_details = []
                if system_health.get('cpu', {}).get('status') != HealthStatus.HEALTHY.value:
                    cpu_pct = system_health['cpu']['percent']
                    issue_details.append(f"CPU: {cpu_pct:.1f}%")
                if system_health.get('memory', {}).get('status') != HealthStatus.HEALTHY.value:
                    mem_pct = system_health['memory']['percent']
                    issue_details.append(f"Memory: {mem_pct:.1f}%")
                if system_health.get('disk', {}).get('status') != HealthStatus.HEALTHY.value:
                    disk_pct = system_health['disk']['percent']
                    issue_details.append(f"Disk: {disk_pct:.1f}%")
                if issue_details:
                    issues.append(f"System resources ({system_health.get('status')}): {', '.join(issue_details)}")
            
            # MT5 connection issues
            if mt5_health.get('status') != HealthStatus.HEALTHY.value:
                error_msg = mt5_health.get('message', mt5_health.get('error', 'Unknown error'))
                connected = mt5_health.get('connected', False)
                if not connected:
                    issues.append(f"MT5 Connection (CRITICAL): Not connected - {error_msg}")
                else:
                    ping = mt5_health.get('ping_ms', 'N/A')
                    issues.append(f"MT5 Connection ({mt5_health.get('status')}): High latency - {ping}ms")
            
            # Data pipeline issues  
            if pipeline_health.get('status') != HealthStatus.HEALTHY.value:
                error_msg = pipeline_health.get('error', '')
                bars = pipeline_health.get('recent_data_bars', 0)
                db_connected = pipeline_health.get('database_connected', False)
                if not db_connected:
                    issues.append(f"Data Pipeline (CRITICAL): Database not connected - {error_msg}")
                else:
                    issues.append(f"Data Pipeline ({pipeline_health.get('status')}): Low data freshness - {bars} bars in last 24h")
            
            # ML model issues
            if model_health.get('status') != HealthStatus.HEALTHY.value:
                model_loaded = model_health.get('model_loaded', False)
                if not model_loaded:
                    issues.append(f"ML Model (WARNING): No active model loaded")
                else:
                    accuracy = model_health.get('accuracy', 0) * 100
                    issues.append(f"ML Model ({model_health.get('status')}): Low accuracy - {accuracy:.1f}%")
            
            result = {
                'overall_status': overall_status.value,
                'components': {
                    'system': system_health,
                    'mt5': mt5_health,
                    'pipeline': pipeline_health,
                    'model': model_health
                },
                'issues': issues,
                'healthy_components': len([s for s in component_statuses if s == HealthStatus.HEALTHY.value]),
                'total_components': len(component_statuses),
                'timestamp': datetime.now()
            }
            
            # Cache result
            self._last_check = result
            self._check_history.append(result)
            if len(self._check_history) > self._max_history:
                self._check_history.pop(0)
            
            # Log detailed results
            if issues:
                issues_str = " | ".join(issues)
                self.logger.log_health_check(
                    "Overall System",
                    overall_status.value,
                    {'issue_count': len(issues), 'details': issues_str}
                )
                # Also log each issue separately for easier tracking
                for i, issue in enumerate(issues, 1):
                    self.logger.warning(f"Health Issue {i}/{len(issues)}: {issue}", category="health")
            else:
                self.logger.log_health_check(
                    "Overall System",
                    overall_status.value,
                    {'issue_count': 0, 'details': 'All systems healthy'}
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error performing health check: {str(e)}", category="health")
            return {
                'overall_status': HealthStatus.UNKNOWN.value,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _assess_threshold(
        self,
        value: float,
        warning_threshold: float,
        critical_threshold: float
    ) -> HealthStatus:
        """Assess value against thresholds"""
        if value >= critical_threshold:
            return HealthStatus.CRITICAL
        elif value >= warning_threshold:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health check history"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            check for check in self._check_history
            if check.get('timestamp', datetime.min) > cutoff
        ]
    
    def get_uptime_percentage(self, hours: int = 24) -> float:
        """Calculate uptime percentage"""
        history = self.get_health_history(hours)
        if not history:
            return 100.0
        
        healthy_checks = sum(
            1 for check in history
            if check.get('overall_status') in [HealthStatus.HEALTHY.value, HealthStatus.WARNING.value]
        )
        
        return (healthy_checks / len(history)) * 100.0 if history else 100.0


if __name__ == "__main__":
    # Test health monitor
    print("🏥 Testing Health Monitor...")
    
    monitor = HealthMonitor()
    
    # Test system resources
    print("\n📊 System Resources:")
    resources = monitor.check_system_resources()
    print(f"   Status: {resources['status']}")
    print(f"   CPU: {resources['cpu']['percent']:.1f}%")
    print(f"   Memory: {resources['memory']['percent']:.1f}%")
    print(f"   Disk: {resources['disk']['percent']:.1f}%")
    
    # Test comprehensive health check
    print("\n🏥 Comprehensive Health Check:")
    health = monitor.perform_health_check()
    print(f"   Overall Status: {health['overall_status']}")
    print(f"   Healthy Components: {health['healthy_components']}/{health['total_components']}")
    if health.get('issues'):
        print(f"   Issues:")
        for issue in health['issues']:
            print(f"      - {issue}")
    
    # Test uptime
    uptime = monitor.get_uptime_percentage(1)
    print(f"\n📈 Uptime: {uptime:.1f}%")
    
    print("\n✓ Health monitor test completed")
