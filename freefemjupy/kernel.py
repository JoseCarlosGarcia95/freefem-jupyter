#!//usr/bin/python
import base64
from io import BytesIO
from ipykernel.kernelbase import Kernel
from freefemjupy.pyfreemfem import pyfreefem
from matplotlib.pyplot import imshow

class FreeFemJupyter(Kernel):
    implementation = 'FreeFem++'
    implementation_version = '1.0'
    banner = 'FreeFem++ Jupyter'

    language_info = {
        'version': '1.0',
        'name': 'c++',
        'mimetype': 'text/x-freefem',
    }

    name = 'FreeFemJupyter'
    
    ##freefem = pyfreefem(mpi=True, cores=2)
    freefem = pyfreefem()
    keywords = ['plot', 'mesh', 'border']
    """
    Handle jupyter connections.
    """
    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        if not silent:
            
            freefem = self.freefem.execute(code)

            html = freefem['output']#replace("\n", "<br>")      
                    
            display_data = {
                'data' : {'text/plain' : html},
                'metadata' : {},
                'execution_count' : self.execution_count
            }
                    
            self.send_response(self.iopub_socket, 'display_data', display_data)

            for graphic in freefem['graphics']:
                if graphic == None:
                    continue
                buff = BytesIO()
                graphic.save(buff, format="PNG", optimize=True, dpi=(1024, 1024))

                display_data = {
                    'data' : {
                        'image/png' : base64.b64encode(buff.getvalue()).decode()
                    },
                    'metadata' : {
                        'image/png' : {
                            'width': 640,
                            'height': 480
                        }
                    },
                    'execution_count' : self.execution_count
                }

                self.send_response(self.iopub_socket, 'display_data', display_data)


        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=FreeFemJupyter)
