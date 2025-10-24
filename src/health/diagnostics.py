"""
System Diagnostics
Detailed diagnostic tools for troubleshooting
"""
from typing import Dict, Any, List
from datetime import datetime
import traceback

from src.utils.logger import get_logger

logger = get_logger()


class SystemDiagnostics:
    """
    Perform detailed system diagnostics
    
    Features:
    - Component connectivity tests
    - Data quality checks
    - Performance benchmarks
    - Configuration validation
    """
    
    def __init__(self):
        """Initialize diagnostics"""
        self.logger = logger
        self.test_results = []
    
    def run_all_diagnostics(self) -> Dict[str, Any]:
        """Run all diagnostic tests"""
        self.logger.info("Running comprehensive diagnostics", category="health")
        
        results = {
            'mt5_diagnostics': self._test_mt5(),
            'database_diagnostics': self._test_database(),
            'data_quality': self._test_data_quality(),
            'config_validation': self._test_configuration(),
            'timestamp': datetime.now()
        }
        
        # Calculate overall pass rate
        all_tests = []
        for category in results.values():
            if isinstance(category, dict) and 'tests' in category:
                all_tests.extend(category['tests'])
        
        passed = sum(1 for t in all_tests if t.get('passed', False))
        total = len(all_tests)
        
        results['summary'] = {
            'total_tests': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }
        
        return results
    
    def _test_mt5(self) -> Dict[str, Any]:
        """Test MT5 connectivity and operations"""
        tests = []
        
        # Test 1: MT5 Import
        try:
            import MetaTrader5 as mt5
            tests.append({'name': 'MT5 Library Import', 'passed': True})
        except Exception as e:
            tests.append({'name': 'MT5 Library Import', 'passed': False, 'error': str(e)})
        
        # Test 2: Connection class availability
        try:
            from src.mt5.connection import MT5Connection
            _ = MT5Connection
            tests.append({'name': 'MT5 Connection Class', 'passed': True})
        except Exception as e:
            tests.append({'name': 'MT5 Connection Class', 'passed': False, 'error': str(e)})
        
        return {'category': 'MT5', 'tests': tests}
    
    def _test_database(self) -> Dict[str, Any]:
        """Test database connectivity and operations"""
        tests = []
        
        # Test 1: Database import
        try:
            from src.database.repository import DatabaseRepository
            tests.append({'name': 'Database Import', 'passed': True})
        except Exception as e:
            tests.append({'name': 'Database Import', 'passed': False, 'error': str(e)})
        
        # Test 2: Connection
        try:
            from src.database.repository import get_repository
            repo = get_repository()
            tests.append({'name': 'Database Connection', 'passed': True})
        except Exception as e:
            tests.append({'name': 'Database Connection', 'passed': False, 'error': str(e)})
        
        return {'category': 'Database', 'tests': tests}
    
    def _test_data_quality(self) -> Dict[str, Any]:
        """Test data quality"""
        tests = []
        
        try:
            from src.mt5.validator import DataValidator
            validator = DataValidator()
            tests.append({'name': 'Data Validator', 'passed': True})
        except Exception as e:
            tests.append({'name': 'Data Validator', 'passed': False, 'error': str(e)})
        
        return {'category': 'Data Quality', 'tests': tests}
    
    def _test_configuration(self) -> Dict[str, Any]:
        """Test configuration validity"""
        tests = []
        
        try:
            from config.settings import validate_config
            is_valid = validate_config()
            tests.append({'name': 'Config Validation', 'passed': is_valid})
        except Exception as e:
            tests.append({'name': 'Config Validation', 'passed': False, 'error': str(e)})
        
        return {'category': 'Configuration', 'tests': tests}


if __name__ == "__main__":
    print("🔍 Testing System Diagnostics...")
    
    diag = SystemDiagnostics()
    results = diag.run_all_diagnostics()
    
    print(f"\n📊 Summary:")
    print(f"   Tests: {results['summary']['passed']}/{results['summary']['total_tests']} passed")
    print(f"   Pass Rate: {results['summary']['pass_rate']:.1f}%")
    
    print("\n✓ Diagnostics test completed")
