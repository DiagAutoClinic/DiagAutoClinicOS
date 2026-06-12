### Step 1: Clone the Repository

```bash
git clone https://github.com/DiagAutoClinic/DiagAutoClinicOS.git
cd DiagAutoClinicOS
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Validate Installation

```bash
python scripts/validate_install.py
```

### Step 5: Launch Application

```bash
python launcher.py
```

## ✅ Verification

If everything is installed correctly, you should see:
- ✓ Maximized launcher window
- ✓ Three application buttons (AutoDiag, AutoECU, AutoKey)
- ✓ System stats dashboard
- ✓ Activity log showing initialization messages

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'PyQt6'"

bash pip install PyQt6

### "Permission denied" on Linux serial ports
Then log out and back in


### Application buttons show "✗ Available"
Check that the application files exist:

bash ls -l AutoDiag/main.py ls -l AutoECU/main.py ls -l AutoKey/main.py



## 📚 Next Steps

1. **Connect Hardware**: Plug in your OBD-II adapter
2. **Scan Devices**: Click "Scan Hardware" button
3. **Launch AutoDiag**: Click the AutoDiag Pro button
4. **Run Diagnostics**: Follow the on-screen instructions

## 🆘 Support

- **Issues**: https://github.com/DiagAutoClinic/DiagAutoClinicOS/issues
- **Email**: dacos@diagautoclinic.co.za
- **Documentation**: See `docs/` directory

## 📖 Documentation

- [Testing Guide](docs/testing/TESTING_GUIDE.md)
- [Security Policy](SECURITY.md)
- [Contributing](COMMUNITY_DISCUSSIONS.md)






