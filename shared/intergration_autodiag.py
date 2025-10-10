# Add to imports in main_v2_beta.py
from shared.special_functions import special_functions_manager, FunctionCategory
from shared.calibrations_resets import calibrations_resets_manager, ResetType

# Add to AutoDiagPro class __init__ method:
self.special_functions_manager = special_functions_manager
self.calibrations_resets_manager = calibrations_resets_manager

# Connect security managers
self.special_functions_manager.security_manager = self.security_manager
self.calibrations_resets_manager.security_manager = self.security_manager

# Create new tabs in init_ui method:
self.create_special_functions_tab()
self.create_calibrations_resets_tab()
