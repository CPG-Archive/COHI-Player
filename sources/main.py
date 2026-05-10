
from cohi_playrecworker import *
from basic_params import basic_params

from COHI_player_UI import *
import subprocess
import logging

from datetime import datetime
import datetime as ndatetime
from auxiliaries import auxiliaries as auxi, RPListener
import os
import threading
from datetime import datetime


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
        self.running = True

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

        self.reftime = datetime.now()



    @pyqtSlot()

    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        while self.running:
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

            print("Thread beendet.")




class MainWindow(QMainWindow):

    __slots__ = ["filename", "timescaler", "TEST", "pause", "fileHandle", "data", "gain", "formattag", "datablocksize",
                 "fileclose", "configparameters", "actual_file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        logging.getLogger().setLevel(logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        # Create handlers
        warning_handler = logging.StreamHandler()
        debug_handler = logging.FileHandler("system_log.log")
        warning_handler.setLevel(logging.WARNING)
        debug_handler.setLevel(logging.DEBUG)
        # Create formatters and add it to handlers
        warning_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        debug_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        warning_handler.setFormatter(warning_format)
        debug_handler.setFormatter(debug_format)
        # Add handlers to the logger
        self.logger.addHandler(warning_handler)
        self.logger.addHandler(debug_handler)
        self.logger.debug('Init logger in playrec  reached')




        self.basic_data = basic_params()

        self.basic_data.read_yaml()
        self.basic_data.read_filelist()

        self.JUNKSIZE = 2048*4                  # TODO: globale Variable
        self.timescaler = 156250                     # TODO: globale Variable


        # #########################################


        print('STEMLab Address: ',self.basic_data.yaml_address)

        if self.basic_data.fn_list_count == 0:
            print('no WAV Files found, program stopped')
            msg = QMessageBox()
            #msg.setGeometry(QRect(50,50,200,100))
            msg.setIcon(QMessageBox.Critical)
            msg.setText("      FATAL ERROR      ")
            msg.setInformativeText(
                "no WAV Files found, program stopped")
            msg.setWindowTitle("MISSION IMPOSSIBLE")
            msg.exec_()
            exit(0)


        print(self.basic_data.fn_list_count,' WAV Files: ',self.basic_data.fn_list)


        self.fn_pointer = 0
        self.slider_update_stop_count = 1

        self.counter = 0

        self.win = Ui_MainWindow()
        self.win.setupUi(self)

        self.win.pushButton_prev.setShortcut('p')
        self.win.pushButton_prev.pressed.connect(self.pushButton_previous_pressed)
        self.win.pushButton_restart.setShortcut('r')
        self.win.pushButton_restart.pressed.connect(self.pushButton_restart_pressed)
        self.win.pushButton_next.setShortcut('n')
        self.win.pushButton_next.pressed.connect(self.pushButton_next_pressed)
        self.win.pushButton_pause.setShortcut('x')
        self.win.pushButton_pause.pressed.connect(self.pushButton_pause_pressed)
        self.win.pushButton_cont.setShortcut('c')
        self.win.pushButton_cont.pressed.connect(self.pushButton_continue_pressed)
        self.win.pushButton_shutdown.setShortcut('S')
        self.win.pushButton_shutdown.pressed.connect(self.pushButton_shutdown_pressed)

        self.win.ScrollBar_playtime.sliderReleased.connect(self.jump_to_position)
        self.win.ScrollBar_playtime.sliderPressed.connect(self.disable_slider_update)

        self.win.playing_wav.setText('Connecting STEMLab...')


        self.threadpool = QThreadPool()

        self.show()


        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())


        self.worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function

        self.worker.signals.result.connect(self.print_output)
        self.worker.signals.finished.connect(self.thread_complete)
        self.worker.signals.progress.connect(self.progress_fn)
        self.worker.signals.error.connect(self.progress_fn)


        # Execute
        self.threadpool.start(self.worker)




    def progress_fn(self, n):
        print("%d%% done" % n)

    def timing_fn(self,n):

        # ts = self.fileparam
        sq_list = self.basic_data.sq_list[self.fn_pointer]
        total_stop_cs = sq_list[len(sq_list)-1]['stop_cs']

        if n == 0:
            self.reftime= datetime.now()

        junkspersecond = self.timescaler / self.JUNKSIZE * 32

        playtime = datetime.fromtimestamp(int(n / junkspersecond) + 23 * 60 * 60)
        #print(playtime)
        playtime_str = playtime.strftime('%H:%M:%S')

        #print('Playtime: ', playtime_str,      'Timer: ', datetime.now() - self.reftime)
        self.win.play_time.setText('current position: ' + playtime_str)


        #print('Total Time: ', ts['true_datachunksize'] / (junkspersecond * self.JUNKSIZE))

        playprogress = n / total_stop_cs * self.JUNKSIZE


        #print(ts['stoptime_dt'] - ts['starttime_dt'])
        #print(ts['nSamplesPerSec'])
        #print(ts['nChannels'] * ts['nBitsPerSample']))
        #print((ts['filesize'] - 208) / ts['nSamplesPerSec'] )
        #print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')

        if self.slider_update and playprogress > 0:
            #print('Progress: ', playprogress)
            if self.slider_update_stop_count == 0:
                self.win.ScrollBar_playtime.setProperty("value", int(playprogress * 1000))
            else:
                self.slider_update_stop_count = self.slider_update_stop_count - 1

    def jump_to_position(self):

        # ts = self.fileparam
        sq_list = self.basic_data.sq_list[self.fn_pointer]
        total_stop_cs = sq_list[len(sq_list)-1]['stop_cs']


        rel_position = self.win.ScrollBar_playtime.value()
        #print('rel. Position: ',rel_position)
        abs_position = int(rel_position / 1000 * total_stop_cs / self.JUNKSIZE)
        max_position = int(total_stop_cs / self.JUNKSIZE)



        for ix,segment in enumerate(sq_list):
            if  abs_position >= segment['start_cs']/self.JUNKSIZE and abs_position < segment['stop_cs']/self.JUNKSIZE:
                print('abs. Position: ', abs_position, '   File ', segment['segment_file'], '    ', int(segment['start_cs']/self.JUNKSIZE), '   %: ',abs_position/max_position,'      ',ix)
                break

        segment_progress = int(abs_position - segment['start_cs'] / (segment['stop_cs'] - segment['start_cs']))
        print('max. Position: ', max_position, '    rel. Position: ', int(abs_position-segment['start_cs']/self.JUNKSIZE), '     Offset: ', int(segment['start_cs']/self.JUNKSIZE), '       %:',segment_progress)

        self.slider_update = True
        self.slider_update_stop_count = 1
        self.PLW.jump_to_position(segment['segment_file'],int(abs_position-segment['start_cs']/self.JUNKSIZE),int(segment['start_cs']/self.JUNKSIZE))


    def disable_slider_update(self):
        self.slider_update = False


    def errorhandler(self,value):
        """handles errors when methods return errormessages on errorstate == True
        (1) displays errormessage conveyed in 'value' and writes error to logfile
        (2) if 'value' contains the keyword 'ERRORSP' at the initial position, some special actions are performed

        :param value: error description which is to be displayed in the errormessage
        :type value: str
        """
        self.logger.error(str(value))
        try:
            self.logger.error(str(value))
            auxi.standard_errorbox(str(value))
            exit(0)
        except:
            if str(value) == "None":
                value = "unknown error, maybe the internet connection was required and could not be established. Please check."
            auxi.standard_errorbox(str(value))
            self.logger.error(str(value))
            self.cb_Butt_STOP()

    def execute_this_fn(self, progress_callback):

        HostAdress = self.basic_data.yaml_address

        self.SDR = SDR_control()

        if HostAdress != '0.0.0.0':                 # valid address in config
            self.SDR.set_HostAddress(HostAdress)
            #self.win.playing_wav.setText('Pinging STEMLab...')
            msg = 'Pinging STEMLab IP: ' + HostAdress + ' ...'
            self.win.playing_wav.setText(msg)
            time.sleep(2)

            if not self.SDR.ping_RP():              # ping to this address fail
                print('STEMlab ping failed: '+ HostAdress + ' new search needed...' )
                RP_id = self.SDR.search_RP()        # search for RP
                if len(RP_id) != 0:                 # RP found
                    adr = RP_id[0][1]
                    print('STEMlab found: ')
                    print(RP_id)
                    self.basic_data.yaml_address = adr
                    msg = 'STEMlab found, IP: ' + adr
                    self.win.playing_wav.setText(msg)
                    time.sleep(2)
                    self.basic_data.write_yaml_adr()
                else:                               # RP not found
                    msg = 'Fatal Error - no STEMlab found'
                    self.win.playing_wav.setText(msg)
                    time.sleep(5)

                    return
        else:                                       # no valid address in config
            self.win.playing_wav.setText('Searching for STEMLab...')
            RP_id = self.SDR.search_RP()            # search for RP
            if len(RP_id) != 0:                     # RP found
                adr = RP_id[0][1]
                print('STEMlab found: ')
                print(RP_id)
                self.basic_data.yaml_address = adr
                msg = 'STEMlab found, IP: ' + adr
                self.win.playing_wav.setText(msg)
                time.sleep(2)
                self.basic_data.write_yaml_adr()
            else:                                   # RP not found
                msg = 'Fatal Error - no STEMlab found'
                self.win.playing_wav.setText(msg)
                time.sleep(5)

                return

        time.sleep(2)
        dev = self.SDR.identify()


        while True:

            print('start play loop')

            filenames = self.basic_data.sq_list[self.fn_pointer]
            HostAdress = self.basic_data.yaml_address

            print('Files:' + str(filenames) + '   fn_index: ' + str(self.fn_pointer))

            self.slider_update = True

            self.fileparam = WAVheader_tools().get_sdruno_header(filenames[0]['segment_file'])
            #print(fileparam)
            self.SDR.set_ifreq(int(self.fileparam["centerfreq"]))
            self.SDR.set_HostAddress(HostAdress)
            self.SDR.set_irate(int(self.fileparam["nSamplesPerSec"]))
            self.SDR.set_icorr(0)
            self.SDR.set_rates(dev['rates'])
            self.SDR.set_LO_offset(0)

            self.SDR.set_play()

            self.SDR.SigError.connect(self.errorhandler)


            sdr_ok = self.SDR.sdrserverstart()

            if sdr_ok[0] == False:
                time.sleep(10)
                self.worker.running = False
                self.woker.join()

            config_ok = self.SDR.config_socket()

            #TODO: Fehlerbehandlung ergänzen

            self.PLW = playrec_worker(self.SDR)

            self.PLW.set_filename(filenames)

            self.PLW.set_timescaler(156250)    #TODO: ?????????
            self.PLW.set_TEST(False)
            self.PLW.set_pause(False)
            self.PLW.set_gain(1)
            self.PLW.set_formattag([1, 0, 16])

            self.PLW.SigNextfile.connect(self.print_output)

            self.PLW.SigIncrementCurTime.connect(self.timing_fn)



            self.PLW.play_loop_filelist()
            print('stop play Loop')
            plw_ret = self.PLW.get_fileclose()
            print(self.fn_pointer)

            if self.fn_pointer < self.basic_data.fn_list_count - 1:
                self.fn_pointer = self.fn_pointer + 1
            else:
                self.fn_pointer = 0


    def print_output(self, s):

        print('Result Signal: ' + s)
        self.win.playing_wav.setText('playing: ' + s)

        sq_list = self.basic_data.sq_list[self.fn_pointer]
        total_stop_cs = sq_list[len(sq_list) - 1]['stop_cs']
        junkspersecond = self.timescaler / self.JUNKSIZE * 32

        total_time = datetime.fromtimestamp(int(total_stop_cs / (self.timescaler * 32)) + 23 * 60 * 60)
        total_time_str = total_time.strftime('%H:%M:%S')
        print(total_time_str)
        self.win.play_total.setText('total playing time: ' + total_time_str)

    def print_output_total_time(self, s):
        print('Total playing time: ' + s)
        self.win.play_total.setText('Total playing time: ' + s)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def pushButton_next_pressed(self):
        print('next')
        self.PLW.stop_loop()

    def pushButton_previous_pressed(self):
        self.fn_pointer = self.fn_pointer - 2
        if self.fn_pointer < 0: self.fn_pointer = self.basic_data.fn_list_count - 1
        print('prev')
        self.PLW.stop_loop()


    def pushButton_restart_pressed(self):
        print('restart')
        self.fn_pointer = self.fn_pointer - 1
        if self.fn_pointer < 0: self.fn_pointer = self.basic_data.fn_list_count - 1
        self.PLW.stop_loop()


    def pushButton_continue_pressed(self):
        print('cont')
        self.PLW.set_pause(False)

    def pushButton_pause_pressed(self):
        print('pause')
        self.PLW.set_pause(True)

    def pushButton_shutdown_pressed(self):
        print('call SHUTDOWN')
        if self.basic_data.yaml_shutdown:
            self.win.playing_wav.setText('Shutdown RasPi + STEMLab')
            self.PLW.set_pause(True)
            self.SDR.RPShutdown()
            subprocess.call(["shutdown", "-h", "now"])
        else:
            self.win.playing_wav.setText('Shutdown STEMLab')
            self.PLW.set_pause(True)
            self.SDR.RPShutdown()

        self.worker.running = False
        self.woker.join()



    def recurring_timer(self):
        self.counter +=1
        #self.l.setText("Counter: %d" % self.counter)

    def closeEvent(self, event):
        print('kill_all')
        self.PLW.set_pause(True)
        time.sleep(0.1)
        self.worker.running = False
        self.woker.join()


    def start_device_search(self):
        """        self.progress = QProgressDialog(
            "Searching for connected devices,\nplease wait...",
            None,
            0, 0,
            self.win
        )
        self.progress.setWindowModality(Qt.ApplicationModal)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.show()
        self.waitfordevices = True
        """
        self.worker = DeviceSearchWorker()
        self.worker.finished.connect(self.on_search_finished)
        self.worker.start()



    def on_search_finished(self,devicelist):
        """
        Takes action when the search for IP addresses of connected STEMLABs is accomplished:
        generates and displays list of devices found
        if at least one device is found, fills in the first IP address found into the IP address line edit field. Terminates DeviceSearchWorker thread
        and takes over the found address via self.editHostAddress_action()
        :param: devicelist
        :type: list
        :raises: none
        :return: none
        """
        print("on_search_finished: +++++++ Found Red Pitayas:", devicelist)
        if len(devicelist) > 0:
            self.gui.lineEdit_IPAddress.setText(devicelist[0][1])
            auxi.standard_infobox("Address found. If correct, please press 'set IP', else enter correct address manually !")
        else:
            auxi.standard_errorbox("No Red Pitaya found. \nPlease retry once again, because at the first time the auto-search may fail. \n \n If still unsuccessful, check if device is connected or determine and enter the address manually!")
        self.editHostAddress_action()

            # self.gui.lineEdit_IPAddress.setReadOnly(True)
            # self.gui.lineEdit_IPAddress.setEnabled(False)
            # self.gui.pushButton_IP.clicked.connect(self.editHostAddress)
            # self.gui.pushButton_IP.setText("Set IP Address")
            # self.gui.pushButton_IP.adjustSize()

        self.progress.close()
        self.progress.deleteLater()
        self.worker.deleteLater()

class DeviceSearchWorker(QThread):
    finished = pyqtSignal(object)

    def run(self):
        # Simulierter langer Prozess
        #time.sleep(5)
        zeroconf = Zeroconf()
        listener = RPListener()
        browser = ServiceBrowser(zeroconf, "_http._tcp.local.", listener)
        time.sleep(2)  # kurze Wartezeit für Antworten
        zeroconf.close()
        print("Found Red Pitayas:", listener.devices)
        self.finished.emit(listener.devices)



app = QApplication(sys.argv)

win = MainWindow()

app.setQuitOnLastWindowClosed(True)

#win.destroyed.connect(app.quit)

sys.exit(app.exec_())