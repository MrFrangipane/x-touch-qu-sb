import time

import pymidi.client


host = '192.168.1.34'
port = 5004
client = pymidi.client.Client((host, port))
print(f'Connecting to RTP-MIDI server @ {host}:{port} ...')
print('Connecting!')
while True:
    print('Striking key...')
    client.send_note_on('B6')
    time.sleep(0.5)
    client.send_note_off('B6')
    time.sleep(0.5)
