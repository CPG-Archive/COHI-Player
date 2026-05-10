import os.path
from auxiliaries import WAVheader_tools
import glob
import yaml
import time
from pathlib import Path


class basic_params():

    def __init__(self, *args, **kwargs):
        #super().__init__()

        # Store constructor arguments (re-used for processing)
        self.config_metadata = None
        self.yaml_error = False
        self.yaml_filepath = list()
        self.yaml_address = ''
        self.yaml_shutdown = False

        self.fn_error = False
        self.fn_list = list()
        self.sq_list = list()
        self.fn_list_count = 0



    def read_yaml(self):
        
        time.sleep(2)

        # get basic configuration

        try:
            stream = open("config_sdr.yaml", "r")  # TODO: doesn't find file ?
            self.config_metadata = yaml.safe_load(stream)
            stream.close()
            self.yaml_error = False

        except:
            print("invalid metadata, check your config_sdr.yaml "
                  "exists")
            self.yaml_error = True

        try:
            self.yaml_filepath.append(self.config_metadata.get("filename"))  # TODO: remove after list test
        except:
            print("invalid filename in config_sdr.yaml")
            self.yaml_error = True

        try:
            self.yaml_filepath.append(self.config_metadata.get("filename2"))  # TODO: remove after list test
        except:
            print("invalid filename2 in config_sdr.yaml")
            self.yaml_error = True

        try:
            self.yaml_address = (self.config_metadata.get("address"))
        except:
            print("invalid address in config_sdr.yaml")
            self.yaml_error = True

        try:
            self.yaml_shutdown = (self.config_metadata.get("shutdown"))
        except:
            print("invalid shutdown information in config_sdr.yaml")
            self.yaml_error = True


        return self.yaml_error


    def write_yaml_adr(self):
        self.config_metadata['address'] = self.yaml_address
        stream = open("config_sdr.yaml", "w")
        yaml.dump(self.config_metadata, stream)
        stream.close()



    def read_filelist(self):


        for lw_inp in self.yaml_filepath:

            filelist_raw = list()

            for wavfile in Path(lw_inp).rglob('*_0.wav'):
                print(f'found WAV files: {wavfile}')
                filelist_raw.append(str(wavfile))

            #lw_dir = os.path.dirname(lw_inp)

            #filelist = sorted(glob.glob(lw_inp))
            filelist = sorted(filelist_raw)

            print(f'found WAV files on drive {lw_inp}: {filelist}')
            #print(f'found WAV files: {filelist}')

            for filename in filelist:
                print(
                    '##################################################################################################')
                print(f"scanning file: {filename}")

                filenames = list()
                sq_list = {}
                filesequenz = list()

                fileparam = WAVheader_tools().get_sdruno_header(filename)


                lw_dir = os.path.dirname(filename)

                if fileparam:
                    filenames.append(filename)
                    print(fileparam)
                    i = 0
                    sq_list['segment_file'] = filename
                    start_cs = 0
                    sq_list['start_cs'] = start_cs
                    stop_cs = fileparam['true_datachunksize']
                    sq_list['stop_cs'] = stop_cs
                    filesequenz.append(sq_list)

                    while '.wav' in fileparam['nextfilename']:
                        nextfilename_clean = fileparam['nextfilename'].rstrip('\x00').strip()
                        newfile = os.path.join(lw_dir, nextfilename_clean)
                        if os.path.exists(newfile):
                            filenames.append(newfile)
                            # print(filenames)
                            fileparam = WAVheader_tools().get_sdruno_header(newfile)
                            i = i + 1
                            #sq_list[0] = newfile
                            start_cs = stop_cs + 1
                            #sq_list[1] = start_cs
                            stop_cs = start_cs + fileparam['true_datachunksize']
                            #sq_list[2] = stop_cs
                            filesequenz.append({'segment_file': newfile,'start_cs': start_cs, 'stop_cs': stop_cs})



                        else:
                            print(f'chained file {newfile} not found')
                            fileparam['nextfilename'] = ''
                    self.fn_list.append(filenames)
                    self.sq_list.append(filesequenz)
                    self.fn_list_count = self.fn_list_count + 1




"""
basic_data = basic_params()

print(basic_data)

basic_data.read_yaml()
print(basic_data.yaml_address)
basic_data.yaml_address = '0.0.0.0'
basic_data.write_yaml_adr()
basic_data.read_yaml()
print(basic_data.yaml_address)

basic_data.read_filelist()

print(basic_data.yaml_address)
print(basic_data.fn_list)
print(basic_data.fn_list_count)
"""

