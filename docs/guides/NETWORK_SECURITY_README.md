# Network Compromise Detection Scripts

Comprehensive PowerShell scripts to detect signs of network compromise, malware, and security vulnerabilities on Windows systems.

## 🚨 **CRITICAL: Before Running**

**These scripts require Administrator privileges to function properly.**

### Running the Scripts

1. **Open PowerShell as Administrator:**
   - Right-click Start button
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"
   - If prompted by UAC, click "Yes"

2. **Set Execution Policy (if needed):**
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
   ```

3. **Run the Scripts:**
   ```powershell
   # Quick security check (2-3 minutes)
   .\quick_network_security_check.ps1
   
   # Comprehensive analysis (5-10 minutes)
   .\network_compromise_detection.ps1
   ```

## 📋 Script Overview

### 1. `quick_network_security_check.ps1`
**Purpose:** Fast security scan for immediate threat detection
**Duration:** 2-3 minutes
**Best for:** Quick daily checks or when time is limited

**Checks performed:**
- Suspicious processes running from temp folders
- Network connections to suspicious ports
- Firewall status
- Cryptocurrency mining detection
- DNS configuration issues

### 2. `network_compromise_detection.ps1`
**Purpose:** Comprehensive security analysis
**Duration:** 5-10 minutes
**Best for:** Thorough security audits or when compromise is suspected

**Checks performed:**
- All quick check items PLUS:
- Detailed network connection analysis
- Malicious process detection
- DNS security analysis
- Persistence mechanism detection
- Firewall rule analysis
- System integrity checks
- Data exfiltration detection
- Complete report generation

## 🔍 What the Scripts Detect

### Critical Threats (🔴 Red)
- **Cryptocurrency Miners:** Unauthorized mining software
- **Malware Processes:** Known malicious executables
- **Suspicious Network Connections:** Connections to known bad IPs/ports
- **Firewall Disabled:** Security system turned off
- **DNS Hijacking:** Modified DNS settings

### Security Warnings (🟡 Yellow)
- **Unusual Network Activity:** High data transfer
- **Suspicious Startup Items:** Programs set to run at boot
- **Old Scheduled Tasks:** Forgotten automated tasks
- **Modified System Files:** Changed critical system files

### Informational (🔵 Blue)
- **Public DNS Usage:** Using external DNS servers
- **Cloud Service Connections:** Legitimate but tracked connections
- **System Configuration:** Normal but documented settings

## 📊 Understanding Results

### Quick Check Results
```
⚡ Quick Network Security Check
===============================
🔍 Checking processes...
  ✅ No suspicious processes found
🔍 Checking network connections...
  ❌ Suspicious port connection: 192.168.1.100:4444
🔍 Checking firewall...
  ✅ Firewall enabled on all profiles
🔍 Checking for mining...
  ✅ No mining processes detected
🔍 Checking DNS...
  ✅ DNS configuration looks normal

📊 Quick Summary:
  ❌ 1 security issues found:
     [CRITICAL] Connection to suspicious port: 4444
```

### Comprehensive Report
The full analysis generates a detailed report saved to your Desktop with:
- Executive summary
- Detailed findings with timestamps
- Evidence for each detection
- Security recommendations
- Action items based on severity

## 🛡️ Security Best Practices

### After Running the Scripts

1. **If Critical Issues Found:**
   - **ISOLATE** the system from network immediately
   - **RUN** a full antivirus scan with updated definitions
   - **CHANGE** all passwords, especially admin accounts
   - **CONTACT** your IT security team
   - **CONSIDER** system rebuild if compromise is severe

2. **If Warnings Found:**
   - **INVESTIGATE** each warning individually
   - **UPDATE** all security software
   - **MONITOR** system for unusual activity
   - **REVIEW** user access and permissions

3. **If No Issues Found:**
   - **CONTINUE** regular security monitoring
   - **SCHEDULE** regular scans (weekly recommended)
   - **KEEP** scripts updated
   - **MAINTAIN** good security practices

### Regular Security Routine

1. **Daily:** Run quick check during startup
2. **Weekly:** Run comprehensive analysis
3. **Monthly:** Review and update detection rules
4. **After** any security incident: Run full analysis

## 🔧 Customization

### Adding Custom Detection Rules

You can modify the scripts to detect specific threats:

```powershell
# Add to suspicious IP addresses
$maliciousIPs = @(
    "192.168.100.",    # Existing
    "YOUR_CUSTOM_IP"   # Add your own
)

# Add to suspicious process names
$maliciousProcesses = @(
    "existing.exe",
    "your_custom_process.exe"  # Add your own
)
```

### Adjusting Sensitivity

Modify detection thresholds in the scripts:
- Network connection timeouts
- File size limits for data exfiltration
- Process age limits for persistence detection

## 🚫 False Positives

Some legitimate software may trigger warnings:

- **Development tools** running from temp folders
- **VPN connections** to unusual ports
- **Cloud backup services** with high data usage
- **Legitimate remote access** tools

Always investigate the context before taking action.

## 📝 Troubleshooting

### Common Issues

1. **"Execution of scripts is disabled"**
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
   ```

2. **"Access denied" errors**
   - Ensure you're running as Administrator
   - Check antivirus isn't blocking the scripts

3. **"Module not found" errors**
   - Some modules may not be available on older Windows versions
   - Scripts include error handling for missing modules

### Performance Notes

- Scripts are designed to be lightweight
- Network analysis may take longer on busy systems
- Disk I/O is minimized to avoid system impact
- Memory usage is kept low for older systems

## 🔄 Updates and Maintenance

### Keeping Scripts Current

1. **Review detection rules** monthly
2. **Update malicious IP lists** regularly
3. **Add new threat signatures** as they emerge
4. **Test scripts** after Windows updates

### Contributing Improvements

If you find new detection methods or improve existing ones:
1. Test thoroughly in isolated environment
2. Document the changes
3. Share findings with security team

## 🆘 Emergency Response

### If Compromise is Detected

1. **IMMEDIATE ACTIONS:**
   - Disconnect from network
   - Document what you found
   - Do not power off (preserve evidence)

2. **SECURITY TEAM NOTIFICATION:**
   - Report time and nature of findings
   - Provide script output and reports
   - Follow organizational incident response procedures

3. **EVIDENCE PRESERVATION:**
   - Save all script reports
   - Take screenshots of critical findings
   - Document system state before changes

---

**⚠️ WARNING:** These scripts are for defensive security purposes only. Use them responsibly and in accordance with your organization's security policies.

**🔒 Remember:** Security is an ongoing process, not a one-time scan. Regular monitoring and updates are essential for maintaining system security.