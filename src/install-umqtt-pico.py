import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Jerome","jp:1984@")
print(wlan.isconnected())

import mip

mip.install('umqtt.robust')