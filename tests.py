#!/usr/bin/env python

import unittest

from nose.tools import raises, assert_equal

from csr import CsrGenerator


class GenerationTests(unittest.TestCase):
    def setUp(self):
        self.csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'OU': 'Marketing',
            'CN': 'example.com'
        }

    def test_keypair_type(self):
        import OpenSSL.crypto
        csr = CsrGenerator(self.csr_info)
        self.assertTrue(isinstance(csr.keypair, OpenSSL.crypto.PKey))

    def test_keypair_bits_default(self):
        csr = CsrGenerator(self.csr_info)
        assert_equal(csr.keypair.bits(), 2048)

    def test_keypair_1024_bits(self):
        self.csr_info['keySize'] = 1024
        csr = CsrGenerator(self.csr_info)
        assert_equal(csr.keypair.bits(), 1024)

    def test_keypair_4096_bits(self):
        self.csr_info['keySize'] = 4096
        csr = CsrGenerator(self.csr_info)
        assert_equal(csr.keypair.bits(), 4096)

    def test_csr_length(self):
        csr = CsrGenerator(self.csr_info)
        assert_equal(len(csr.csr), 1029)

    def test_csr_starts_with(self):
        csr = CsrGenerator(self.csr_info)
        self.assertTrue(csr.csr.startswith(b'-----BEGIN CERTIFICATE REQUEST-----'))

    def test_csr_ends_with(self):
        csr = CsrGenerator(self.csr_info)
        self.assertTrue(csr.csr.endswith(b'-----END CERTIFICATE REQUEST-----\n'))

    def test_private_key_starts_with(self):
        csr = CsrGenerator(self.csr_info)
        # The result here can differ based on OpenSSL versions
        self.assertTrue(csr.private_key.startswith(b'-----BEGIN RSA PRIVATE KEY-----') or
                        csr.private_key.startswith(b'-----BEGIN PRIVATE KEY-----'))

    def test_private_key_ends_with(self):
        csr = CsrGenerator(self.csr_info)
        # The result here can differ based on OpenSSL versions
        self.assertTrue(csr.private_key.endswith(b'-----END RSA PRIVATE KEY-----\n') or
                        csr.private_key.endswith(b'-----END PRIVATE KEY-----\n'))


class ExceptionTests(unittest.TestCase):
    def test_missing_country(self):
        csr_info = {
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_empty_country(self):
        csr_info = {
            'C': '',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_state(self):
        csr_info = {
            'C': 'US',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_locality(self):
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_organization(self):
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    @raises(KeyError)
    def test_missing_common_name(self):
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers'
        }
        CsrGenerator(csr_info)

    def test_missing_ou(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_empty_ou(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'OU': '',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    @raises(KeyError)
    def test_zero_key_size(self):
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'OU': 'Marketing',
            'CN': 'example.com',
            'keySize': 0
        }
        CsrGenerator(csr_info)

    @raises(ValueError)
    def test_invalid_key_size(self):
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'OU': 'Marketing',
            'CN': 'example.com',
            'keySize': 'penguins'
        }
        CsrGenerator(csr_info)
