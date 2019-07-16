

from __future__ import absolute_import
import os

from flask import Flask, request, Response, render_template

from csr import CsrGenerator

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/security')
def security():
    return render_template('security.html')


@app.route('/generate', methods=['POST'])
def generate_csr():
    csr = CsrGenerator(request.form)
    response = '\n'.join([str(csr.csr), str(csr.private_key)])
    return Response(response, mimetype='text/plain')


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port,debug=True)
