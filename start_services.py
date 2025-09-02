#!/usr/bin/env python3
"""
Helper script to start all services for local development
"""
import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def start_service(service_name, command, cwd):
    """Start a service in a separate thread"""
    print(f"Starting {service_name}...")
    try:
        # Change to service directory
        os.chdir(cwd)
        
        # Start the service
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output
        for line in iter(process.stdout.readline, ''):
            print(f"[{service_name}] {line.strip()}")
        
        process.stdout.close()
        return_code = process.wait()
        
        if return_code != 0:
            print(f"ERROR: {service_name} exited with code {return_code}")
        
    except Exception as e:
        print(f"ERROR: Error starting {service_name}: {e}")

def check_dependencies():
    """Check if required dependencies are installed"""
    dependencies = {
        'flask': 'Flask',
        'fastapi': 'FastAPI', 
        'uvicorn': 'Uvicorn',
        'streamlit': 'Streamlit',
        'pandas': 'Pandas',
        'sklearn': 'Scikit-learn',
        'plotly': 'Plotly',
        'httpx': 'HTTPX'
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(name)
    
    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"   - {dep}")
        print("\nInstall with: pip install " + " ".join(dep.lower().replace('-', '_') for dep in missing))
        return False
    
    return True

def check_database():
    """Check if database exists, create if not"""
    db_path = Path("erp_demo.db")
    if not db_path.exists():
        print("Creating database...")
        try:
            subprocess.run([sys.executable, "create_db.py"], check=True)
            print("Database created successfully")
        except subprocess.CalledProcessError:
            print("Failed to create database")
            return False
    else:
        print("Database found")
    
    return True

def main():
    """Main function to start all services"""
    print("ERP Prediction System - Service Starter")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check database
    if not check_database():
        sys.exit(1)
    
    # Get current directory
    base_dir = Path.cwd()
    
    # Service configurations
    services = [
        {
            'name': 'ERP Service',
            'command': f'{sys.executable} app.py',
            'cwd': base_dir / 'erp-service',
            'url': 'http://localhost:3001'
        },
        {
            'name': 'Prediction Service', 
            'command': f'{sys.executable} app.py',
            'cwd': base_dir / 'prediction-service',
            'url': 'http://localhost:3002'
        },
        {
            'name': 'Frontend Dashboard',
            'command': f'{sys.executable} -m streamlit run app.py --server.port 3000',
            'cwd': base_dir / 'frontend',
            'url': 'http://localhost:3000'
        }
    ]
    
    # Start services in separate threads
    threads = []
    
    for service in services:
        if not service['cwd'].exists():
            print(f"ERROR: Service directory not found: {service['cwd']}")
            continue
            
        thread = threading.Thread(
            target=start_service,
            args=(service['name'], service['command'], service['cwd'])
        )
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(2)  # Stagger startup
    
    print("\n" + "=" * 50)
    print("All services started!")
    print("\nService URLs:")
    for service in services:
        print(f"   - {service['name']}: {service['url']}")
    
    print("\nAccess the dashboard at: http://localhost:3000")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        sys.exit(0)

if __name__ == "__main__":
    main()