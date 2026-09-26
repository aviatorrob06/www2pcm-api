import platform

from bin_managers import linux_bin_manager, windows_bin_manager, mac_bin_manager

system = platform.system()

if system == "Linux":
    linux_bin_manager.main()
elif system == "Windows":
    windows_bin_manager.main()
elif system == "Darwin":
    mac_bin_manager.main()
else:
    raise RuntimeError(f"Unsupported OS: {system}")