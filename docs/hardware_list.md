# Hardware List (On-Hand)

## 1. Hardware

- **Godiag GT100 breakout box** — Excellent for making clean bench harnesses, switching ignition/power lines and wiring multiple modules. Use as physical interface between ECU and your emulator.
- **Godiag GD101 J2534** — Pass-thru for reflashing; spoofed ELM327 chip behavior. **Note:** Requires J2534 driver initialization BEFORE opening any serial connection (Windows needs to see VCI first). Firmware v1.15 tested ok.
- **Launch X431 Pro 5 / X-Prog** — Diagnostics, coding and MCU programmers (useful if you need to change configuration or read certain memories; X-Prog for EEPROM/MCU programming).
- **ELM327 v1.5 / v2.1** — Cheap CAN/OBD sniffing where low timing accuracy is OK (useful for quick checks, NOT ideal for tight timings).
- **OBDLink MX+** — Very reliable USB/Bluetooth CAN logger; good for consistent logging and used with PC tools.
- **PCMmaster (Scanmatik Pro2)** — The only other J2534 VCI left. Used for flash/ECU dumps.
- **Scanmatik Pro2 + Tricore cable** — Critical for Tricore ECUs, reading/writing memory, JTAG access, for deep bench work.
- **VX SCAN OP-COM v1.99** — Opel-specific diagnostics, useful to reproduce exact state/gateway messages.
- **STM32F103C8T6 (“Blue Pill”)**
- **ST-Link V2 (Original)** → Flash/debug
- **ST-Link clones** → Backups, secondary dev
- **J-Link Original** → Advanced debugging and JTAG/SWD flashing

## 2. Final System Profile: Laptop

| Specs          | Value                                              |
|----------------|----------------------------------------------------|
| Laptop         | Acer TravelMate P2510-G2-M-84MQ                    |
| CPU            | Intel® Core™ i7-8550U (1.8 → 4.0 GHz, 4C/8T)       |
| RAM            | 12 GB DDR4 (upgradable)                            |
| Storage        | 1 TB Samsung NVMe SSD + 1 TB WD HDD                |
| GPU            | Intel® UHD Graphics 620                            |
| OS Installed   | Windows 10 Pro 64-bit (22H2, Build 19045.6456)     |
| Ports          | USB-C, 3.0, 2.0×2, HDMI, VGA, RJ45, SD             |
| Connectivity   | 802.11ac, BT 4.0, Gigabit LAN                      |

## 3. Software List

### 1. Diagnostic Software

| Software Name                        | Location         | Notes                                              |
|--------------------------------------|------------------|----------------------------------------------------|
| CAT SIS 2022                         | d3               | Caterpillar Service Information System             |
| CAT SIS 2019 Torrent File            | Downloads 2      | Likely backup/download                             |
| CAT et 2019C                         | d4               | Caterpillar Electronic Technician                  |
| CONSULT III+ v82.11.00-82.50.00      | Downloads 2      | Nissan/Renault diagnostic                          |
| CONSULT3PlusV7.secured               | Downloads 2      | Secured version                                    |
| DiagAutoClinic                       | DiagAutoClinic   | Custom clinic diagnostic suite                     |
| DiagSoftware                         | DiagSoftware     | General diagnostic tools                           |
| FORScanSetup2.3.48.release           | d3\GoDiag GD101  | Ford/Mazda OBD tool                                |
| GoDIAG J1979 TesterSetup_vc-x86_2v3  | d3\GoDiag GD101  | OBD tester                                         |
| hds                                  | d3\GoDiag GD101  | Honda Diagnostic System                            |
| New Download (various)               | New Download     | Includes ScanMaster, SDFLASH, etc.                 |
| ODIS-E 18.1.0                        | Downloads 2      | Opel Diagnostic Interface                          |
| ODIS-S 24.3.1                        | Downloads 2      | VW/Audi Group Offboard Diagnostic                  |
| PCMFLASH                             | d3\GoDiag GD101  | ECU flashing tool (also in d4)                     |
| PCM Flasher Link                     | d4               | PCMFLASH support                                   |
| pcmflash-1.4.0-1                     | Downloads 2      | PCMFLASH v1.4                                      |
| PowerISO 8.1 Full (64 Bit)           | d4               | ISO/image tool (diagnostic support)                |
| ScanMaster                           | d4               | Generic OBD scanner                                |
| Techstream_Setup_V17.00.020          | d3\GoDiag GD101  | Toyota/Lexus diagnostic (multiple copies)          |
| VCDS                                 | VCDS             | VAG-COM Diagnostic System (Ross-Tech)              |
| VCI Manager JLR_1.4.2.1810           | VCI Manager JLR  | Jaguar/Land Rover interface                        |
| Xentry / SDflash                     | New Download     | Mercedes-Benz diagnostic & flashing                |

