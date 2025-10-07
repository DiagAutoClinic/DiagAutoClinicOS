#!/bin/bash
# quick_connect.sh

echo "🔗 Quick connecting to OBD II device..."
sudo rfcomm release /dev/rfcomm0 2>/dev/null
sudo rfcomm bind /dev/rfcomm0 00:1D:A5:68:98:8B 1
echo "✅ Connection established!"