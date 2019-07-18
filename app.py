

from __future__ import absolute_import
import os

from flask import Flask, request, Response, render_template

from csr import CsrGenerator

from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

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
    response = b'\n'.join([csr.csr, csr.private_key])
    driver = webdriver.Chrome('/home/minty/Documents/GitHub/bpki-enrolment-gui/chromedriver')
    opts = Options()
    opts.set_headless(headless=True)
    browser = Chrome(options=opts)
    browser.get('https://externalra.afrinic.net/externalra-gui/facelet/enroll-csrcert.xhtml')
    org_id = browser.find_element_by_id('org-id')
    password = browser.find_element_by_id('password')
    perm = browser.find_element_by_id('form:j_id71:_1')
    cerfitifcate_form  = browser.find_element_by_id('form:certificateRequest')
    submit = browser.find_element_by_id('form:j_id77')

    return Response(response, mimetype='text/plain')


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port,debug=True)
