from shutil import copyfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def factory_reset():
    default_config = Path("/default/defaultConfig.py")
    current_config = Path("config.py")

    if not default_config.exists():
        logger.error(f"Default config not found: {default_config}")
        print("Error: Default config not found")
        return False
    try:
        copyfile(str(default_config), str(current_config))
        logger.info("Configs have been reset")
        return True
    except (FileNotFoundError, OSError, PermissionError) as e:
        logger.error(f"Factory Reset Failed: {e}")
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    factory_reset()
