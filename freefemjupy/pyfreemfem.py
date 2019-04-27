import os
import re
import tempfile
import subprocess
from PIL import Image

from distutils.spawn import find_executable


class pyfreefem:

    OUTPUT_CODE_REGEX = r"[\d]+ :.*"

    def __init__(self, freefem_binary=None, output_encoding='utf-8', mpi = False, cores = 2):
        self.freefem_binary = freefem_binary
        self.mpi = mpi
        self.cores = cores
        if self.freefem_binary == None:
            self.freefem_binary = self.locate_binary()

        if not os.path.exists(self.freefem_binary):
            raise Exception(
                'Fatal error', '{} does not exists'.format(self.freefem_binary))

        self.custom_args = {}

        # TODO: Windows need a different encoding?
        self.output_encoding = output_encoding

        self.set_arguments('v', 0)

    # This function help to find the correct path for freefem
    def locate_binary(self):
        if self.mpi:
            tmp_binary = find_executable('FreeFem++-mpi')
        else: 
            tmp_binary = find_executable('FreeFem++')

        if tmp_binary == None:
            raise Exception('Installation', 'FreeFem++ is not installed')

        return tmp_binary

    # Set arguments for sending to FreeFem++ compiler
    def set_arguments(self, key, value):
        self.custom_args[key] = value

    # Clear all arguments.
    def clear_arguments(self):
        self.custom_args = {}

    # Execute a string as FreeFem
    def execute(self, src):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(src.encode(self.output_encoding))
        tmp.seek(0)
        tmp.close()

        output = self.execute_file(tmp.name)

        os.unlink(tmp.name)

        return output

    
    def preprocess_line(self, line):
        line = line.rstrip()

        if re.match(r"plot\(.*ps=\)", line):
            return line
        if re.match(r"(plot\(.*)\);", line):
            tmp = tempfile.NamedTemporaryFile(delete=False)
            tmp.close()
            self.runtime_graphics.append(tmp.name)

            return re.sub(r"(plot\(.*)\);", "\\1,ps=\"" + re.escape(tmp.name) + "\");", line)

        return line

    # Preporcess edp file for generating images.
    def preprocess_edp(self, path):
        edp_code = open(path, 'r')
        formatted_code = "\n".join(list(map(self.preprocess_line, edp_code.readlines())))
        edp_code.close()

        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(formatted_code.encode(self.output_encoding))
        tmp.close()

        return tmp.name


    # Preprocess post script for processing images easily.
    def process_postscript(self, file):
        statinfo = os.stat(file)
        if statinfo.st_size == 0:
            return None

        img = Image.open(file)

        os.unlink(file)
        return img

    # Execute a file with FreeFem++
    def execute_file(self, path):
        if not os.path.exists(path):
            raise Exception('Execution', 'Given file could not be execute')

        execution = []

        if self.mpi:
            mpi_binary = find_executable('mpirun')
            if mpi_binary == None:
                raise Exception('MPI not available')

            execution.append(mpi_binary)
            execution.append('-np')
            execution.append(str(self.cores))
            
        execution.append(self.freefem_binary)

        for key, value in self.custom_args.items():
            execution.append('-{}'.format(key))
            execution.append(str(value))

        self.runtime_graphics = []

        tmpedp = self.preprocess_edp(path)
        execution.append(tmpedp)
        execution.append('-ng') # No graphics window.

        args = tuple(execution)

        
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()

        os.unlink(tmpedp)

        graphics = list(map(self.process_postscript, self.runtime_graphics))

        return {'output': output.decode(self.output_encoding, "ignore"), 'graphics': graphics}