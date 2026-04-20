#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
 csr.py
 CSR Generator for csrgenerator.com

 Copyright (c) 2024 David Wittman <david@wittman.com>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <http://www.gnu.org/licenses/>.

"""

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


class CsrGenerator(object):
    DIGEST = "sha256"
    SUPPORTED_KEYSIZES = (1024, 2048, 4096)
    DEFAULT_KEYSIZE = 2048
    # Map short field names to cryptography NameOID attributes
    _NAME_OID_MAP = {
        'C': NameOID.COUNTRY_NAME,
        'ST': NameOID.STATE_OR_PROVINCE_NAME,
        'L': NameOID.LOCALITY_NAME,
        'O': NameOID.ORGANIZATION_NAME,
        'OU': NameOID.ORGANIZATIONAL_UNIT_NAME,
        'CN': NameOID.COMMON_NAME,
    }

    def __init__(self, form_values):
        self.csr_info = self._validate(form_values)
        key_size = self.csr_info.pop('keySize')

        if 'subjectAltNames' in self.csr_info:
            # The SAN list should contain the CN as well
            # TODO(dw): do list(set())
            sans = f"{self.csr_info['CN']},{self.csr_info.pop('subjectAltNames')}"
        else:
            sans = self.csr_info['CN']
            if sans.count('.') == 1:
                # root domain, add www. as well
                sans += ",www.{}".format(sans)

        self.subjectAltNames = list(map(lambda d: "DNS:{}".format(d.strip()), sans.split(',')))

        self.keypair = self.generate_rsa_keypair(key_size)

    def _validate(self, form_values):
        valid = {}
        fields = ('C', 'ST', 'L', 'O', 'OU', 'CN', 'keySize', 'subjectAltNames')
        required = ('CN',)

        for field in fields:
            try:
                # Check for keys with empty values
                if form_values[field] == "":
                    raise KeyError("%s cannot be empty" % field)
                valid[field] = form_values[field]
            except KeyError:
                if field in required:
                    raise

        try:
            valid['keySize'] = int(valid.get('keySize', self.DEFAULT_KEYSIZE))
        except ValueError:
            raise ValueError("RSA key size must be an integer")

        return valid

    def generate_rsa_keypair(self, bits):
        """
        Generates a public/private RSA keypair of length bits.
        """

        if bits not in self.SUPPORTED_KEYSIZES:
            raise KeyError("Only 2048 and 4096-bit RSA keys are supported")

        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=bits,
        )

    @property
    def private_key(self):
        return self.keypair.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )

    @property
    def csr(self):
        name_attrs = [
            x509.NameAttribute(self._NAME_OID_MAP[k], v)
            for k, v in self.csr_info.items()
            if k in self._NAME_OID_MAP
        ]

        san_entries = [x509.DNSName(d.removeprefix('DNS:')) for d in self.subjectAltNames]

        builder = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name(name_attrs))
            .add_extension(x509.SubjectAlternativeName(san_entries), critical=False)
        )

        request = builder.sign(self.keypair, hashes.SHA256())
        return request.public_bytes(serialization.Encoding.PEM)
