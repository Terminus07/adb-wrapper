# adb-wrapper

A Python ADB wrapper for executing commands on multiple devices. This tool can be used to uninstall pre-installed Google Play Store packages, store device settings, modify package permissions and install APK files.

## Installation

- Download [SDK Platform-Tools for Windows](https://dl.google.com/android/repository/platform-tools-latest-windows.zip)
- [Add ADB to your PATH variable](https://www.xda-developers.com/adb-fastboot-any-directory-windows-linux/)
- Run `pip install git+https://github.com/Terminus07/adb-wrapper@main`

## Usage

```Python
from adb import ADB, Device
dirs = [r'C:\Desktop\example.apk']
apks = ["com.example.package']
permissions = ["android.permission.WRITE_EXTERNAL_STORAGE"]
settings = ["global.wifi_on=0"] # NAMESPACE.KEY=VALUE (namespace is either system,secure or global)

adb = ADB()
device:Device # define as device type

for device in adb.devices: # run for each device
    device.install_packages(dirs)  # install all specified packages
    device.uninstall_packages(apks) # uninstall all specified packages
    device.uninstall_google_packages() # uninstall all third party and system apps found on your device
    device.set_permissions(permissions, package) # set app permissions
    device.set_password('', '1234') # set pin (if no pin is set)
    device.set_password('1234', '5555') # change lockscreen password
    device.clear_password('1234') # clear lockscreen password
    device.remove_lock_screen() # remove lockscreen
    device.create_touch_event(["1100 78", "1000 100"]) # execute specific touch event
    device.set_settings(settings) # set settings
    device.toggle_wifi(True) # turn wifi on/off
    device.toggle_mobile_data(True) #turn mobile data on/off
    print(device.settings) # prints device settings
```
