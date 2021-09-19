import paramiko
import requests
from time import sleep

class Website():
    def __init__(self, address):
        self.address = address
        self.get()

    def get(self):
        self.code = requests.get(self.address).status_code

class Ssh():
    def __init__(self, host, port, user, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, port, user, password)

    def exec(self, command):

        if command == 'cpu':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('awk \'{u=$2+$4; t=$2+$4+$5; if (NR==1){u1=u; t1=t;} else print ($2+$4-u1) * 100 / (t-t1); }\' \
            <(grep \'cpu \' /proc/stat) <(sleep 1;grep \'cpu \' /proc/stat)')

        elif command == 'ram_total':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('free --mega | awk \'/Mem:/ { printf("%3.2f", $2/1024) }\'')

        elif command == 'ram_%':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('free -m | awk \'/Mem:/ { printf("%3.1f", $3/$2*100) }\'')

        elif command == 'disk_name':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('df -BG | sed s:G:: | awk -F \' \' \'($2>5) {printf $1"\\n"}\' | head -1')

        elif command == 'disk_total':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('df -BG | sed s:G:: | awk -F \' \' \'($2>5) {printf $2"\\n"}\' | head -1')

        elif command == 'disk_%':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('df -BG | sed s:G:: | awk -F \' \' \'($2>5) {printf "%s\\n",$5}\' | head -1 | sed s:%::')

        elif command == 'uptime':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('awk \'{print $1}\' /proc/uptime')

        elif command == 'speedtest':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('speedtest-cli | grep -e ms -e Mbit')

        elif command == 'bandwidth_received':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('cat /proc/net/dev | grep -v Inter | grep -v face | awk -F\' \' \'{print $2}\' | awk \'{s+=$1} END {printf "%.0f", s}\'')

        elif command == 'bandwidth_transmited':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('cat /proc/net/dev | grep -v Inter | grep -v face | awk -F\' \' \'{print $10}\' | awk \'{s+=$1} END {printf "%.0f", s}\'')

        elif command == 'ip':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('curl ipinfo.io/ip')

        elif command == 'sensor':
            self.stdin, self.stdout, self.stderr = self.client.exec_command('python Desktop/bme80.py')

    def format_sensor(self):
        self.exec('sensor')
        temperature, pressure, humidity = self.get()
        return [str(round(float(temperature), 1)), pressure, humidity]

    def format_uptime(self):
        self.exec('uptime')
        uptime = int(float(self.get()[0]))
        days = 0
        hours = 0
        minutes = 0

        while uptime > 86400:
            days+=1
            uptime-=86400
        while uptime > 3600:
            hours+=1
            uptime-=3600
        while uptime > 60:
            minutes+=1
            uptime-=60

        return [days, hours, minutes]

    def calculate_bandwidth(self):
        self.exec('bandwidth_received')
        received1 = self.get()[0]
        sleep(1)
        self.exec('bandwidth_received')
        received2 = self.get()[0]

        self.exec('bandwidth_transmited')
        transmited1 = self.get()[0]
        sleep(1)
        self.exec('bandwidth_transmited')
        transmited2 = self.get()[0]

        r_count = (float(received2) - float(received1))/1024
        t_count = (float(transmited2) - float(transmited1))/1024
        r_unit = 'KB/s'
        t_unit = 'KB/s'

        if r_count > 1024:
            r_count /= 1024
            r_unit = 'MB/s'
        if t_count > 1024:
            t_count /= 1024
            t_unit = 'MB/s'

        return [f'{round(r_count, 1)} {r_unit}', f'{round(t_count, 1)} {t_unit}']

    def get(self):
        lines = self.stdout.readlines()
        return [line.replace('\n', '') for line in lines]

    def close(self):
        self.client.close()
