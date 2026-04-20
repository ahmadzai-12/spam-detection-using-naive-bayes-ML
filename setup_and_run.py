"""
Setup and Run Instructions for Email Spam Detection System
"""

import os
import subprocess
import sys

def setup_project():
    """Setup the complete project"""
    
    print("="*60)
    print("EMAIL SPAM DETECTION SYSTEM - SETUP")
    print("="*60)
    
    # Create directories
    directories = ['data', 'models', 'templates', 'static']
    for dir_name in directories:
        os.makedirs(dir_name, exist_ok=True)
        print(f"✓ Created directory: {dir_name}")
    
    # Install requirements
    print("\nInstalling required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Run 'python model_training.py' to train the model")
    print("2. Run 'python gui_app.py' for desktop GUI")
    print("3. Run 'python web_app.py' for web application")
    print("4. Visit http://localhost:5000 in your browser")

if __name__ == "__main__":
    setup_project()