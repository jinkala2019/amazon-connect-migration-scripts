#!/usr/bin/env python3
"""
Installation verification script for Amazon Connect Migration Scripts
Run this script to verify that all dependencies are installed correctly.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.7+")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    dependencies = ['boto3', 'botocore', 'psutil']
    all_good = True
    
    for dep in dependencies:
        try:
            module = importlib.import_module(dep)
            version = getattr(module, '__version__', 'unknown')
            print(f"✅ {dep} {version} - OK")
        except ImportError:
            print(f"❌ {dep} - NOT INSTALLED")
            all_good = False
    
    return all_good

def check_aws_cli():
    """Check if AWS CLI is available (optional)"""
    try:
        result = subprocess.run(['aws', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ AWS CLI - {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  AWS CLI - NOT INSTALLED (optional but recommended)")
    return False

def check_scripts():
    """Check if all migration scripts are present"""
    required_scripts = [
        'connect_user_export.py',
        'connect_user_import.py',
        'connect_queue_export.py', 
        'connect_queue_import.py',
        'connect_quick_connect_export.py',
        'connect_quick_connect_import.py',
        'connect_phone_number_mapper.py'
    ]
    
    all_present = True
    for script in required_scripts:
        if Path(script).exists():
            print(f"✅ {script} - Present")
        else:
            print(f"❌ {script} - MISSING")
            all_present = False
    
    return all_present

def check_documentation():
    """Check if key documentation files are present"""
    docs = [
        'README.md',
        'QUICK_CONNECT_MIGRATION_GUIDE.md',
        'QUEUE_MIGRATION_GUIDE.md',
        'SIMPLE_PHONE_MAPPING_GUIDE.md'
    ]
    
    all_present = True
    for doc in docs:
        if Path(doc).exists():
            print(f"✅ {doc} - Present")
        else:
            print(f"❌ {doc} - MISSING")
            all_present = False
    
    return all_present

def main():
    """Main verification function"""
    print("Amazon Connect Migration Scripts - Installation Verification")
    print("=" * 60)
    
    print("\n🐍 Checking Python Version:")
    python_ok = check_python_version()
    
    print("\n📦 Checking Dependencies:")
    deps_ok = check_dependencies()
    
    print("\n☁️  Checking AWS CLI:")
    aws_ok = check_aws_cli()
    
    print("\n📜 Checking Migration Scripts:")
    scripts_ok = check_scripts()
    
    print("\n📚 Checking Documentation:")
    docs_ok = check_documentation()
    
    print("\n" + "=" * 60)
    
    if python_ok and deps_ok and scripts_ok and docs_ok:
        print("🎉 Installation verification PASSED!")
        print("✅ All required components are present and working.")
        print("\n📋 Next Steps:")
        print("1. Configure AWS credentials: aws configure")
        print("2. Review README.md for usage instructions")
        print("3. Start with dry-run mode for testing")
        return True
    else:
        print("❌ Installation verification FAILED!")
        print("\n🔧 To fix issues:")
        if not python_ok:
            print("- Install Python 3.7 or higher")
        if not deps_ok:
            print("- Run: pip install -r requirements.txt")
        if not scripts_ok:
            print("- Ensure all script files are present")
        if not docs_ok:
            print("- Ensure all documentation files are present")
        if not aws_ok:
            print("- Install AWS CLI: pip install awscli (optional)")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)