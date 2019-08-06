from __future__ import absolute_import
import os
import logging
import time

from pathlib import Path
from flask import Flask, request, render_template, abort, send_from_directory
import OpenSSL.crypto as crypt
from werkzeug.utils import html

from csr import CsrGenerator
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
import hashlib
import binascii

app = Flask(__name__)
base_directory = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(filename=base_directory + '/logs/enrolment.log', format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)
# app.config['P12_PATH'] = base_directory + '/p12'
user_errors = []
server_errors = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_csr():
    """
    Receive form data and generate csr and private key.
    """
    csr = CsrGenerator(request.form)
    nic_id = request.form['CN']
    password = request.form['password']
    org_id = request.form['org_id']
    user_directory = generate_hash(nic_id, org_id)[:12]
    generate_pem(nic_id, user_directory, password, csr.csr)
    generate_p12(nic_id, user_directory, password, csr.private_key)

    file_url = '/certificate' + base_directory + '/downloads/' + user_directory + '/' + nic_id + '.p12'
    return render_template('success.html', url=file_url)


def generate_pem(nic_id: str, user_directory: str, password: str, csr: str):
    """
    Download pem file to the specified user directory
    :param nic_id: NIC handle specified by the user.
    :param user_directory: the name of the directory generated for the user.
    :param password: the password of the user
    :param csr: generated csr
    """
    global browser
    downloads = base_directory + '/downloads/' + user_directory

    try:
        os.mkdir(downloads)

    except FileExistsError:
        pass

    except OSError as error:
        print(error)
        server_errors.append(error)
        logger.error('Unable to create path: %s -- %s', error, nic_id)

    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', downloads)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/x-pem-file')

    try:
        browser = webdriver.Firefox(executable_path=base_directory + '/geckodriver', options=options,
                                    firefox_profile=profile, log_path=base_directory + '/logs/geckodriver.log')
    except WebDriverException as error:
        logger.error("Unable to launch chrome driver: %s -- NIC Handle: %s", error, nic_id)
        server_errors.append(error)
        abort(500)

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

    downloaded_pem_path = Path(downloads + '/' + nic_id + '.pem')
    time_to_wait = 30
    time_counter = 0
    while not os.path.exists(downloaded_pem_path):
        time.sleep(1)
        time_counter += 1
        if time_counter > time_to_wait:
            break

    if downloaded_pem_path.exists() and downloaded_pem_path.is_file():
        browser.close()
        browser.quit()

    else:
        try:
            element = WebDriverWait(browser, 30).until(expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'iceMsgsError')))
            error_msg = element.text
            browser.implicitly_wait(3)
            browser.close()
            browser.quit()

            if error_msg not in user_errors:
                user_errors.append(error_msg)
            print(user_errors)

        except TimeoutException as error:
            print(error)
            logger.error('Unable to retrieve error. Operation timeout: %s --NIC Handle: %s', error, nic_id)
            server_errors.append(error)

        except NoSuchElementException as error:
            print(error)
            logger.error('Unable to retrieve error message: %s --NIC Handle: %s', error, nic_id)
            server_errors.append(error)

    if user_errors:
        abort(412)

    if server_errors:
        abort(500)


def generate_p12(nic_id: str, user_directory: str, password: str, private_key: str):
    """
    Generate PKCS12 (p12) file and save to directory created for the user for this session
    :param nic_id: NIC handle of the user
    :param user_directory: the directory generated for the user for this session
    :param password: password of the user
    :param private_key: private key generated by generate_csr function
    :return:
    """
    global pfx_data
    download_path = base_directory + '/downloads/' + user_directory
    pem_file = download_path + '/' + nic_id + '.pem'
    output = download_path + '/' + nic_id + '.p12'

    try:
        with open(pem_file, 'rb') as pem_file:
            pem_buffer = pem_file.read()
            pem = crypt.load_certificate(crypt.FILETYPE_PEM, pem_buffer)

    except IOError as error:
        print('Could not read pem file. Make sure file exists and you have the right permission. ', error)
        logger.error('Could not read pem file. Make sure file exists and you have the right permission: %s '
                     '-- NIC Handle: %s', error, nic_id)
        server_errors.append(error)
        abort(500)

    try:
        private_key = crypt.load_privatekey(crypt.FILETYPE_PEM, private_key)
        pfx = crypt.PKCS12Type()
        pfx.set_privatekey(private_key)

        try:
            pfx.set_certificate(pem)
            pfx_data = pfx.export(password)

        except crypt.Error as error:
            print('An unexpected error occurred', error)
            logger.error('An unexpected error occurred: %s -- NIC Handle: %s', error, nic_id)
            server_errors.append(error)
            abort(500)

        try:
            with open(output, 'wb') as p12_file:
                p12_file.write(pfx_data)

        except IOError as error:
            print('Unable to write p12 file ', error)
            logger.error('Unable to write p12 file: %s --NIC Handle: %s', error, nic_id)
            server_errors.append(error)
            abort(500)

    except UnboundLocalError as error:
        print('Pem file not created:', error)
        logger.error('Pem file not created: %s --NIC Handle: %s', error, nic_id)
        server_errors.append(error)
        abort(500)

    except crypt.Error as error:
        print('An unexpected error occurred while generating p12 file:', error)
        logger.error('An unexpected error occurred while generating p12 file: %s --NIC Handle: %s', error, nic_id)
        server_errors.append(error)
        abort(500)


@app.route('/certificate/<path:file_path>')
def get_certificate(file_path):
    """
    send the PKCS12 (p12) file to the user
    :param file_path: the path of the p12 file
    :return: the p12 file
    """
    try:
        path_arr = file_path.split('/')
        file_name = path_arr[-1]
        file_directory = '/' + '/'.join(path_arr[:len(path_arr) - 1])
        return send_from_directory(file_directory, filename=file_name, as_attachment=True)

    except FileNotFoundError:
        abort(404)


def generate_hash(nic_id, org_id):
    """Generate base_directory name from hash of nic handle and org handle"""
    nic_org = nic_id + org_id
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    dir_hash = hashlib.pbkdf2_hmac('sha512', nic_org.encode('utf-8'), salt, 100000)
    dir_hash = binascii.hexlify(dir_hash)
    return (salt + dir_hash).decode('ascii')


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle HTTP 404 exceptions (Page not found)
    :param e: event
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """
    Handle HTTP 500 exception (Server Error). We raise this error when something happens on the server and we
    add it to the server_errors list.
    :param e: event
    """
    return render_template('server_error.html'), 500


@app.errorhandler(412)
def user_error(e):
    """
    Handle HTTP 412 exception. We raise this when pem file was not downloaded
    :param e: event
    """
    # return render_template('user_error.html'), 412
    return render_template('user_error.html', user_errors=user_errors)


@app.errorhandler(405)
def method_not_allowed(e):
    """
    Handle HTTP 405 exception. We raise this when user tries to access a URL via a method we haven't allowed.
    For example when a user sends a GET request to a URL that accepts only POST requests.
    :param e: event
    """
    return render_template('405.html')


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)
