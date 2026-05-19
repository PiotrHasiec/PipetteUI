import serial
def wait_for_stop(connection):
    stopset = ['_','A','B','C','D','E','F','G','H','I','J']
    while True:
        connection.write(b'g')
        w = connection.read(1000).decode('utf-8')
        print(w)
        if w in stopset:
            break
def start(connection):
    connection.write(bytes(f'{-50} 3200\n', 'utf-8'))
    wait_for_stop(connection)
    connection.write(bytes(f'{500} 3200\n', 'utf-8'))
    wait_for_stop(connection)
    connection.write(bytes(f'{-100} 3200\n', 'utf-8'))
    wait_for_stop(connection)


stopset = ['_','A','B','C','D','E','F','G','H','I','J']
connection = serial.Serial(
        'COM5',
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=1 # could probably be less
    )
connection.write(b'g')


start(connection)
input("Press Enter to continue...")
N= 250
connection.write(bytes(f'{-N} 3200\n', 'utf-8'))
wait_for_stop(connection)
input("Press Enter to continue...")
connection.write(bytes(f'{N+50} 3200\n', 'utf-8'))
wait_for_stop(connection)
connection.write(b'-50 3200\n')
wait_for_stop(connection)
connection.write(b"s")
wait_for_stop(connection)

connection.close()