### 2. ECU Software & Tools

| Software Name                          | Location        | Notes                                      |
|----------------------------------------|-----------------|--------------------------------------------|
| ECM TITANIUM 26100                     | 10 ECU Gifts    | ECU remapping tool                         |
| ECM TITANIUM 26100 (archive)           | 10 ECU Gifts    | WinRAR backup                              |
| ECU maps                               | 10 ECU Gifts    | ECU map files                              |
| ECU Pinouts collection                 | 10 ECU Gifts    | Wiring & pinout database                   |
| Ecu Safe 2.0                           | 10 ECU Gifts    | ECU safety/backup tool                     |
| public-archivedw1-317                  | 10 ECU Gifts    | Archived ECU data                          |
| Setup DPF EGR Lambda Remover 05.20...  | 10 ECU Gifts    | DPF/EGR delete tool                        |
| Winols_24                              | 10 ECU Gifts    | WinOLS ECU editing (v2.4?)                 |
| BOOT OTx-DIAG                          | New Download    | ECU boot mode diagnostics                  |
| DBWXI NG3 After Sales STANDARD         | New Download    | BMW ECU tool                               |
| FullFix for Xentry and Truck v8.3.1    | New Download    | Mercedes Xentry fix                        |
| SDFLASH 2008-10                        | New Download    | ECU flashing (older)                       |
| sp421-b 9.1                            | sp421-b 9.1     | ECU programming suite                      |
| WinOLS                                 | 10 ECU Gifts    | ECU file editor                            |
| ZENZEFI Downgrade for 12-28 xentry     | New Download    | Xentry downgrade tool                      |

### 3. Key Coding / IMMO / Security

| Software Name                              | Location | Notes                              |
|--------------------------------------------|----------|------------------------------------|
| Immo Code Calculator v147                  | IMMO     | Universal IMMO calculator          |
| Immo_Decoding v3.2                         | IMMO     | PIN/code extraction                |
| Immo_Killer_v1.1                           | IMMO     | IMMO off tool                      |
| Immo Login_Calculator                      | IMMO     | Login code generator               |
| IMMO_Service_Tool v1.0+v1.2                | IMMO     | IMMO service suite                 |
| IMMO_Universal_Keygen_v3.2                 | IMMO     | Keygen for IMMO tools              |
| MultiFlasher v1.2.1                        | IMMO     | ECU & key flashing                 |
| Opel Pin Repair                            | IMMO     | Opel immobilizer repair            |
| Opel VIN Decoder                           | IMMO     | VIN to PIN                         |
| OTOCheck_Immo_Tool_v2.0                    | IMMO     | Key programming tool               |
| Professional EGR+Immo+HotStart Rem...      | IMMO     | Multi-function remover             |
| IMMOFF17_Launcher_v2.1162.au3              | IMMO     | AutoIt script launcher             |
| Immokiller v1.10                           | IMMO     | IMMO bypass                        |
| ImmoTool v1.5                              | IMMO     | Key coding utility                 |
| ME 7.1.1_LookKit_jam5_lastBetaNov23.au3    | IMMO     | ECU key learning script            |

### 4. Support Tools & Utilities

| Tool                               | Purpose                              |
|------------------------------------|--------------------------------------|
| AOMEI Partition Assistant 8.4.0    | Disk management                      |
| Autocom 2021.11 + KEYGEN           | Delphi/Autocom diagnostic            |
| FoxFlash Manager                   | ECU programmer interface             |
| Getintopc.com AOMEI...             | AOMEI backup                         |
| MongoosE JLR                       | JLR passthru interface               |
| Office 2016 64bit                  | Documentation                        |
| OP-COM                             | Opel diagnostic interface            |
| PCM-Setup                          | PCMFLASH installer                   |
| PHP-Mailer-master                  | Scripting (possible automation)      |
| PIWIS OEM Driver PT3G              | Porsche diagnostic driver            |
| RCC v2.31                          | Renault CAN Clip patch               |
| SDD 164.00.01 FULL                 | Jaguar/Land Rover SDD                |
| Visual-C-Runtimes-All-in-One-Nov-2024 | Runtime libraries                 |
| 7-Zip, AnyDesk, Acronis, etc.      | General utilities                    |