#!//usr/bin/python
import base64
from io import BytesIO
from ipykernel.kernelbase import Kernel
from freefemjupy.pyfreemfem import pyfreefem

class FreeFemJupyter(Kernel):
    implementation = 'FreeFem++'
    implementation_version = '1.0'
    banner = 'FreeFem++ Jupyter'

    language_info = {
        'version': '1.0',
        'name': 'FreeFem++',
        'mimetype': 'text/x-freefem',
        'pygments_lexer': 'c',

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

            html = freefem['output'].replace("\n", "<br>")      
                    
            #stream_content = {'name': 'stdout', 'text': html}
            #self.send_response(self.iopub_socket, 'stream', stream_content)
            for graphic in freefem['graphics']:
                buff = BytesIO()
                graphic.save(buff, format="PNG")

                html += "<img src=\"data:image/png;base64,{}\"/>".format(base64.b64encode(buff.getvalue()).decode())

            display_data = {
                'data' : {'text/html' : html},
                'metadata' : {},
                'execution_count' : self.execution_count
            }
                    
            self.send_response(self.iopub_socket, 'execute_result', display_data)

        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }


if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=FreeFemJupyter)
