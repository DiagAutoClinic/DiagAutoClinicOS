#!/bin/bash
# scripts/final_setup.sh

echo "🚗 DiagAutoClinicOS Final Setup"
echo "================================"

# Create virtual environments for each app
python3 -m venv AutoDiag/venv
python3 -m venv AutoECU/venv  
python3 -m venv AutoKey/venv

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Set executable permissions
chmod +x launcher.py
chmod +x scripts/*.sh
chmod +x shared/install_linux_deps.sh

# Create desktop entry (Linux)
if [ -d "/usr/share/applications" ]; then
    sudo tee /usr/share/applications/diagautoclinic.desktop > /dev/null << EOF
[Desktop Entry]
Name=DiagAutoClinicOS
Comment=Professional Vehicle Diagnostics
Exec=/usr/bin/python3 $(pwd)/launcher.py
Icon=$(pwd)/assets/icon.png
Terminal=false
Type=Application
Categories=Development;Automotive;
EOF
fi

echo "✅ Setup complete! Run './launcher.py' to start."