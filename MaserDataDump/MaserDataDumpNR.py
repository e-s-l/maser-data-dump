########################
# RECEIVE DATA THRO' TCP
# SAVE TO FILE
########################

# We have a serial-to-ethernet (s2e) device acting as a server.
# This program acts as TCP client to that server, reading the data it receives from the serial port.
#
# This is an alternate approach to the old ways--adopted for two reasons.
# 1. From some perspective by using the s2e, both masers appear the same.
# 2. This program can be run by occasional crons.
#
# That's the theory, anyway.

########################

########
# TODO #
########
#
# - rather than write to file, write to DB (see version in 'old' folder)
# - request the data by sending dump command...
# - use logging...
#

########################

import sys                          # for exit calls
import socket                       # for TCP/IP socket connection
import datetime                     # for the DOY in the name of the output file

############################
# Connection Configuration #
############################

tcp_address = ''        # thx IT
tcp_port = ''                    # for COM port 1
buffer_size = 4096                  # maybe overkill w the looping approach
timeout_secs = 20                   # a third of one minute

########
# NOTE #
########
#
# - serial port settings are set in the s2e web interface (port 9999)
# - i've just guessed this buffer size
# - timeout is enough to run down stairs & punch in the dump cmd (which is, btw: 24*0110D*)
#

########################

def process(data):
    """
    Convert byte-objet-string-thing to string,
    Remove the carridge returns (adopting *nix-style EOLs),
    Delete any extra whitespace.
    """

    # debug print("processing data")
    # K.I.S.S.
    return data.decode('utf-8').replace('\r', ' ').strip()


########################

def save(data, file):
    """
    Append the final data to todays data file.
    """

    # debug print("saving data")
    # open & write & close
    try:
        with open(file, 'a+') as f:         # 'plus' to make file if not exists
            f.write(f"{data}\n\n")
    except IOError as err:
        print(f'Failed to open file:\n{err}')

########################

def maser_data_dump():
    """
    Main function to request a data dump and save output to file.
    1. Open a TCP socket and try to connect.
    2. Request a data dump. 
    3. Start listening to the socket and record any data there.
    4. Clean the data.
    5. Save the data.
    """

    ##########
    # Set-up #
    ##########

    # output data file
    doy = datetime.datetime.now().strftime('%j')
    file_output = f"/home/oper/Data/MaserData/NR/MaserData-NR-{doy}.txt"
    # tcp socket connection
    print("Attempting to connect to: ", tcp_address, tcp_port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            ###########
            # Connect #
            ###########

            # create the connection to the tcp server (the s2e adaptor)
            s.connect((tcp_address, tcp_port))
            print("Connected :)")
            # set up a time out so program exits after data dries up:
            s.settimeout(timeout_secs)

            ##################
            # Start the dump #
            ##################

            # command to trigger the data dump:
            # option 1--with labels:
            #cmd = 'C24F0110DF'         # (this sends extra stuff too tho!)
            # option 2--without labels: 
            #cmd = '90F'                 # (buuuuut this has labels)
            cmd = '90F'
            s.sendall(cmd.encode('utf-8'))

            #########
            # NOTE: #
            #########
            # C = clear
            # 24F = request data
            # 0 = dump all, 1 = , agh, just see the manual
            # '90F' = output all analog channels withoutlabels

            #################
            # Read the port #
            #################

            # initialise empty byte-string-thing
            data = b''
            # enter a read-loop which breaks on timeout (no data)
            while True:
                try:
                    data += s.recv(buffer_size)
                    # debug print(data)
                except socket.timeout:          # wait a sec
                    break

            if data:
                print("Data recevied.")
                # clean up
                data = process(data)
                # print to screen (for debug)
                print(data)
                # save to file
                save(data, file_output)
            else:
                print("No data received.")
        except socket.error as err:
            print(f"Socket error :(\n{err}")
        except KeyboardInterrupt:
            print("\nSIGTERM!")
        finally:
            # disconnect & exit
            s.close()

########################

if __name__ == "__main__":
    sys.exit(maser_data_dump())