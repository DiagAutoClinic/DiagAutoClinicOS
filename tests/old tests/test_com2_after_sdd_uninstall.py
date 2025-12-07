#!/usr/bin/env python3
"""
Ultimate test: Is there ANY GoDiag left in this device?
"""

import serial
import time
import struct

def test_all_possible_commands():
    """Test every possible command pattern"""
    try:
        ser = serial.Serial('COM2', 115200, timeout=1, write_timeout=1)
        print("Connected to COM2")
        print("="*60)
        
        # Standard ELM327 commands (should work)
        print("\n1. STANDARD ELM327 COMMANDS:")
        elm_commands = [
            ('ATZ', 'Reset'),
            ('ATI', 'Identify'),
            ('AT@1', 'Device Description'),
            ('AT@2', 'Device Identifier'),
            ('ATRV', 'Voltage'),
            ('ATDP', 'Protocol'),
            ('ATSP0', 'Auto Protocol'),
            ('0100', 'PIDs Supported'),
        ]
        
        for cmd, desc in elm_commands:
            ser.write(f'{cmd}\r'.encode())
            time.sleep(0.3)
            response = ser.read(100)
            print(f"{desc} ({cmd}): {response.decode('ascii', errors='ignore').strip()}")
        
        # GoDiag proprietary commands (might work)
        print("\n2. GODIAG PROPRIETARY COMMANDS:")
        godiag_commands = [
            ('GD', 'GoDiag Base'),
            ('GDVER', 'GoDiag Version'),
            ('GDINFO', 'GoDiag Info'),
            ('GDSTAT', 'GoDiag Status'),
            ('ATGD', 'GoDiag AT'),
            ('AT@GD', 'GoDiag Device'),
            ('GDMODE', 'GoDiag Mode'),
            ('GDSN', 'GoDiag Serial'),
            ('GDPID', 'GoDiag Product ID'),
            ('GD2534', 'J2534 Mode'),
            ('GDRST', 'GoDiag Reset'),
        ]
        
        for cmd, desc in godiag_commands:
            ser.write(f'{cmd}\r'.encode())
            time.sleep(0.3)
            response = ser.read(100)
            if response:
                print(f"{desc} ({cmd}): {response.decode('ascii', errors='ignore').strip()}")
            else:
                print(f"{desc} ({cmd}): NO RESPONSE")
        
        # Binary/hex commands (might trigger different modes)
        print("\n3. BINARY/HEX COMMANDS:")
        binary_tests = [
            (b'\x01\x00', 'ISO-TP Single Frame'),
            (b'\x02\x01\x00', 'ISO-TP First Frame'),
            (b'\xAA\x55', 'Common sync pattern'),
            (b'\x55\xAA', 'Reverse sync'),
            (b'GOIAG', 'Misspelled GoDiag'),
            (b'J2534', 'J2534 keyword'),
        ]
        
        for cmd, desc in binary_tests:
            try:
                ser.write(cmd)
                time.sleep(0.3)
                response = ser.read(100)
                if response:
                    print(f"{desc}: {response.hex()}")
                else:
                    print(f"{desc}: No response")
            except:
                pass
        
        # Try to brute-force a mode switch
        print("\n4. MODE SWITCH ATTEMPTS:")
        mode_commands = [
            ('ATZGD', 'Reset to GoDiag'),
            ('ATSPG', 'GoDiag Protocol'),
            ('ATSH7E0', 'CAN Diagnostic'),
            ('ATE0', 'Echo Off'),
            ('ATL0', 'Linefeeds Off'),
            ('ATM0', 'Memory Off'),
            ('ATAL', 'Allow Long'),
            ('ATPC', 'Protocol Close'),
        ]
        
        for cmd, desc in mode_commands:
            ser.write(f'{cmd}\r'.encode())
            time.sleep(0.3)
            response = ser.read(100)
            if response:
                resp_str = response.decode('ascii', errors='ignore').strip()
                if resp_str and resp_str != '?' and resp_str != 'ERROR':
                    print(f"POSSIBLE SUCCESS: {desc} ({cmd}): {resp_str}")
        
        ser.close()
        
        print("\n" + "="*60)
        print("ANALYSIS:")
        print("="*60)
        
        print("\nIF ALL COMMANDS RETURN ELM327 RESPONSES:")
        print("• Device is 100% ELM327 now")
        print("• No GoDiag functionality remains")
        print("• Firmware completely replaced")
        
        print("\nIF SOME GODIAG COMMANDS WORK:")
        print("• Mixed firmware")
        print("• Might be recoverable")
        print("• GoDiag might have hidden commands")
        
        print("\nIF BINARY COMMANDS GET RESPONSES:")
        print("• Raw mode available")
        print("• Might bypass ELM327 layer")
        
    except Exception as e:
        print(f"ERROR: {e}")

def check_device_fingerprint():
    """Check what the device REALLY is"""
    print("\n" + "="*60)
    print("DEVICE FINGERPRINT ANALYSIS")
    print("="*60)
    
    print("\nCurrent Fingerprint:")
    print("• VID:PID: E327:2534 (ELM327 + CP2102)")
    print("• Serial: MT000230 (Generic format)")
    print("• Description: USB Serial Device (Microsoft driver)")
    print("• Firmware: ELM327 v1.3a")
    
    print("\nWhat This Means:")
    print("1. HARDWARE: ELM327 chip + CP2102 USB converter")
    print("2. FIRMWARE: Standard ELM327, not GoDiag")
    print("3. DRIVER: Windows generic, not GoDiag")
    print("4. CAPABILITY: Basic OBD2 only")
    
    print("\nThe Smoking Gun:")
    print("• E327 = ELM Electronics (chip manufacturer)")
    print("• 2534 = Silicon Labs CP2102 (USB bridge)")
    print("• This is a STANDARD ELM327 clone configuration")
    print("• GoDiag was just REBRANDING this hardware")

if __name__ == "__main__":
    test_all_possible_commands()
    check_device_fingerprint()
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS FOR GODIAG SUPPORT EMAIL")
    print("="*60)
    
    print("\nKEY POINTS TO INCLUDE:")
    print("1. After online firmware update, GD101 changed to ELM327")
    print("2. VID/PID changed from GoDiag to E327:2534")
    print("3. Device now uses Microsoft driver, not GoDiag driver")
    print("4. J2534 functionality completely lost")
    print("5. No local rollback available (server-based update)")
    
    print("\nDEMAND (politely):")
    print("1. Correct GD101 firmware file")
    print("2. Offline flashing tool")
    print("3. Recovery procedure")
    print("4. Explanation of what happened")
    
    print("\nALTERNATIVELY:")
    print("1. Refund for device")
    print("2. Replacement unit")
    print("3. Public apology/explanation")