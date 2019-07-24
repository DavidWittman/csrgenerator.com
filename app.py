

from __future__ import absolute_import
import os
import logging
import pathlib
from flask import Flask, request, Response, render_template
import OpenSSL.crypto as crypt
from csr import CsrGenerator
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

app = Flask(__name__)
directory = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=directory + '/logs/enrolment.log', format='%(asctime)s - %(message)s')
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
    downloads = directory + '/downloads'
    for file in os.listdir(downloads):
        file_name = os.path.join(downloads, file)
        try:
            if os.path.isfile(file_name):
                os.unlink(file_name)
        except OSError as error:
            print('Unable to delete file:', error)
            logger.error('Unable to delete file: %s', error)

    opts = webdriver.ChromeOptions()
    opts.add_argument('--no-sandbox')
    opts.add_argument('--headless')
    opts.add_argument('--disable-dev-shm-usage')
    log_path = directory + '/logs/chromedriver.log'
    prefs = {'download.default_directory': directory + '/downloads'}
    opts.add_experimental_option("prefs", prefs)

    browser = webdriver.Chrome(directory + '/chromedriver', options=opts, service_args=['--verbose', '--log-directory=' + log_path])
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

    downloaded_pem_path = pathlib.Path(directory + '/downloads/' + nic_id + '.pem')

    if downloaded_pem_path.exists() and downloaded_pem_path.is_file():
        browser.close()
        browser.quit()

    else:
        try:
            element = WebDriverWait(browser, 15).until(expected_conditions.presence_of_element_located((By.CLASS_NAME, 'iceMsgsError')))
            error_msg = element.text
            browser.close()
            browser.quit()

            if error_msg:
                return Response(error_msg, mimetype='text/plain')

        except TimeoutException as error:
            print(error)
            logger.error('Unable to retrieve error. Operation timeout: %s', error)

        except NoSuchElementException as error:
            print(error)
            logger.error('Unable to retrieve error message: %s', error)

            return Response(error, mimetype='text/plain')


def generate_p12(nic_id, password, private_key):
    download_path = directory + '/downloads'
    pem_file = download_path + '/' + nic_id + '.pem'
    output = download_path + '/' + nic_id + '.p12'

    try:
        with open(pem_file, 'rb') as pem_file:
            pem_buffer = pem_file.read()
            pem = crypt.load_certificate(crypt.FILETYPE_PEM, pem_buffer)

    except IOError as error:
        print('Could not read pem file. Make sure file exists and you have the right permission. ', error)
        logger.error('Could not read pem file. Make sure file exists and you have the right permission: %s', error)

    try:
        private_key = crypt.load_privatekey(crypt.FILETYPE_PEM, private_key)
        pfx = crypt.PKCS12Type()
        pfx.set_privatekey(private_key)

        try:
            pfx.set_certificate(pem)
            pfx_data = pfx.export(password)

        except crypt.Error as error:
            print('An unexpected error occurred', error)
            logger.error('An unexpected error occurred: %s', error)

        try:
            with open(output, 'wb') as p12_file:
                p12_file.write(pfx_data)

        except IOError as error:
            print('Unable to write p12 file ', error)
            logger.error('Unable to write p12 file: %s', error)

    except UnboundLocalError as error:
        print('Pem file not created:', error)
        logger.error('Pem file not created: %s', error)

    except crypt.Error as error:
        print('An unexpected error occurred while generating p12 file:', error)
        logger.error('An unexpected error occurred while generating p12 file: %s', error)


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)
