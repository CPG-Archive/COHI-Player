"""
Created on Feb 24 2024

#@author: scharfetter_admin
"""

import time
from socket import socket, AF_INET, SOCK_STREAM
from struct import pack, unpack
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import paramiko
from zeroconf import Zeroconf, ServiceBrowser

from auxiliaries import RPListener


class SDR_control(QObject):
    """     Class for STEMLAB ssh connection, server start and stop,
    data stream socket control and shutdown of the STEMLAB LINUX
    some methods emit a pyqtSignal(str) named SigMessage(messagestring) with argument messagestring 
    two settings are called via methods, i.e. set_play() and set_rec() for selecting play or rec
    :param : no regular parameters; communication occurs via
        __slots__: Dictionary with entries:
        __slots__[0]: irate, Type: int
        __slots__[1]: ifreq = LO, Type integer
        __slots__[2]: icorr Type: integer
        __slots__[3]: rates Type: list
    :raises [ErrorType]: none
    :return: none
    :rtype: none
    """
    __slots__ = ["irate", "ifreq", "icorr", "rates", "HostAddress", "LO_offset"]

    
    SigError = pyqtSignal(str)
    SigMessage = pyqtSignal(str)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_irate(self, _value):
        self.__slots__[0] = _value

    def get_irate(self):
        return(self.__slots__[0])

    def set_ifreq(self, _value):
        self.__slots__[1] = _value

    def get_ifreq(self):
        return(self.__slots__[1])

    def set_icorr(self, _value):
        self.__slots__[2] = _value

    def get_icorr(self):
        return(self.__slots__[2])

    def set_rates(self, _value):
        self.__slots__[3] = _value

    def get_rates(self):
        return (self.__slots__[3])

    def set_HostAddress(self, _value):
        self.__slots__[4] = _value

    def get_HostAddress(self):
        return(self.__slots__[4])

    def set_LO_offset(self, _value):
        self.__slots__[5] = _value

    def get_LO_offset(self):
        return(self.__slots__[5])


    def identify(self):
        """return important device characteristics:
        (1) allowed samplingrates as a dict: if discrete: give values, if continuous: give lower and upper bound
        (2) rate_type: discrete or continuous
        (3) RX, TX, or RX & TX
        (3) device name
        (4) device ID
        (5) max_IFREQ
        (6) min IFREQ
        (7) possible resolutions (bits): list
        (8) connection type: ethernet, USB, USB_Vethernet
        
        : param: none

        : return: device_ID_dict
        : rtype: dict
        """
        device_ID_dict = {"rates": {20000:0, 50000:1, 100000:2, 250000:3, 
                      500000:4, 1250000:5, 2500000:6},
                          "rate_type": "discrete",
                          "RX": True,
                          "TX": True,
                          "device_name": "STEMlab 125-14",
                          "device_ID": 0,
                          "max_IFREQ": 62500000,
                          "min_IFREQ": 0,
                          "resolutions": [16, 24, 32],
                          "connection_type": "ethernet"}
        return(device_ID_dict)

    def set_play(self):
        self.modality = "play"
        errorstate = False
        value = ""
        return(errorstate, value)  

    def set_rec(self):
        self.modality = "rec"
        errorstate = False
        value = ""
        return(errorstate, value)   

    def monitor(self):
        # print(f"Stemlabcontrol modality: {self.modality}")
        pass

    def config_socket(self):  ##TODO: make modality a slot rather than a method
        '''
        initialize stream socket for communication to sdr_transceiver_wide on
        the STEMLAB
        returns as errorflag 'False' if an error occurs, else it returns 'True'
        In case of unsuccessful socket setup popup error messages are sent
        param: configparams
        type: dict
        Returns:
            True if socket can be configures, False in case of error
            requires self.modality to have been set by set_play() or set_rec()
        '''
        # print(f'configparams ifreq: {self.get_ifreq()} , HostAddress: {self.get_HostAddress()}')
        # print(f'configparams irate: {self.get_irate()} , icorr: {self.get_icorr()}')
        # print(f'configparams rates: {self.get_rates()} , LO_offset: {self.get_LO_offset()}')

        self.ctrl_sock = socket(AF_INET, SOCK_STREAM)
        self.ctrl_sock.settimeout(5)
        try:
            self.ctrl_sock.connect((self.get_HostAddress(), 1001))
        except:
            self.SigError.emit("Cannot establish socket connection for streaming to the STEMLAB")
            return False
            # self.ctrl_sock.settimeout(None)
        self.data_sock = socket(AF_INET, SOCK_STREAM)
        self.data_sock.settimeout(5)
        try:
            self.data_sock.connect((self.get_HostAddress(), 1001))
        except:  # TODO: replace errormessages by parameterized signals connected to errorbox-calls, par = errormessage
            self.SigError.emit("Cannot establish socket connection for streaming to the STEMLAB")
            return False
        # self.data_sock.settimeout(None) ######FFFFFFFFFFFFF
        if (self.modality != "play") and (self.modality != "rec"):
            # TODO remove after tests 13-12-2023: auxi.standard_errorbox("Error , self.modality must be rec or play")
            self.SigError.emit("Error , self.modality must be rec or play")
            return False

        # send control parameters to ctrl_sock:
        if self.modality == "play":
            self.ctrl_sock.send(pack('<I', 2))
            self.ctrl_sock.send(pack('<I', 0 << 28
                                     | int((1.0 + 1e-6 * self.get_icorr())
                                           * self.get_ifreq() + 0 * self.get_LO_offset())))

            # TODO: check replacement 13-12-2023: print(f'effective LO: {int((1.0 + 1e-6 * win.icorr)* win.ifreq + system_state["LO_offset"])}')
            # print(f'effective LO: {int((1.0 + 1e-6 * self.get_icorr())* self.get_ifreq() + 0*self.get_LO_offset())}')
            self.ctrl_sock.send(pack('<I', 1 << 28 | self.get_rates()[self.get_irate()]))
            self.data_sock.send(pack('<I', 3))
        else:
            self.ctrl_sock.send(pack('<I', 0))
            # self.ctrl_sock.send(pack('<I', 0 << 28
            #                          | int((1.0 + 1e-6 * win.icorr)
            #                                * win.ifreq)))
            # self.ctrl_sock.send(pack('<I', 0 << 28
            #                          | int((1.0 + 1e-6 * [system_state["icorr"]])
            #                                * [system_state["ifreq"]])))
            self.ctrl_sock.send(pack('<I', 0 << 28
                                     | int((1.0 + 1e-6 * self.get_icorr())
                                           * self.get_ifreq())))
            # self.ctrl_sock.send(pack('<I', 1 << 28 | win.rates[win.irate])) FFFFFFFFFFFFFFFFFFFFFFFFFFFF

            # TODO: ckech change 13-12-2023
            # self.ctrl_sock.send(pack('<I', 1 << 28 | win.rates[system_state["irate"]])) TODO: last working version
            # self.ctrl_sock.send(pack('<I', 1 << 28 | system_state["rates"][system_state["irate"]]))
            self.ctrl_sock.send(pack('<I', 1 << 28 | self.get_rates()[self.get_irate()]))
            self.data_sock.send(pack('<I', 1))

        # TODO in further versions: diagnostic output to status message window: send signal
        # ("socket started")
        self.SigMessage.emit("socket started")
        return True

    def startssh(self):
        '''
        login to Host and start ssh session with STEMLAB
        Returns False if a connection error occurs, returns True if
        successful
        '''
        #print(f'configparams ifreq: {self.get_ifreq()} , HostAddress: {self.get_HostAddress()}')

        port = 22
        username = "root"
        password = "root"
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.SigMessage.emit("trying to start ssh connection with STEMLAB")
        try:
            self.ssh.connect(self.get_HostAddress(), port, username, password)
            self.SigMessage.emit("ssh connection successful")
            return True
        except:
            self.SigError.emit("Cannot connect to Host " + self.get_HostAddress())
            return False

    def sshsendcommandseq(self, shcomm):
        '''
        send ssh command string sequence via command string list shcomm
        '''
        count = 0
        while (count < len(shcomm)):  #TODO REM FIN check list, only diagnostic    TODO: rewrite loop more pythonian
            try:
                self.ssh.exec_command(shcomm[count])
            except:
                print("stemlab control sshsendcommandseq, command cannot be sent")
            count = count + 1
            time.sleep(0.1)
        self.SigMessage.emit("ssh command sent")

    def sdrserverstart(self):
        '''
        Purpose: start server sdr-transceiver-wide on the STEMLAB.
        Stop potentially running server instance before so as to prevent
        undefined communication
        '''
        errorstate = False
        value = ["",None]
        # TODO: future versions could send diagnostic output to status message indicator
        shcomm = []
        shcomm.append('/bin/bash /sdrstop.sh &')
        shcomm.append('/bin/bash /sdrstart.sh &')
        # connect to remote server via ssh
        if self.startssh() is False:
            value[0] = "SDR Server could not be started, please check if STEMLAB is connected correctly."
            return(errorstate, value)
        self.sdrserverstop()  #TODO ?is this necessary ?
        time.sleep(0.2)     # wait state for letting the server react before it is being accessed; issue after tetst unter LINUX Debian 12 
        self.sshsendcommandseq(shcomm)
        time.sleep(0.2)     # wait state for letting the server react before it is being accessed; issue after tetst unter LINUX Debian 12
        self.SigMessage.emit("transmit ssh command for ssh start")
        return(True, value)

    def sdrserverstop(self):
        '''
        Purpose: stop server sdr-transceiver-wide on the STEMLAB.
        '''
        shcomm = []
        shcomm.append('/bin/bash /sdrstop.sh &')
        self.sshsendcommandseq(shcomm)
        

    def RPShutdown(self):
        '''
        Purpose: Shutdown the LINUX running on the STEMLAB
        Sequence:   (1) stop server sdr-transceiver-wide on the STEMLAB.
                    (2) send 'halt' command via ssh, track result via stdout
                    (3) communicate steps and progress via popup messages
        '''
        if self.startssh() is False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("ignoring command")
            msg.setInformativeText(
                              "No Connection to STEMLAB or STEMLAB OS is down")
            msg.setWindowTitle("FATAL ERROR")
            msg.exec_()
            return
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("SHUTDOWN")
        msg.setInformativeText(
                              "Shutting down the STEMLAB !"
                              "Please wait until heartbeat stops flashing")
        msg.setWindowTitle("SHUTDOWN")
        msg.exec_()
        self.sdrserverstop()
        #stdin, stdout, stderr = self.ssh.exec_command("/sbin/halt >&1 2>&1")
        stdin, stdout, stderr = self.ssh.exec_command("/sbin/poweroff >&1 2>&1")
        #TODO check schnellere Variante mit poweroff statt halt
        chout = stdout.channel
        textout = ""
        while True:
            bsout = chout.recv(1)
            textout = textout + bsout.decode("utf-8")
            if not bsout:
                break

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("POWER DOWN")
        msg.setInformativeText("It is now safe to power down the STEMLAB")
        msg.setWindowTitle("SHUTDOWN")
        msg.exec_()

    def ping_RP(self):
        """ping server"""
        import socket
        server = self.get_HostAddress()
        port = 22
        timeout = 3
        try:
            socket.setdefaulttimeout(timeout)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server, port))
        except OSError as error:
            return False
        else:
            s.close()
            return True

    def update_service(self, zeroconf, type, name):
        """Called when a service is updated."""
        pass

    def search_RP(self):
        zeroconf = Zeroconf()
        listener = RPListener()
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        time.sleep(2)  # kurze Wartezeit für Antworten
        zeroconf.close()
        print("Found Red Pitayas:", listener.devices)
        return listener.devices




