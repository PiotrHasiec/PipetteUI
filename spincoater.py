import serial
from time import sleep
spincoater = serial.Serial('COM5', 19200, timeout=1) 
spincoater.write(b'va=1 \n')
sleep(1)
print(spincoater.write(b'em \n'))
sleep(1)

print(spincoater.write(b'rm \n'))
sleep(1)
for i in range(13):
    command = f'pg={i} \n'.encode()
    print(spincoater.write(command))
sleep(1)

print(spincoater.write(b'up \n'))
sleep(1)

print(spincoater.write(b'go=4 \n'))

for i in range(70):
    sleep(1)
    print(spincoater.read_all())
