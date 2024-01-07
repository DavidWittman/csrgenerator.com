import pytest
import OpenSSL.crypto
from csr import CsrGenerator


class TestGeneration:
    @pytest.fixture
    def csr_info(self):
        return {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'OU': 'Marketing',
            'CN': 'example.com'
        }

    def test_keypair_type(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert isinstance(csr.keypair, OpenSSL.crypto.PKey)

    def test_keypair_bits_default(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert csr.keypair.bits() == 2048

    def test_keypair_1024_bits(self, csr_info):
        csr_info['keySize'] = 1024
        csr = CsrGenerator(csr_info)
        assert csr.keypair.bits() == 1024

    def test_keypair_4096_bits(self, csr_info):
        csr_info['keySize'] = 4096
        csr = CsrGenerator(csr_info)
        assert csr.keypair.bits() == 4096

    def test_csr_length(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert len(csr.csr) == 1106

    def test_csr_starts_with(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert csr.csr.startswith(b'-----BEGIN CERTIFICATE REQUEST-----')

    def test_csr_ends_with(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert csr.csr.endswith(b'-----END CERTIFICATE REQUEST-----\n')

    def test_private_key_starts_with(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert (
                csr.private_key.startswith(b'-----BEGIN RSA PRIVATE KEY-----') or
                csr.private_key.startswith(b'-----BEGIN PRIVATE KEY-----')
        )

    def test_private_key_ends_with(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert (
                csr.private_key.endswith(b'-----END RSA PRIVATE KEY-----\n') or
                csr.private_key.endswith(b'-----END PRIVATE KEY-----\n')
        )

    def test_subject_alt_names(self, csr_info):
        csr_info['subjectAltNames'] = "www.example.com,*.example.com"
        csr = CsrGenerator(csr_info)
        assert sorted(csr.subjectAltNames) == sorted(["DNS:example.com", "DNS:www.example.com", "DNS:*.example.com"])

    def test_default_subject_alt_name(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert csr.subjectAltNames == ["DNS:example.com", "DNS:www.example.com"]


class TestException:
    def test_missing_country(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_empty_country(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': '',
            'ST': 'Texas',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_state(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': 'US',
            'L': 'San Antonio',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_locality(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'O': 'Big Bob\'s Beepers',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_organization(self):
        "This should _not_ raise any exceptions"
        csr_info = {
            'C': 'US',
            'ST': 'Texas',
            'L': 'San Antonio',
            'CN': 'example.com'
        }
        CsrGenerator(csr_info)

    def test_missing_common_name(self):
        with pytest.raises(KeyError):
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

    def test_zero_key_size(self):
        with pytest.raises(KeyError):
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

    def test_invalid_key_size(self):
        with pytest.raises(ValueError):
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
