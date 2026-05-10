"""
Created on Feb 24 2024

#@author: scharfetter_admin
"""
from operator import truediv

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback, sys
import numpy as np
from SDR_control import *
import os.path

from datetime import datetime

from auxiliaries import WAVheader_tools




class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    timing = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done






class playrec_worker(QObject):
    """ worker class for data streaming thread from PC to STEMLAB
    object for playback and recording thread
    :param : no regular parameters; as this is a thread worker communication occurs via
        __slots__: Dictionary with entries:
        __slots__[0]: filename = complete file path pathname/filename Type: str
        __slots__[1]: timescaler = bytes per second  TODO: rescaling to samples per second would probably be more logical, Type int
        __slots__[2]: TEST = flag for test mode Type: bool
        __slots__[3]: pause = flag if stream should be paused (True) or not (False)
        __slots__[4]: filehandle
        __slots__[5]: data segment to be returned every second
        __slots__[6]: gain, scaling factor for playback
        __slots__[7]: formatlist: [formattag blockalign bitpsample]
    :type : dictionary
    '''
    :raises [ErrorType]: none
    '''
        :return: none
        :rtype: none
    """

    __slots__ = ["filename", "timescaler", "TEST", "pause", "fileHandle", "data", "gain" ,"formattag" ,"datablocksize","fileclose","configparameters","actual_file"]

    SigFinished = pyqtSignal()
    SigIncrementCurTime = pyqtSignal(int)
    SigBufferOverflow = pyqtSignal()
    SigError = pyqtSignal(str)
    SigNextfile = pyqtSignal(str)
    SigInfomessage = pyqtSignal(str)
    SigRelay = pyqtSignal(str, object)

    def __init__(self, stemlabcontrolinst,*args,**kwargs):

        super().__init__(*args, **kwargs)
        self.stopix = False
        #self.pausestate = False
        self.JUNKSIZE = 2048*4
        self.DATABLOCKSIZE = 1024*4
        self.mutex = QMutex()
        self.stemlabcontrol = stemlabcontrolinst
        self.segment_jump = False

    def set_filename(self,_value):
        self.__slots__[0] = _value
    def get_filename(self):
        return(self.__slots__[0])
    def set_timescaler(self,_value):
        self.__slots__[1] = _value
    def get_timescaler(self):
        return(self.__slots__[1])
    def set_TEST(self,_value):
        self.__slots__[2] = _value
    def get_TEST(self):
        return(self.__slots__[2])
    def set_pause(self,_value):
        self.__slots__[3] = _value
    def get_pause(self):
        return(self.__slots__[3])
    def get_fileHandle(self):
        return(self.__slots__[4])
    def set_fileHandle(self,_value):
        self.__slots__[4] = _value
    def get_data(self):
        return(self.__slots__[5])
    def set_data(self,_value):
        self.__slots__[5] = _value
    def get_gain(self):
        return(self.__slots__[6])
    def set_gain(self,_value):
        self.__slots__[6] = _value
    def get_formattag(self):
        return(self.__slots__[7])
    def set_formattag(self,_value):
        self.__slots__[7] = _value
    def get_datablocksize(self):
        return(self.__slots__[8])
    def set_datablocksize(self,_value):
        self.__slots__[8] = _value
    def get_fileclose(self):
        return(self.__slots__[9])
    def set_fileclose(self,_value):
        self.__slots__[9] = _value
    def get_configparameters(self):
        return(self.__slots__[10])
    def set_configparameters(self,_value):
        self.__slots__[10] = _value
    def get_actual_file(self):
        return (self.__slots__[11])
    def set_actual_file(self, _value):
        self.__slots__[11] = _value

    def play_loop_filelist(self):
        """
        worker loop for sending data to STEMLAB server
        data format i16; 2xi16 complex; FormatTag 1
        sends signals:     
            SigFinished = pyqtSignal()
            SigIncrementCurTime = pyqtSignal()
            SigBufferOverflow = pyqtSignal()

        :param : no regular parameters; as this is a thread worker communication occurs via
        class slots __slots__[i], i = 0...8
        __slots__[0]: filename = complete file path pathname/filename Type: list
        __slots__[1]: timescaler = bytes per second  TODO: rescaling to samples per second would probably be more logical, Type int
        __slots__[2]: TEST = flag for test mode Type: bool
        __slots__[3]: pause : if True then do not send data; Boolean
        __slots__[4]: filehandle: returns current filehandle to main thread methods on request 
        __slots__[5]: data segment to be returned every second
        __slots__[6]: gain, scaling factor for playback
        __slots__[7]: formatlist: [formattag blockalign bitpsample]
        __slots__[8]: datablocksize
        __slots__[9]: file_close
        __slots__[10]: sampling_parameters
        __slots__[11]: actual_file
        """
        #print("reached playloopthread")
        filenames = self.get_filename()
        #TODO: self.fmtscl = self.__slots__[7] #scaler for data format      ? not used so far
        self.stopix = False
        self.set_fileclose(False)
        self.junkcount = 0
        self.segment_count = 0


        filename = filenames[0]
        self.playfile = filename['segment_file']
        position = 0

        fileparam = WAVheader_tools().get_sdruno_header(self.playfile)

        lw_dir = os.path.dirname(self.playfile)

        if fileparam:

            while '.wav' in fileparam['nextfilename'] or self.segment_count == 0:

                if self.stopix is True:
                    break

                #if self.segment_jump:
                    #position = self.segment_jumpposition
                    #print('Segment Jump, Position: ', position)
                #else:
                    #position = 0

                nextfilename_clean = fileparam['nextfilename'].rstrip('\x00').strip()
                newfile = os.path.join(lw_dir, nextfilename_clean)

                self.play_file(self.playfile,position)

                if self.stopix is True:
                    break

                self.segment_count =+ 1

                if self.segment_jump:
                    self.segment_jump = False
                    position = self.segment_jumpposition
                    #print('Segment Jump, Position: ', position)
                else:
                    self.playfile = newfile
                    position = 0

                if '.wav' in fileparam['nextfilename']:
                    fileparam = WAVheader_tools().get_sdruno_header(self.playfile)
                else:
                    break


        # print('worker  thread finished')
        self.SigFinished.emit()
        print("SigFinished from playloop emitted")




    def play_file(self,filename,position):

        #print('Player Position: ', position, '     Player Junkcount: ', self.junkcount)

        timescaler = self.get_timescaler()
        TEST = self.get_TEST()
        gain = self.get_gain()

        self.fileHandle = open(filename, 'rb')
        self.SigNextfile.emit(filename)
        self.set_actual_file(filename)
        #print(f"filehandle for set_4: {fileHandle} of file {filename} ")
        self.set_fileHandle(self.fileHandle)
        format = self.get_formattag()
        self.set_datablocksize(self.DATABLOCKSIZE)
        #print(f"Filehandle :{fileHandle}")
        self.junkcount = self.junkcount + position
        self.fileHandle.seek(216 + position * self.JUNKSIZE, 0)
        if format[2] == 16:
            data = np.empty(self.DATABLOCKSIZE, dtype=np.int16)
        else:
            data = np.empty(self.DATABLOCKSIZE, dtype=np.float32) #TODO: check if true for 32-bit wavs wie Gianni's
        #print(f"playloop: BitspSample: {format[2]}; wFormatTag: {format[0]}; Align: {format[1]}")
        if format[0] == 1:
            normfactor = int(2**int(format[2]-1))-1
        else:
            normfactor = 1
        if format[2] == 16 or format[2] == 32:
            size = self.fileHandle.readinto(data)
        elif format[2] == 24:
            data = self.read24(format,data,self.fileHandle)
            size = len(data)
        self.set_data(data)
        junkspersecond = timescaler / self.JUNKSIZE * 32
        self.SigIncrementCurTime.emit(0)
        count = 0
        # self.junkcount = 0
        # print(f"Junkspersec:{junkspersecond}")
        while size > 0 and not (self.stopix or self.segment_jump):
            if not TEST:
                if not self.get_pause():
                    try:
                        self.stemlabcontrol.data_sock.send(
                                                gain*data[0:size].astype(np.float32)
                                                /normfactor)  # send next DATABLOCKSIZE samples
                    except BlockingIOError:
                        print("Blocking data socket error in playloop worker")
                        time.sleep(0.1)
                        self.SigError.emit("Blocking data socket error in playloop worker")
                        self.SigFinished.emit()
                        time.sleep(0.1)
                        return
                    except ConnectionResetError:
                        print("Diagnostic Message: Connection data socket error in playloop worker")
                        time.sleep(0.1)
                        self.SigError.emit("Diagnostic Message: Connection data socket error in playloop worker")
                        self.SigFinished.emit()
                        time.sleep(0.1)
                        return
                    except Exception as e:
                        print("Class e type error  data socket error in playloop worker")
                        print(e)
                        time.sleep(0.1)
                        self.SigError.emit(f"Diagnostic Message: Error in playloop worker: {str(e)}")
                        self.SigFinished.emit()
                        time.sleep(0.1)
                        return
                    if format[2] == 16 or format[2] == 32:
                        size = self.fileHandle.readinto(data)
                        if size == 0:
                            print("No data available")
                            self.fileHandle.seek(216 + self.junkcount * self.JUNKSIZE, 0)
                            time.sleep(0.1)
                            size = self.fileHandle.readinto(data)

                    elif format[2] == 24:
                        data = self.read24(format,data,self.fileHandle)
                        size = len(data)

                    #  read next 2048 samples
                    count = count + 1
                    self.junkcount = self.junkcount + 1


                    if count > junkspersecond:
                        #print('Junkcount: ',self.junkcount)
                        self.SigIncrementCurTime.emit(self.junkcount)
                        #print(count, '   ', datetime.now())
                        count = 0
                        #self.mutex.lock()
                        gain = self.get_gain()
                        #print(f"diagnostic: gain in worker: {gain}")
                        self.set_data(data)
                        #self.mutex.unlock()
                else:
                    #print("Pause, do not do anything")
                    time.sleep(0.1)
                    if self.stopix is True:
                        break
            else:
                if not self.get_pause():
                    #print("test reached")
                    if format[2] == 16 or format[2] == 32:
                        size = self.fileHandle.readinto(data)
                    elif format[2] == 24:
                        data = self.read24(format,data,self.fileHandle)
                        size = len(data)
                    #print(f"size read: {size}")
                    #print(data[1:10])
                    #size = fileHandle.readinto(data)
                    time.sleep(0.0001)
                    #  read next 2048 bytes
                    count += 1
                    if count > junkspersecond and size > 0:
                        #print('timeincrement reached')
                        self.SigIncrementCurTime.emit(self.junkcount)
                        #print (count, '   ',datetime.now())
                        gain = self.get_gain()
                        #print(f"diagnostic: gain in worker: {gain}")
                        #print(f"maximum: {np.max(data)}")
                        #self.set_data(gain*data)
                        self.set_data(data)
                        count = 0
                else:
                    time.sleep(1)
                    if self.stopix is True:
                        break
        self.set_fileclose(True)
        self.fileHandle.close()
        #self.set_fileclose(True)



    def jump_to_position(self, file, position, chunk_offset):

        if file == self.playfile:
            self.segment_jump = False
            position = int(position)
            self.junkcount = position + chunk_offset
            self.fileHandle.seek(216 + position * self.JUNKSIZE, 0)
            print('same File: Position: ',self.junkcount)

        else:
            self.segment_jump = True
            self.playfile = file
            self.segment_jumpposition = position
            self.junkcount = chunk_offset
            print('Jump Position: ', position,'   Jump Offset= ', chunk_offset)





        #0self.set_pause(True)
        #
        #self.fileHandle.close()
        #self.fileHandle = open(file, 'rb')
        #
        #self.SigNextfile.emit(file)
        #self.set_actual_file(file)
        #self.sq_file = file
        #
        #

        #time.sleep(0.5)
        #self.set_pause(False)



    def stop_loop(self):
        self.stopix = True

    def read24(self,format,data,filehandle):
       for lauf in range(0,self.DATABLOCKSIZE):
        d = filehandle.read(3)
        if d == None:
            data = []
        else:
            dataraw = unpack('<%ul' % 1 ,d + (b'\x00' if d[2] < 128 else b'\xff'))
            #formatlist: [formattag blockalign bitpsample]
            if format[0] == 1:
                data[lauf] = np.float32(dataraw[0]/8388608)
            else:
                data[lauf] = dataraw[0]
        return data
       


"""

SDR = SDR_control()
dev = SDR.identify()

filenames = ['D:\\AM3_onefile_0.wav']
HostAdress = "192.168.178.73"

fileparam = WAVheader_tools().get_sdruno_header(filenames[0])

SDR.set_ifreq(int(fileparam["centerfreq"]))
SDR.set_HostAddress(HostAdress)
SDR.set_irate(int(fileparam["nSamplesPerSec"]))
SDR.set_icorr(0)
SDR.set_rates(dev['rates'])
SDR.set_LO_offset(0)

SDR.set_play()

sdr_ok = SDR.sdrserverstart()
config_ok = SDR.config_socket()

PLW = playrec_worker(SDR)

PLW.set_filename(filenames)
PLW.set_timescaler(156250)
PLW.set_TEST(False)
PLW.set_pause(False)
PLW.set_gain(1)
PLW.set_formattag([1, 0, 16])

PLW.play_loop_filelist()

plw_ret = PLW.get_fileclose()

"""