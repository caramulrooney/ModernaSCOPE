from pymodbus.client import ModbusTcpClient

# DE-AD-BE-EF-FE-ED
# 192.168.0.210
# arp -s 192.168.0.210 de-ad-be-ef-fe-ed

client = ModbusTcpClient(host = "192.168.0.210")   # Create client object
client.connect()                           # connect to device, reconnect automatically
client.write_coil(100, True, slave=1)        # set information in device
result = client.read_coils(2, 3, slave=1)  # get information from device
print(result.bits[0])                      # use information
client.close()                             # Disconnect device                            # Disconnect device
