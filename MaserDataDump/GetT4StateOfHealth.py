#!/home/oper/esl/DataDump/.venv/bin/python3

###################
# REQUEST & RECEIVE
# UDP DATAGRAM
# SAVE TO FILE
# esl 2024
###################

########
# TODO #
########
# - proper logger
#

###################

import pandas as pd                     # for processing the formatting of the maser state of health parameters
from astropy.time import Time           # for timestamping the data in mjd
from datetime import datetime           # as above, ugh
import socket                           # for the UDP datagrams
import sys                              # for proper program exit calls

#############
# UDP stuff #
#############

server_address = ""          # "0.0.0.0" = all available network interfaces
server_port = ""                     # what's the default UDP port again?
udp_timeout = 2
buffer_size = 1024

class UDP:

    def __init__(self, address, port):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.address = address
            self.port = port
            self.socket.bind(('', self.port))
            self.socket.connect((self.address, self.port))
            print(f"UDP set-up on {self.address}:{self.port}")
        except socket.error as err:
            print(f"Socket error in connect :(\n{err}")
            sys.exit(1)

    def send(self, message):
        try:
            self.socket.sendto(message.encode(), (self.address, self.port))
            print("Sent: %s" % message)
        except socket.error as err:
            print(f"Socket error in send :(\n{err}")
            sys.exit(1)

    def receive(self):
        try:
            msgRaw, client_address = self.socket.recvfrom(buffer_size)
            print(f"Received from {client_address}: {msgRaw}")
            return msgRaw
        except socket.error as err:
            print(f"Socket error in receive :(\n{err}")
            sys.exit(1)
        
    def close(self):
        try:
            self.socket.close()
        except socket.error as err:
            print(f"Socket error while closing :(\n{err}")
            sys.exit(1)

########
# main #
########
def request_n_ye_shall_receive():

    # create udp server/client object:
    udp = UDP(server_address, server_port)

    # for specifics conversions of the t4 maser data to engineering units
    FileFactor=r'/home/oper/esl/DataDump/ParamFactors.csv'
    ParamFactors = pd.read_csv(FileFactor, delimiter = ";")

    # file output
    doy = datetime.now().strftime('%j')
    output_file = f"/home/oper/Data/MaserData/T4/MaserData-T4-{doy}.txt"

    #####################
    # request & receive #
    #####################
    try:
        # initialise the pandas dataframe
        df = pd.DataFrame(columns=['Parameter','Value'])
        udp.send('MONIT;\r\n')              # request
        try:
            msg = udp.receive()             # receive
            # if got something then...
            if msg:
                # specific formatting of SOH data from the T4 maser:
                data = str(msg, "utf-8").replace('\r', '').replace('\n', '').replace('$', '')
                # if the data matches our expectations then...
                # NOTE: this if statement is mostly someone elses code...
                if len(data) == 113:
                    timestamp_mjd = Time(str(datetime.now()), format="iso").mjd
                    timestamp_df = pd.DataFrame({'Parameter': ['Timestamp'], 'Value': [str(timestamp_mjd)]})
                    df = pd.concat([timestamp_df],ignore_index=True)
                    i = 1
                    while (i < 42):
                        if i < 33:
                            value = float(int('0x' + data[0:3], 16))
                            data = data[3:]
                        else:
                            value = float(int('0x' + data[0:2], 16))
                            data = data[2:]
                        #####
                        New_Row = pd.DataFrame({'Parameter':[str(ParamFactors['Titles'][i])], 'Value' :[str(value * float(ParamFactors['ArrayFactors'][i]))]})
                        fram = [df,New_Row]
                        df = pd.concat(fram,ignore_index=True)
                        i += 1
                ################
                # save to file #
                ################
                data_list = df.values.tolist()
                try:
                    with open(output_file, 'a+') as f:
                        for i in range(0,len(data_list)):
                            f.write(f"{data_list[i][0]} {data_list[i][1]}\n")
                except IOError as err:
                    print(f'Failed to open file to write :(\n{err}')
        except TimeoutError as err:
            print(f'Timeout :(\n{err}')
    finally:
      udp.close()


if __name__ == "__main__":
    sys.exit(request_n_ye_shall_receive())
