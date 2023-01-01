import os
import json
from typing import List

class Device():
    def __init__(self, id):
        self.id = id
        self.model, self.name, self.settings = self.get_device_info()
        self.system_packages, self.third_party_packages = self.get_packages()
        self.do_not_delete_packages = ["com.google.android.inputmethod.latin"]
        
    def get_packages(self):
        command = "adb -s {0} shell pm list packages".format(self.id)
        system_packages = read_command("{0} -f".format(command))
        third_party_packages = read_command("{0} -3".format(command))
        return [item.split('apk=')[1] for item in system_packages],  [item.split('package:')[1] for item in third_party_packages]
    
    def get_device_info(self):
       command  = "adb -s {0} shell getprop".format(self.id)
       device_model = read_command("{0} ro.product.model".format(command))
       device_name = read_command("{0} ro.product.name".format(command))
       device_settings = self.get_device_settings()
       return device_model, device_name, device_settings
    
    def get_device_settings(self):
        command = "adb -s {0} shell settings list".format(self.id)
        settings = {"system_settings" :[], "global_settings": [], "secure_settings": []}
        system_settings = read_command("{0} system".format(command))
        global_settings = read_command("{0} global".format(command))
        secure_settings = read_command("{0} secure".format(command))
        settings.update(system_settings= system_settings, global_settings = global_settings, secure_settings= secure_settings)
        return settings
    
    def get_changed_settings(self):
        input("Press enter after you changed target setting...")
        final_settings = self.get_device_settings()

        for key in self.settings:
            arr1 = self.settings[key]
            arr2 = final_settings[key]
            arr = set(arr1) ^ (set(arr2))
            if(len(arr)>0):
                print("Key: {0}, Value {1}".format(key,arr))
        
    
    def set_password(self,  old_password, new_password):
        if old_password == "":
            os.system("adb -s {0} shell locksettings set-password {1}".format(self.id,new_password))
        else:
            os.system("adb -s {0} shell locksettings set-password --old {1} {2}".format(self.id,old_password, new_password))
  
    def clear_password(self, current_password):
        os.system("adb -s {0} shell locksettings clear --old {1}".format(self.id,current_password))
        
    def set_settings(self,  settings:List[str]):
        for setting in settings:
            setting = setting.split(".",1)
            namespace = setting[0]
            key_value_pair = ' '.join(setting[1:])
            
            if '.' in key_value_pair:
                expression = "{0} {1}".format(namespace, key_value_pair)    
            else:    
                expression = "{0} {1} {2}".format(namespace, key_value_pair.split("=")[0], key_value_pair.split("=")[1])
           
            command = "adb -s {0} shell settings put {1}".format(self.id, expression)
            print(command)
            os.system(command)
    
    def set_home_app(self,  package):
        os.system("adb -s {0} shell cmd package set-home-activity {1}".format(self.id,package))
     
    def install_packages(self, apk_directories:List[str]):
        for dir in apk_directories:
          os.system("adb -s {0} install {1}".format(self.id, dir))
          
    def set_permissions(self, package,permissions:List[str]):
        for permission in permissions:
            os.system("adb -s {0} shell pm grant {1} {2}".format(self.id,package, permission))  
   
    def uninstall_packages(self, packages):
        for package in packages:
            if package not in self.do_not_delete_packages:
                os.system("adb -s {0} shell pm uninstall --user 0 {1}".format(self.id,package))
    
    def create_touch_event(self, inputs:List[str]):
        for input in inputs:
            input = input.split(" ")
            command = "adb -s {0} shell input tap {1} {2}".format(self.id, input[0], input[1])
            os.system(command)
             
            
    def expand_notifications(self):
        command = "adb shell cmd statusbar expand-notifications"
        os.system(command)
    
    def uninstall_google_packages(self):
        # get common device and google packages 
        google_third_party_packages = set(get_google_packages()).intersection(set(self.third_party_packages))
        google_system_packages = set(get_google_packages()).intersection(set(self.system_packages))
        extras = ["com.android.contacts",
                  "com.skype.raider",
                  "com.tblenovo.kidslauncher",
                  "com.tblenovo.center",
                  "com.tblenovo.soundrecorder",
                  "com.amazon.mp3",
                  "com.microsoft.bing.wallpapers",
                  "com.android.fmradio",
                  "com.google.android.music", 
                  "com.miui.screenrecorder",
                  "com.netflix.mediaclient", 
                  "com.mediatek.emcamera", 
                  "com.dolby.daxappui",
                  "com.google.android.contacts",
                  "com.mediatek.camera",
                  "cn.sinoangel.monsterclass",
                  "cn.sinoangel.kidcamera",
                  "cn.sinoangel.color",
                  "com.android.musicfx",
                  "com.android.providers.contacts",
                  "com.android.vending",
                  "com.microsoft.office.outlook",
                  "org.codeaurora.snapcam",
                  "com.caf.fmradio"
                  ]
        
        extra_third_party_packages = set(extras).intersection(set(self.third_party_packages))
        extra_system_packages = set(extras).intersection(set(self.system_packages))
        
        self.uninstall_packages(google_third_party_packages)
        self.uninstall_packages(google_system_packages)
        self.uninstall_packages(extra_third_party_packages)
        self.uninstall_packages(extra_system_packages)
    
    def remove_lock_screen(self):
        self.set_settings(["global.LOCKSCREEN_AD_ENABLED=0", "secure.lockscreen.disabled 1"])
        os.system("adb -s {0} shell locksettings clear".format(self.id))
        os.system("adb -s {0} shell locksettings set-disabled true".format(self.id))

    def toggle_mobile_data(self, value:bool):
        value = "enable" if value else "disable" 
        os.system("adb -s {0} shell svc data {1}".format(self.id, value))
   
    def toggle_wifi(self, value:bool):
       value = "enable" if value else "disable" 
       os.system("adb -s {0} shell svc wifi {1}".format(self.id, value))

            
class ADB():
    def __init__(self):
        self.devices = self.get_devices() # get connected device information
        
    def get_devices(self):
        ids = read_lines_command("adb devices")[1:]
        new = [s.strip().split('\t')[0] for s in ids]
        device_ids =  [x for x in new if x]
        devices = []
        for id in device_ids:
            devices.append(Device(id))
        return devices
   
def read_command(command):
    return os.popen(command).read().split()
    
def read_lines_command(command):
    return os.popen(command).readlines()

def get_google_packages():
    google_packages = []
    file = open("google-app-ids.json")
    packages_json =  json.load(file)
    for p in packages_json:
        google_packages.append(p['package_name'])
    return google_packages

