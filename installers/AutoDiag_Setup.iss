#define MyAppName "DiagAutoClinicOS - AutoDiag Suite"
#define MyAppVersion "0.0.1-alpha"
#define MyAppPublisher "DACOS - Diagnostic Auto Clinic OS"
#define MyAppURL "https://diagautoclinic.co.za"
#define MyOutputBase "DACOS_Alpha_v0.0.1"

[Setup]
AppId={{3D411A4C-0B72-4A2F-9A2E-9B6C9A1D5A01}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={pf}\DiagAutoClinicOS
DefaultGroupName=DiagAutoClinicOS
DisableDirPage=no
DisableProgramGroupPage=no
OutputDir=Output
OutputBaseFilename={#MyOutputBase}
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
SetupIconFile=assets\icons\app_icon.ico
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "launcher.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "AutoDiag\*"; DestDir: "{app}\AutoDiag"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "shared\*"; DestDir: "{app}\shared"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: ".git\*"
Source: "Files\*"; DestDir: "{app}\Files"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "docs\QUICK_START.html"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\POST_INSTALL.txt"; DestDir: "{app}\docs"; Flags: ignoreversion
Source: "docs\INSTALLATION_NOTES.txt"; DestDir: "{app}\docs"; Flags: ignoreversion

[Icons]
Name: "{group}\AutoDiag Pro"; Filename: "{app}\Files\AutoDiag_Launcher.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icons\app_icon.ico"
Name: "{commondesktop}\AutoDiag Pro"; Filename: "{app}\Files\AutoDiag_Launcher.bat"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icons\app_icon.ico"
Name: "{group}\Documentation\Quick Start"; Filename: "{app}\docs\QUICK_START.html"
Name: "{group}\Documentation\Post Install"; Filename: "{app}\docs\POST_INSTALL.txt"
Name: "{group}\Documentation\Installation Notes"; Filename: "{app}\docs\INSTALLATION_NOTES.txt"

[Run]
Filename: "{app}\Files\AutoDiag_Launcher.bat"; Description: "Start AutoDiag Pro"; Flags: postinstall nowait skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
function IsPythonAvailable(): Boolean;
var ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
end;

procedure InitializeWizard();
begin
  // Proceed even if Python is missing; Files/Python_Installation_Guide.txt guides the user
end;
