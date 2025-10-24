#!/usr/bin/env python3
"""
Dependency Verification Script
Checks if all required packages are installed and working
"""

import sys
from typing import List, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_import(package_name: str, import_name: str = None) -> Tuple[bool, str]:
    """
    Try to import a package and return success status with version
    
    Args:
        package_name: Name to display
        import_name: Actual import name (if different from package_name)
    
    Returns:
        Tuple of (success, version_or_error)
    """
    if import_name is None:
        import_name = package_name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        return True, version
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"

def main():
    """Run dependency verification"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  SMC Bot - Dependency Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Define all required packages
    # Format: (display_name, import_name)
    required_packages = [
        # Core Framework
        ("Streamlit", "streamlit"),
        ("Python-dotenv", "dotenv"),
        
        # MT5 Integration
        ("MetaTrader5", "MetaTrader5"),
        
        # Data Processing
        ("Pandas", "pandas"),
        ("NumPy", "numpy"),
        ("Pandas-TA", "pandas_ta"),
        
        # Technical Analysis
        ("TA-Lib", "talib"),
        
        # Machine Learning
        ("Scikit-learn", "sklearn"),
        ("XGBoost", "xgboost"),
        ("LightGBM", "lightgbm"),
        ("CatBoost", "catboost"),
        ("TensorFlow", "tensorflow"),
        ("Joblib", "joblib"),
        ("Imbalanced-learn", "imblearn"),
        ("Optuna", "optuna"),
        ("SHAP", "shap"),
        
        # Visualization
        ("Plotly", "plotly"),
        ("Matplotlib", "matplotlib"),
        ("Seaborn", "seaborn"),
        ("Kaleido", "kaleido"),
        
        # Database
        ("SQLAlchemy", "sqlalchemy"),
        ("Alembic", "alembic"),
        
        # Reporting
        ("ReportLab", "reportlab"),
        ("Jinja2", "jinja2"),
        ("PyPDF2", "PyPDF2"),
        
        # Monitoring & Logging (CRITICAL!)
        ("Loguru", "loguru"),
        ("Psutil", "psutil"),
        
        # Utilities
        ("Python-dateutil", "dateutil"),
        ("Pytz", "pytz"),
        ("Requests", "requests"),
        ("PyYAML", "yaml"),
    ]
    
    # Check each package
    results = []
    failed = []
    
    print(f"{BLUE}Checking packages...{RESET}\n")
    
    for display_name, import_name in required_packages:
        success, version = check_import(display_name, import_name)
        results.append((display_name, success, version))
        
        if success:
            print(f"  {GREEN}✓{RESET} {display_name:<25} {version}")
        else:
            print(f"  {RED}✗{RESET} {display_name:<25} NOT FOUND")
            failed.append((display_name, import_name, version))
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    total = len(results)
    passed = sum(1 for _, success, _ in results if success)
    failed_count = total - passed
    
    if failed_count == 0:
        print(f"{GREEN}✓ All {total} packages are installed!{RESET}")
        print(f"\n{GREEN}You're ready to run the bot!{RESET}")
        
        # Detect environment type and show appropriate command
        if 'venv' in sys.prefix.lower() or sys.prefix.endswith('venv'):
            print(f"\nTo start: {YELLOW}run_bot.bat{RESET} (Windows) or {YELLOW}./run_bot.sh{RESET} (Linux/Mac)")
        else:
            print(f"\nTo start: {YELLOW}run_bot.bat{RESET} or {YELLOW}conda smc.bat{RESET}")
    else:
        print(f"{YELLOW}⚠ {passed}/{total} packages installed{RESET}")
        print(f"{RED}✗ {failed_count} package(s) missing{RESET}\n")
        
        print(f"{YELLOW}Missing packages:{RESET}")
        for display_name, import_name, error in failed:
            print(f"  • {display_name} ({import_name})")
        
        print(f"\n{YELLOW}How to fix:{RESET}")
        
        # Detect environment and show appropriate fix
        if 'venv' in sys.prefix.lower() or sys.prefix.endswith('venv'):
            print(f"  {BLUE}Using Python venv:{RESET}")
            print(f"    pip install -r requirements.txt")
            print(f"  Or manually install missing packages:")
            print(f"    pip install <package_name>")
        elif 'conda' in sys.prefix.lower() or 'anaconda' in sys.prefix.lower():
            print(f"  {BLUE}Using Conda:{RESET}")
            print(f"    conda env update -f environment.yml")
            print(f"  Or manually install missing packages:")
            print(f"    conda install -c conda-forge <package_name>")
        else:
            print(f"  {BLUE}No virtual environment detected!{RESET}")
            print(f"  Option 1 - Python venv (recommended):")
            print(f"    setup_venv.bat (Windows) or ./setup_venv.sh (Linux/Mac)")
            print(f"  Option 2 - Conda:")
            print(f"    conda env update -f environment.yml")
        
        # Special note for critical packages
        critical_missing = [name for name, imp, _ in failed if imp in ['loguru', 'streamlit', 'MetaTrader5']]
        if critical_missing:
            print(f"\n{RED}⚠ CRITICAL: The following essential packages are missing:{RESET}")
            for pkg in critical_missing:
                print(f"     • {pkg}")
    
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    # Check Python version
    print(f"{BLUE}Python Information:{RESET}")
    print(f"  Version: {sys.version.split()[0]}")
    print(f"  Path: {sys.executable}")
    
    # Check environment type
    if 'venv' in sys.prefix.lower() or sys.prefix.endswith('venv'):
        print(f"  {GREEN}✓ Running in Python venv{RESET}")
    elif 'conda' in sys.prefix.lower() or 'anaconda' in sys.prefix.lower():
        print(f"  {GREEN}✓ Running in Conda environment{RESET}")
    else:
        print(f"  {YELLOW}⚠ No virtual environment detected{RESET}")
        print(f"     Recommended: Run {BLUE}setup_venv.bat{RESET} or {BLUE}./setup_venv.sh{RESET}")
    
    print()
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = main()
    
    # Pause on Windows so user can see results
    if sys.platform == 'win32':
        input("\nPress Enter to exit...")
    
    sys.exit(exit_code)
