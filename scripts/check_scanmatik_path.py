import os

paths = [
    r"C:\Program Files\Scanmatik\sm2j2534.dll",
    r"C:\Program Files (x86)\Scanmatik\smj2534.dll",
    r"C:\Program Files (x86)\Scanmatik\sm2j2534.dll",
    r"C:\Program Files (x86)\Scanmatik\smj2534_0202_usb.dll"
]

print("Checking paths:")
for p in paths:
    exists = os.path.exists(p)
    print(f"[{'FOUND' if exists else 'MISSING'}] {p}")
