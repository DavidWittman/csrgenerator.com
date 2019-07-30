
from __future__ import absolute_import
import os
import logging
from pathlib import Path
from flask import Flask, request, render_template, send_from_directory, abort, redirect, url_for, jsonify
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
app.config['P12_PATH'] = directory + '/p12'
user_errors = []
server_errors = []


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/security')
def security():
    return render_template('security.html')


@app.route('/generate', methods=['POST'])
def generate_csr():
    nic_id = request.form['CN']

    csr = CsrGenerator(request.form)
    # response = b'\n'.join([csr.csr, csr.private_key])
    # nic_id = request.form['CN']
    password = request.form['password']
    generate_pem(nic_id, password, csr.csr)
    generate_p12(nic_id, password, csr.private_key)

    if user_errors:
        return redirect('/user-error')

    elif server_errors:
        return redirect('/server-error')

    return redirect('/certificate' + nic_id + '.pem')
    # return Response(response, mimetype='text/plain')


def generate_pem(nic_id, password, csr):
    downloads = directory + '/downloads'
    for file in os.listdir(downloads):
        file_name = os.path.join(downloads, file)
        try:
            if os.path.isfile(file_name):
                os.unlink(file_name)
        except OSError as error:
            print('Unable to delete file:', error)
            logger.error('Unable to delete file: %s --NIC Handle: %s', error, nic_id)

    opts = webdriver.ChromeOptions()
    opts.add_argument('--no-sandbox')
    #  opts.add_argument('--headless')
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
    browser.implicitly_wait(5)

    downloaded_pem_path = Path(directory + '/downloads/' + nic_id + '.pem')

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
        # abort(jsonify({'code': 412, 'message': 'You are not authorized to access'}), 412)  # Precondition
        abort(412, jsonify({'code': 412, 'url': '/user-errors', 'errors': user_errors}))
    if server_errors:
        # abort(make_response(jsonify({'code': 500, 'message': 'You are not authorized to access'}), 500))
        # abort(500, 'Server error occurred', server_errors)
        abort(500, jsonify({'code': 500, 'url': '/user-errors', 'errors': user_errors}))


def generate_p12(nic_id, password, private_key):
    download_path = directory + '/downloads'
    pem_file = download_path + '/' + nic_id + '.pem'
    output = directory + '/p12/' + nic_id + '.p12'

    try:
        with open(pem_file, 'rb') as pem_file:
            pem_buffer = pem_file.read()
            pem = crypt.load_certificate(crypt.FILETYPE_PEM, pem_buffer)

    except IOError as error:
        print('Could not read pem file. Make sure file exists and you have the right permission. ', error)
        logger.error('Could not read pem file. Make sure file exists and you have the right permission: %s '
                     '-- NIC Handle: %s', error, nic_id)
        server_errors.append(error)

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

        try:
            with open(output, 'wb') as p12_file:
                p12_file.write(pfx_data)

        except IOError as error:
            print('Unable to write p12 file ', error)
            logger.error('Unable to write p12 file: %s --NIC Handle: %s', error, nic_id)
            server_errors.append(error)

    except UnboundLocalError as error:
        print('Pem file not created:', error)
        logger.error('Pem file not created: %s --NIC Handle: %s', error, nic_id)
        server_errors.append(error)

    except crypt.Error as error:
        print('An unexpected error occurred while generating p12 file:', error)
        logger.error('An unexpected error occurred while generating p12 file: %s --NIC Handle: %s', error, nic_id)
        server_errors.append(error)

    return get_certificate(output)


@app.route('/certificate/<file_name>')
def get_certificate(file_name):

    try:
        request.form['NC']
        return send_from_directory(app.config['P12_PATH'], filename=file_name, as_attachment=True)

    except FileNotFoundError:
        abort(404)

    except KeyError:
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('server_error.html'), 500


@app.errorhandler(412)
def user_error(e):
    # return render_template('user_error.html'), 412
    return render_template('user_error.html', user_errors=user_errors)


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html')


if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)