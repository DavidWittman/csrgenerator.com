

from __future__ import absolute_import
import os
import logging
from flask import Flask, request, Response, render_template
import OpenSSL.crypto as crypt
from csr import CsrGenerator
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

app = Flask(__name__)
path = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=path + '/logs/enrolment.log', format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


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
    nic_id = request.form['CN']
    password = request.form['password']
    generate_pem(nic_id, password, csr.csr)
    generate_p12(nic_id, password, csr.private_key)
    return Response(response, mimetype='text/plain')


def generate_pem(nic_id, password, csr):
    opts = webdriver.ChromeOptions()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--headless')
    opts.add_argument('--disable-dev-shm-usage')
    log_path = path + '/logs/chromedriver.log'

    browser = webdriver.Chrome(path + '/chromedriver', options=opts, service_args=['--verbose', '--log-path=' + log_path])
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
    # browser.quit()


def generate_p12(nic_id, password, private_key):
    working_dir = os.getcwd()
    download_path = working_dir + '/Downloads'
    pem_file = download_path + '/' + nic_id + '.pem'
    output = download_path + '/' + nic_id + '.p12'

    try:
        with open(pem_file, 'rb') as pem_file:
            pem_buffer = pem_file.read()
            pem = crypt.load_certificate(crypt.FILETYPE_PEM, pem_buffer)

    except IOError as error:
        print('Could not read pem file. Make sure file exists and you have the right permission. ', error)

    try:
        private_key = crypt.load_privatekey(crypt.FILETYPE_PEM, private_key)
        pfx = crypt.PKCS12Type()
        pfx.set_privatekey(private_key)
        pfx.set_certificate(pem)
        pfx_data = pfx.export(password)

        try:
            with open(output, 'wb') as p12_file:
                p12_file.write(pfx_data)

        except IOError as error:
            print('Unable to write p12 file ', error)

    except crypt.Error as error:
        print('An unexpected error occurred while generating p12 file ', error)


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)
