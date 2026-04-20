import pytest
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from cryptography.x509.oid import NameOID
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
        assert isinstance(csr.keypair, RSAPrivateKey)

    def test_keypair_bits_default(self, csr_info):
        csr = CsrGenerator(csr_info)
        assert csr.keypair.key_size == 2048

    def test_keypair_1024_bits(self, csr_info):
        csr_info['keySize'] = 1024
        csr = CsrGenerator(csr_info)
        assert csr.keypair.key_size == 1024

    def test_keypair_4096_bits(self, csr_info):
        csr_info['keySize'] = 4096
        csr = CsrGenerator(csr_info)
        assert csr.keypair.key_size == 4096

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

    def test_csr_subject_fields(self, csr_info):
        csr = CsrGenerator(csr_info)
        parsed = x509.load_pem_x509_csr(csr.csr)
        subject = parsed.subject
        assert subject.get_attributes_for_oid(NameOID.COUNTRY_NAME)[0].value == 'US'
        assert subject.get_attributes_for_oid(NameOID.STATE_OR_PROVINCE_NAME)[0].value == 'Texas'
        assert subject.get_attributes_for_oid(NameOID.LOCALITY_NAME)[0].value == 'San Antonio'
        assert subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value == "Big Bob's Beepers"
        assert subject.get_attributes_for_oid(NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value == 'Marketing'
        assert subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == 'example.com'

    def test_csr_san_extension(self, csr_info):
        csr_info['subjectAltNames'] = "www.example.com,*.example.com"
        csr = CsrGenerator(csr_info)
        parsed = x509.load_pem_x509_csr(csr.csr)
        san = parsed.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        dns_names = san.value.get_values_for_type(x509.DNSName)
        assert sorted(dns_names) == sorted(['example.com', 'www.example.com', '*.example.com'])


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
