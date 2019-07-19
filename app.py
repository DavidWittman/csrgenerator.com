

from __future__ import absolute_import
import os

from flask import Flask, request, Response, render_template

from csr import CsrGenerator

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

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
    key_size = int(request.form['keySize'])
    response = b'\n'.join([csr.csr, csr.private_key])
    nic_id = request.form['CN']
    password = request.form['password']
    csr_pem = response[:key_size]
    generate_pem(nic_id, password, csr.csr)
    return Response(response, mimetype='text/plain')


def generate_pem(nic_id, password, csr):
    opts = Options()
    opts.binary_location = '/home/minty/Documents/GitHub/bpki-enrolment-gui/chromedriver'
    opts.add_argument('--headless')
    browser = webdriver.Chrome('/home/minty/Documents/GitHub/bpki-enrolment-gui/chromedriver')
    browser.get('https://externalra.afrinic.net/externalra-gui/facelet/enroll-csrcert.xhtml')

    pem_checkbox = browser.find_element_by_id('form:j_id71:_1')
    pem_checkbox.click()
    username = browser.find_element_by_id('form:username')
    username.send_keys(nic_id)

    form_password = browser.find_element_by_id('form:secretPassword')
    form_password.send_keys(password)

    certificate_form = browser.find_element_by_id('form:certificateRequest')
    certificate_form.send_keys((Keys.CONTROL + "a"), Keys.DELETE)
    certificate_form.send_keys(csr.decode('utf-8'))

    submit = browser.find_element_by_id('form:j_id77')
    submit.click()

   # browser.close()
    #browser.quit()


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)
