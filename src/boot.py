# boot.py - - runs on boot-up
# import os
# import upip
# from gp_config import GrowplantConfig
# from gp_network import GrowplantNetwork

# Config
# print("Boot init ...")

# # Install package
# print("Checking package...")
# if '/lib' not in os.listdir('/') and 'umqtt' not in os.listdir('/lib'):
#     print("Reading config...")
#     config = GrowplantConfig("secrets.json")

#     # Connect network
#     print("Connecting network...")
#     network = GrowplantNetwork(config.thing_hostname,
#                                config.wifi_ssid, config.wifi_password)
#     network.connect_network()
#     print("Installing package...")
#     upip.install("micropython-umqtt.simple2")

# print('Boot finish successfully')
