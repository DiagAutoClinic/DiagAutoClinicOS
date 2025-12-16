; AutoDiag_Setup.iss - Inno Setup Script for DiagAutoClinicOS v0.0.1
; AutoDiag Suite Alpha Release Installer
; For the DiagAutoClinicOS project: https://github.com/DiagAutoClinic/DiagAutoClinicOS/

#define MyAppName "DiagAutoClinicOS - AutoDiag"
#define MyAppVersion "0.0.1"
#define MyAppPublisher "DiagAutoClinic"
#define MyAppSupportEmail "dacos@diagautoclinic.co.za"
#define MyAppURL "https://diagautoclinic.co.za/dacos"
#define SourceDir "."  ; Since .iss is in root, source is current directory
#define DriversDir "drivers"
#define VenvDir ".venv"  ; Virtual environment in project root

[Setup]
AppId={{E8C3F7A2-9B4D-4E8F-A1C7-6D5F2B3C9A10}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion} - Alpha Release
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
AppContact={#MyAppSupportEmail}
DefaultDirName={autopf}\DiagAutoClinicOS\AutoDiag
DefaultGroupName=DiagAutoClinicOS\AutoDiag
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=Installer
OutputBaseFilename=DiagAutoClinicOS_AutoDiag_v{#MyAppVersion}_Alpha_Setup
SetupIconFile=assets\icons\app_icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=DiagAutoClinicOS AutoDiag Suite - Automotive Diagnostic Dashboard (Alpha Release)
VersionInfoCopyright=Copyright © 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoProductTextVersion=v{#MyAppVersion}
ArchitecturesInstallIn64BitMode=x64compatible
DisableWelcomePage=no
DisableDirPage=no
DisableProgramGroupPage=no
LicenseFile=LICENSE
InfoBeforeFile=docs\INSTALLATION_NOTES.txt
InfoAfterFile=docs\POST_INSTALL.txt
; Enable update/upgrade functionality
UninstallDisplayIcon={app}\assets\icons\app_icon.ico
CreateUninstallRegKey=yes
UninstallDisplayName={#MyAppName}
AppMutex=DiagAutoClinicOS_AutoDiag

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[CustomMessages]
english.SupportEmail=Support Email: {#MyAppSupportEmail}
english.VisitWebsite=Visit: {#MyAppURL}
english.InstallDrivers=Install Hardware Drivers
english.DriverInstallNote=Note: AutoDiag requires J2534/ELM327 compatible hardware
english.AlphaRelease=Alpha Release - AutoDiag Diagnostic Suite
english.AlphaWarning=This is an alpha release. Features may be incomplete or unstable.
english.VehicleSupport=Supports 200+ vehicle models across major brands (BMW, Audi, Mercedes, Ford, GM, etc.)
german.SupportEmail=Support Email: {#MyAppSupportEmail}
german.VisitWebsite=Visit: {#MyAppURL}
german.InstallDrivers=Install Hardware Drivers
german.DriverInstallNote=Note: AutoDiag requires J2534/ELM327 compatible hardware
german.AlphaRelease=Alpha Release - AutoDiag Diagnostic Suite
german.AlphaWarning=This is an alpha release. Features may be incomplete or unstable.
german.VehicleSupport=Supports 200+ vehicle models across major brands (BMW, Audi, Mercedes, Ford, GM, etc.)
french.SupportEmail=Support Email: {#MyAppSupportEmail}
french.VisitWebsite=Visit: {#MyAppURL}
french.InstallDrivers=Install Hardware Drivers
french.DriverInstallNote=Note: AutoDiag requires J2534/ELM327 compatible hardware
french.AlphaRelease=Alpha Release - AutoDiag Diagnostic Suite
french.AlphaWarning=This is an alpha release. Features may be incomplete or unstable.
french.VehicleSupport=Supports 200+ vehicle models across major brands (BMW, Audi, Mercedes, Ford, GM, etc.)

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "install_drivers"; Description: "{cm:InstallDrivers}"; GroupDescription: "Hardware Setup:"; Flags: checkedonce
Name: "install_sql_server"; Description: "Install SQL Server Express (Required for database)"; GroupDescription: "Database Setup:"; Flags: checkedonce
Name: "associate_logs"; Description: "Associate .dlog diagnostic files with AutoDiag"; GroupDescription: "File Associations:"; Flags: unchecked
Name: "create_vehicle_data_folder"; Description: "Create 'Vehicle Data' folder on Desktop"; GroupDescription: "Data Management:"; Flags: unchecked

[Files]
; ============================================================================
; AUTO DIAG SUITE FILES (Main Diagnostic Dashboard)
; ============================================================================
; AutoDiag application files
Source: "AutoDiag\*"; DestDir: "{app}\AutoDiag"; Flags: ignoreversion recursesubdirs

; ============================================================================
; SHARED CORE MODULES (Required by AutoDiag)
; ============================================================================
Source: "core\*"; DestDir: "{app}\core"; Flags: ignoreversion recursesubdirs
Source: "shared\*"; DestDir: "{app}\shared"; Flags: ignoreversion recursesubdirs
Source: "ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs
Source: "utils\*"; DestDir: "{app}\utils"; Flags: ignoreversion recursesubdirs

; ============================================================================
; DRIVERS FOR DIAGNOSTIC HARDWARE (Optional)
; ============================================================================
Source: "{#DriversDir}\*"; DestDir: "{app}\drivers"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist; Tasks: install_drivers

; ============================================================================
; VEHICLE DATA AND CAN BUS REFERENCES
; ============================================================================
Source: "can_bus_data\*"; DestDir: "{app}\can_bus_data"; Flags: ignoreversion recursesubdirs

; ============================================================================
; DOCUMENTATION AND ASSETS
; ============================================================================
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs
Source: "docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs
Source: "tests\AutoDiag\*"; DestDir: "{app}\tests"; Flags: ignoreversion recursesubdirs
Source: "scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs

; ============================================================================
; PYTHON DEPENDENCIES (from virtual environment)
; ============================================================================
; IMPORTANT: We include the entire virtual environment for offline installation
; This makes the installer large but ensures it works without internet
Source: "{#VenvDir}\*"; DestDir: "{app}\Python"; Excludes: "__pycache__\*,*.pyc,*.pyo"; Flags: ignoreversion recursesubdirs skipifsourcedoesntexist

; ============================================================================
; LAUNCHER AND PROJECT FILES
; ============================================================================
; We include launcher.py but with modified functionality - only launches AutoDiag
Source: "launcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "QUICKSTART.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

; ============================================================================
; SQL SERVER EXPRESS (if available)
; ============================================================================
Source: "{#DriversDir}\SQLEXPR_x64_ENU.exe"; DestDir: "{app}\drivers"; Flags: skipifsourcedoesntexist; Tasks: install_sql_server

[Icons]
; Main AutoDiag launcher - using a batch file for better Python environment handling
Name: "{group}\AutoDiag Diagnostic Suite"; Filename: "{app}\AutoDiag_Launcher.bat"; IconFilename: "{app}\assets\icons\app_icon.ico"; Comment: "Launch AutoDiag Diagnostic Dashboard"
Name: "{group}\View Documentation"; Filename: "{app}\docs\README.md"; IconFilename: "{sys}\shell32.dll"; IconIndex: 23
Name: "{group}\Quick Start Guide"; Filename: "{app}\QUICKSTART.md"; IconFilename: "{sys}\shell32.dll"; IconIndex: 23
Name: "{group}\Hardware Drivers"; Filename: "{app}\drivers"; IconFilename: "{sys}\shell32.dll"; IconIndex: 6; Tasks: install_drivers
Name: "{group}\Visit Website"; Filename: "{#MyAppURL}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 13
Name: "{group}\Support Email"; Filename: "mailto:{#MyAppSupportEmail}?subject=AutoDiag Support"; IconFilename: "{sys}\shell32.dll"; IconIndex: 19
Name: "{group}\Uninstall AutoDiag"; Filename: "{uninstallexe}"; IconFilename: "{sys}\shell32.dll"; IconIndex: 31
Name: "{commondesktop}\AutoDiag Diagnostic Suite"; Filename: "{app}\AutoDiag_Launcher.bat"; IconFilename: "{app}\assets\icons\app_icon.ico"; Tasks: desktopicon; Comment: "Launch AutoDiag Diagnostic Dashboard"

[Run]
; Run the AutoDiag application after installation
Filename: "{app}\AutoDiag_Launcher.bat"; Description: "Launch AutoDiag Diagnostic Suite"; Flags: nowait postinstall skipifsilent

; Open documentation after installation
Filename: "{app}\docs\README.md"; Description: "View Documentation"; Flags: postinstall shellexec unchecked

; Open drivers folder if installed
Filename: "{app}\drivers"; Description: "Open Hardware Drivers Folder"; Flags: postinstall shellexec unchecked; Tasks: install_drivers

; Install SQL Server Express if selected
Filename: "{app}\drivers\SQLEXPR_x64_ENU.exe"; Parameters: "/QS /ACTION=Install /FEATURES=SQLEngine /INSTANCENAME=DiagAutoClinic /SQLSVCACCOUNT=""NT AUTHORITY\Network Service"" /SQLSYSADMINACCOUNTS=""BUILTIN\ADMINISTRATORS"" /TCPENABLED=1 /IACCEPTSQLSERVERLICENSETERMS"; Description: "Install SQL Server Express"; Flags: postinstall skipifsilent; Tasks: install_sql_server

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\diagnostic_data"
Type: filesandordirs; Name: "{app}\exports"
Type: filesandordirs; Name: "{app}\config"
Type: filesandordirs; Name: "{userappdata}\DiagAutoClinicOS_AutoDiag"

[Registry]
; File association for .dlog files (if .ico exists)
Root: HKCR; Subkey: ".dlog"; ValueType: string; ValueData: "AutoDiag.DiagnosticLog"; Flags: uninsdeletevalue; Tasks: associate_logs
Root: HKCR; Subkey: "AutoDiag.DiagnosticLog"; ValueType: string; ValueData: "AutoDiag Diagnostic Log File"; Flags: uninsdeletekey; Tasks: associate_logs
Root: HKCR; Subkey: "AutoDiag.DiagnosticLog\DefaultIcon"; ValueType: string; ValueData: "{app}\assets\icons\app_icon.ico,0"; Tasks: associate_logs
Root: HKCR; Subkey: "AutoDiag.DiagnosticLog\shell\open\command"; ValueType: string; ValueData: """{app}\Python\python.exe"" ""{app}\AutoDiag\main.py"" ""%1"""; Tasks: associate_logs

; Application registry entries (for version tracking and updates)
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\AutoDiag"; ValueType: string; ValueName: "Version"; ValueData: "{#MyAppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\AutoDiag"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\AutoDiag"; ValueType: string; ValueName: "InstallDate"; ValueData: "{code:GetInstallDate}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\AutoDiag"; ValueType: string; ValueName: "SupportEmail"; ValueData: "{#MyAppSupportEmail}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#MyAppPublisher}\AutoDiag"; ValueType: string; ValueName: "Website"; ValueData: "{#MyAppURL}"; Flags: uninsdeletekey

[Code]
var
  UpdateExistingInstall: Boolean;
  PreviousVersion: String;

function GetInstallDate(Param: String): String;
begin
  Result := GetDateTimeString('yyyy-mm-dd', '-', '-');
end;

function InitializeSetup(): Boolean;
var
  OldVersion: String;
  Response: Integer;
begin
  // Check if already installed and get previous version
  UpdateExistingInstall := False;
  PreviousVersion := '';
  
  if RegKeyExists(HKLM, 'Software\{#MyAppPublisher}\AutoDiag') then
  begin
    if RegQueryStringValue(HKLM, 'Software\{#MyAppPublisher}\AutoDiag', 'Version', OldVersion) then
    begin
      PreviousVersion := OldVersion;
      UpdateExistingInstall := True;
      
      // Ask user if they want to update
      Response := MsgBox('An existing installation of {#MyAppName} v' + OldVersion + ' was found.' + #13#10 +
                         'Do you want to update to v{#MyAppVersion}?' + #13#10#13#10 +
                         'Note: Your configuration files will be preserved, but program files will be replaced.',
                         mbConfirmation, MB_YESNO or MB_DEFBUTTON1);
      
      if Response = IDNO then
      begin
        Result := False;
        Exit;
      end;
    end;
  end;
  
  // Display Alpha release warning
  if MsgBox('DiagAutoClinicOS - AutoDiag Suite v{#MyAppVersion}' + #13#10 +
            'ALPHA RELEASE WARNING' + #13#10#13#10 +
            'This is an alpha release intended for testing purposes only.' + #13#10 +
            'Features may be incomplete or unstable.' + #13#10 +
            'Not recommended for production use.' + #13#10#13#10 +
            'Do you wish to continue with installation?',
            mbConfirmation, MB_YESNO) = IDNO then
  begin
    Result := False;
  end
  else
  begin
    Result := True;
  end;
end;

procedure InitializeWizard();
begin
  // Customize wizard pages
  if UpdateExistingInstall then
  begin
    WizardForm.WelcomeLabel2.Caption :=
      'This will update {#MyAppName} from v' + PreviousVersion + ' to v{#MyAppVersion}.' + #13#10 +
      'Your configuration and data will be preserved.' + #13#10#13#10 +
      '{cm:AlphaWarning}' + #13#10 +
      '{cm:VehicleSupport}' + #13#10#13#10 +
      'Support: {#MyAppSupportEmail}' + #13#10 +
      'Website: {#MyAppURL}';
  end
  else
  begin
    WizardForm.WelcomeLabel2.Caption :=
      'This will install {#MyAppName} v{#MyAppVersion} (Alpha Release) on your computer.' + #13#10 +
      'AutoDiag is the diagnostic dashboard component of the DiagAutoClinicOS suite.' + #13#10#13#10 +
      '{cm:AlphaWarning}' + #13#10 +
      '{cm:VehicleSupport}' + #13#10#13#10 +
      'Support: {#MyAppSupportEmail}' + #13#10 +
      'Website: {#MyAppURL}';
  end;
    
  WizardForm.FinishedHeadingLabel.Caption := 'AutoDiag Installation Complete';
  
  if UpdateExistingInstall then
  begin
    WizardForm.FinishedLabel.Caption :=
      '{#MyAppName} has been successfully updated from v' + PreviousVersion + ' to v{#MyAppVersion}.' + #13#10#13#10 +
      'Key Updates:' + #13#10 +
      '• Updated core modules and dependencies' + #13#10 +
      '• Improved stability and bug fixes' + #13#10 +
      '• Enhanced vehicle compatibility' + #13#10#13#10 +
      'Your configuration and data have been preserved.' + #13#10#13#10 +
      'Support: {#MyAppSupportEmail}' + #13#10 +
      'Website: {#MyAppURL}';
  end
  else
  begin
    WizardForm.FinishedLabel.Caption :=
      '{#MyAppName} v{#MyAppVersion} has been successfully installed.' + #13#10#13#10 +
      'Key Features:' + #13#10 +
      '• Main Diagnostic Dashboard with 7 specialized tabs' + #13#10 +
      '• Real-time vehicle data monitoring' + #13#10 +
      '• 200+ vehicle models supported (BMW, Audi, Mercedes, Ford, GM, etc.)' + #13#10 +
      '• J2534 and ELM327 hardware compatibility' + #13#10#13#10 +
      'Next Steps:' + #13#10 +
      '1. Connect your diagnostic hardware (OBDLink MX+, GoDiag, etc.)' + #13#10 +
      '2. Launch AutoDiag from Desktop or Start Menu' + #13#10 +
      '3. Refer to Quick Start Guide for initial setup' + #13#10#13#10 +
      'Support: {#MyAppSupportEmail}' + #13#10 +
      'Website: {#MyAppURL}';
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigPath: String;
  OldConfigPath: String;
begin
  if CurStep = ssPostInstall then
  begin
    // Create necessary directories
    ForceDirectories(ExpandConstant('{app}\logs'));
    ForceDirectories(ExpandConstant('{app}\diagnostic_data'));
    ForceDirectories(ExpandConstant('{app}\exports'));
    ForceDirectories(ExpandConstant('{app}\config'));
    
    // Create AutoDiag launcher batch file
    SaveStringToFile(ExpandConstant('{app}\AutoDiag_Launcher.bat'),
      '@echo off' + #13#10 +
      'echo Starting AutoDiag Diagnostic Suite v{#MyAppVersion}...' + #13#10 +
      'echo.' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo DiagAutoClinicOS - AutoDiag' + #13#10 +
      'echo Alpha Release - For Testing Only' + #13#10 +
      'echo ========================================' + #13#10 +
      'echo.' + #13#10 +
      '' + #13#10 +
      'REM Set Python path to use embedded Python' + #13#10 +
      'set PYTHONHOME=%~dp0Python' + #13#10 +
      'set PYTHONPATH=%~dp0Python;%~dp0Python\Lib;%~dp0Python\Lib\site-packages' + #13#10 +
      'set PATH=%~dp0Python;%~dp0Python\Scripts;%PATH%' + #13#10 +
      '' + #13#10 +
      'REM Launch AutoDiag' + #13#10 +
      'python "%~dp0AutoDiag\main.py"' + #13#10 +
      '' + #13#10 +
      'if errorlevel 1 (' + #13#10 +
      '  echo.' + #13#10 +
      '  echo ERROR: AutoDiag failed to start.' + #13#10 +
      '  echo Check %~dp0logs\autodiag.log for details.' + #13#10 +
      '  echo.' + #13#10 +
      '  pause' + #13#10 +
      ')' + #13#10 +
      'exit', False);
    
    // Create simplified launcher.py that only launches AutoDiag
    SaveStringToFile(ExpandConstant('{app}\launcher.py'),
      '#!/usr/bin/env python3' + #13#10 +
      '"""' + #13#10 +
      'AutoDiag Launcher - Simplified version that only launches AutoDiag' + #13#10 +
      'For installer distribution' + #13#10 +
      '"""' + #13#10 +
      '' + #13#10 +
      'import os' + #13#10 +
      'import sys' + #13#10 +
      'import subprocess' + #13#10 +
      '' + #13#10 +
      'def main():' + #13#10 +
      '    print("Launching AutoDiag Diagnostic Suite...")' + #13#10 +
      '    print("Version: {#MyAppVersion}")' + #13#10 +
      '    print("Alpha Release - For Testing Only")' + #13#10 +
      '    print()' + #13#10 +
      '' + #13#10 +
      '    # Get the current directory' + #13#10 +
      '    app_dir = os.path.dirname(os.path.abspath(__file__))' + #13#10 +
      '    autodiag_path = os.path.join(app_dir, "AutoDiag", "main.py")' + #13#10 +
      '' + #13#10 +
      '    if not os.path.exists(autodiag_path):' + #13#10 +
      '        print(f"ERROR: AutoDiag not found at {autodiag_path}")' + #13#10 +
      '        input("Press Enter to exit...")' + #13#10 +
      '        return' + #13#10 +
      '' + #13#10 +
      '    try:' + #13#10 +
      '        # Launch AutoDiag' + #13#10 +
      '        subprocess.Popen([sys.executable, autodiag_path], cwd=os.path.join(app_dir, "AutoDiag"))' + #13#10 +
      '        print("AutoDiag launched successfully!")' + #13#10 +
      '    except Exception as e:' + #13#10 +
      '        print(f"ERROR: Failed to launch AutoDiag: {e}")' + #13#10 +
      '        input("Press Enter to exit...")' + #13#10 +
      '' + #13#10 +
      'if __name__ == "__main__":' + #13#10 +
      '    main()', False);
    
    // Handle configuration preservation during update
    if UpdateExistingInstall then
    begin
      // Backup old config if exists
      ConfigPath := ExpandConstant('{app}\config\autodiag_settings.ini');
      OldConfigPath := ExpandConstant('{app}\config\autodiag_settings.ini.backup');
      
      if FileExists(ConfigPath) then
      begin
        FileCopy(ConfigPath, OldConfigPath, False);
        Log('Backed up existing configuration: ' + ConfigPath);
      end;
    end;
    
    // Create default configuration if doesn't exist
    ConfigPath := ExpandConstant('{app}\config\autodiag_settings.ini');
    if not FileExists(ConfigPath) then
    begin
      SaveStringToFile(ConfigPath,
        '[AutoDiag]' + #13#10 +
        'Version={#MyAppVersion}' + #13#10 +
        'FirstRun=1' + #13#10 +
        'DefaultTheme=glassmorphic' + #13#10 +
        'DefaultVehicleBrand=Ford' + #13#10 +
        'LogLevel=INFO' + #13#10 +
        'SupportEmail={#MyAppSupportEmail}' + #13#10 +
        '', False);
    end;
    
    // Create vehicle data folder on desktop if selected
    if WizardIsTaskSelected('create_vehicle_data_folder') then
    begin
      ForceDirectories(ExpandConstant('{userdesktop}\Vehicle Data'));
    end;
    
    // Create README file
    SaveStringToFile(ExpandConstant('{app}\README_ALPHA.txt'),
      'DiagAutoClinicOS - AutoDiag Suite v{#MyAppVersion}' + #13#10 +
      '==============================================' + #13#10#13#10 +
      'ALPHA RELEASE - FOR TESTING PURPOSES' + #13#10#13#10 +
      'This is the AutoDiag diagnostic dashboard component.' + #13#10 +
      'Features:' + #13#10 +
      '• Dashboard Tab - System overview and quick actions' + #13#10 +
      '• Diagnostics Tab - Vehicle system diagnostics' + #13#10 +
      '• Live Data Tab - Real-time parameter monitoring' + #13#10 +
      '• Special Functions Tab - Advanced vehicle operations' + #13#10 +
      '• Calibrations Tab - Reset and calibration procedures' + #13#10 +
      '• Advanced Tab - Technical and developer tools' + #13#10 +
      '• Security Tab - Access control and security functions' + #13#10#13#10 +
      'Supported Hardware:' + #13#10 +
      '• OBDLink MX+ / EX' + #13#10 +
      '• GoDiag GT100 / GT100 Plus GPT' + #13#10 +
      '• Scanmatik 2' + #13#10 +
      '• Generic ELM327 interfaces' + #13#10#13#10 +
      'Vehicle Support: 200+ models across major brands (BMW, Audi, Mercedes, Ford, GM, etc.)' + #13#10#13#10 +
      'Support: {#MyAppSupportEmail}' + #13#10 +
      'Website: {#MyAppURL}' + #13#10 +
      'GitHub: https://github.com/DiagAutoClinic/DiagAutoClinicOS/' + #13#10 +
      'Installed: ' + GetDateTimeString('yyyy-mm-dd hh:nn:ss', '-', '-') + #13#10 +
      'Install Path: ' + ExpandConstant('{app}'),
      False);
  end;
end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  // Skip license page if updating
  if UpdateExistingInstall and (PageID = wpLicense) then
    Result := True
  else
    Result := False;
end;