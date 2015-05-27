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
        csr = CsrGenerator(2048, self.csr_info)
        self.assertTrue(isinstance(csr.keypair, OpenSSL.crypto.PKey))

    def test_keypair_bits(self):
        csr = CsrGenerator(2048, self.csr_info)
        assert_equal(csr.keypair.bits(), 2048)

        csr = CsrGenerator(1024, self.csr_info)
        assert_equal(csr.keypair.bits(), 1024)

    def test_csr_length(self):
        csr = CsrGenerator(2048, self.csr_info)
        assert_equal(len(csr.csr), 1025)

    def test_csr_starts_with(self):
        csr = CsrGenerator(2048, self.csr_info)
        self.assertTrue(csr.csr.startswith('-----BEGIN CERTIFICATE REQUEST-----'))

    def test_csr_ends_with(self):
        csr = CsrGenerator(2048, self.csr_info)
        self.assertTrue(csr.csr.endswith('-----END CERTIFICATE REQUEST-----\n'))

    def test_private_key_starts_with(self):
        csr = CsrGenerator(2048, self.csr_info)
        # The result here can differ based on OpenSSL versions
        self.assertTrue(csr.private_key.startswith('-----BEGIN RSA PRIVATE KEY-----') or
                        csr.private_key.startswith('-----BEGIN PRIVATE KEY-----'))

    def test_private_key_ends_with(self):
        csr = CsrGenerator(2048, self.csr_info)
        # The result here can differ based on OpenSSL versions
        self.assertTrue(csr.private_key.endswith('-----END RSA PRIVATE KEY-----\n') or
                        csr.private_key.endswith('-----END PRIVATE KEY-----\n'))

class ExceptionTests(unittest.TestCase):
    @raises(KeyError)
    def test_missing_country(self):
        csr_info = {
                    'ST': 'Texas',
                    'L': 'San Antonio',
                    'O': 'Big Bob\'s Beepers',
                    'CN': 'example.com'
                   }
        CsrGenerator(2048, csr_info)

    @raises(KeyError)
    def test_missing_state(self):
        csr_info = {
                    'C': 'US',
                    'L': 'San Antonio',
                    'O': 'Big Bob\'s Beepers',
                    'CN': 'example.com'
                   }
        CsrGenerator(2048, csr_info)

    @raises(KeyError)
    def test_missing_locality(self):
        csr_info = {
                    'C': 'US',
                    'ST': 'Texas',
                    'O': 'Big Bob\'s Beepers',
                    'CN': 'example.com'
                   }
        CsrGenerator(2048, csr_info)

    @raises(KeyError)
    def test_missing_organization(self):
        csr_info = {
                    'C': 'US',
                    'ST': 'Texas',
                    'L': 'San Antonio',
                    'CN': 'example.com'
                   }
        CsrGenerator(2048, csr_info)

    @raises(KeyError)
    def test_missing_common_name(self):
        csr_info = {
                    'C': 'US',
                    'ST': 'Texas',
                    'L': 'San Antonio',
                    'O': 'Big Bob\'s Beepers'
                   }
        CsrGenerator(2048, csr_info)
