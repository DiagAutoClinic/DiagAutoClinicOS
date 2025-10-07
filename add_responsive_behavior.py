#!/usr/bin/env python3
# Add responsive behavior to the window

with open('launcher.py', 'r') as f:
    content = f.read()

# Add a resize event handler method
resize_method = '''
    def resizeEvent(self, event):
        """Handle window resize for better responsive layout"""
        super().resizeEvent(event)
        # You can add dynamic layout adjustments here if needed
        pass
'''

# Insert the resize method before the main function
if 'def main():' in content:
    content = content.replace('def main():', resize_method + '\n\ndef main():')

with open('launcher.py', 'w') as f:
    f.write(content)

print("✅ Added responsive window behavior")
