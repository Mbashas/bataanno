"""
Test Setup Script
Verify that all dependencies and data files are properly configured
Run this before launching the dashboard for the first time
"""

import sys
from pathlib import Path
import os

def print_header(text):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(item, status, message=""):
    """Print status with color coding"""
    symbols = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    symbol = symbols.get(status, 'ℹ️')
    print(f"{symbol} {item}: {message}")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status("Python Version", "success", 
                    f"{version.major}.{version.minor}.{version.micro} (Compatible)")
        return True
    else:
        print_status("Python Version", "error", 
                    f"{version.major}.{version.minor}.{version.micro} (Requires 3.8+)")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    print_header("Checking Dependencies")
    
    required_packages = {
        'streamlit': '1.28.0',
        'pandas': '2.0.0',
        'numpy': '1.24.0',
        'plotly': '5.17.0'
    }
    
    all_installed = True
    
    for package, min_version in required_packages.items():
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'Unknown')
            print_status(package, "success", f"v{version}")
        except ImportError:
            print_status(package, "error", f"Not installed (required: >={min_version})")
            all_installed = False
    
    return all_installed

def check_data_files():
    """Check if all required data files exist"""
    print_header("Checking Data Files")
    
    data_dir = Path(__file__).parent / "Data"
    
    if not data_dir.exists():
        print_status("Data Directory", "error", "Directory 'Data/' not found")
        return False
    
    required_files = [
        'production.csv',
        'w_service.csv',
        's_service.csv',
        'w_access.csv',
        's_access.csv',
        'all_fin_service.csv',
        'all_national.csv'
    ]
    
    all_present = True
    
    for filename in required_files:
        filepath = data_dir / filename
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print_status(filename, "success", f"{size_mb:.2f} MB")
        else:
            print_status(filename, "error", "File not found")
            all_present = False
    
    return all_present

def check_project_structure():
    """Check if project structure is correct"""
    print_header("Checking Project Structure")
    
    project_root = Path(__file__).parent
    
    required_dirs = [
        'utils',
        'page_modules',
        'Data'
    ]
    
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'utils/__init__.py',
        'utils/data_loader.py',
        'utils/kpi_calculator.py',
        'utils/visualizations.py',
        'page_modules/__init__.py',
        'page_modules/home.py',
        'page_modules/overview.py',
        'page_modules/production.py',
        'page_modules/service.py',
        'page_modules/access.py',
        'page_modules/finance.py',
        'page_modules/reports.py'
    ]
    
    all_present = True
    
    # Check directories
    for dirname in required_dirs:
        dirpath = project_root / dirname
        if dirpath.exists() and dirpath.is_dir():
            print_status(f"📁 {dirname}/", "success", "Directory exists")
        else:
            print_status(f"📁 {dirname}/", "error", "Directory not found")
            all_present = False
    
    # Check files
    for filename in required_files:
        filepath = project_root / filename
        if filepath.exists() and filepath.is_file():
            print_status(f"📄 {filename}", "success", "File exists")
        else:
            print_status(f"📄 {filename}", "error", "File not found")
            all_present = False
    
    return all_present

def test_data_loading():
    """Test if data can be loaded successfully"""
    print_header("Testing Data Loading")
    
    try:
        import pandas as pd
        data_dir = Path(__file__).parent / "Data"
        
        # Try loading one file
        test_file = data_dir / "production.csv"
        if test_file.exists():
            df = pd.read_csv(test_file, nrows=5)
            print_status("Sample Data Load", "success", 
                        f"Loaded {len(df)} rows × {len(df.columns)} columns")
            
            # Check for required columns
            required_cols = ['date_YYMMDD', 'source', 'production_m3', 'country']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                print_status("Column Validation", "warning", 
                           f"Missing columns: {', '.join(missing_cols)}")
                return False
            else:
                print_status("Column Validation", "success", "All required columns present")
                return True
        else:
            print_status("Sample Data Load", "error", "Test file not found")
            return False
            
    except Exception as e:
        print_status("Data Loading", "error", str(e))
        return False

def print_summary(results):
    """Print overall test summary"""
    print_header("Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    
    if failed_tests == 0:
        print("\n🎉 All tests passed! You're ready to run the dashboard.")
        print("\nTo start the dashboard, run:")
        print("    streamlit run app.py")
    else:
        print("\n⚠️ Some tests failed. Please address the issues above.")
        print("\nCommon fixes:")
        print("  - Install missing packages: pip install -r requirements.txt")
        print("  - Ensure all CSV files are in the Data/ directory")
        print("  - Check file names match exactly (case-sensitive)")
    
    print("\n" + "="*60 + "\n")

def main():
    """Run all tests"""
    print("\n" + "🌊 "*20)
    print("  WATER SERVICES DASHBOARD - SETUP TEST")
    print("🌊 "*20)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Project Structure': check_project_structure(),
        'Data Files': check_data_files(),
        'Data Loading': test_data_loading()
    }
    
    print_summary(results)
    
    # Return exit code
    sys.exit(0 if all(results.values()) else 1)

if __name__ == "__main__":
    main()

