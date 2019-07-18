#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
 csr.py
 CSR Generator for csrgenerator.com

 Copyright (c) 2016 David Wittman <david@wittman.com>

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

from __future__ import absolute_import
import OpenSSL.crypto as crypt


class CsrGenerator(object):
    DIGEST = "sha256"
    SUPPORTED_KEYSIZES = (1024, 2048, 4096)
    DEFAULT_KEYSIZE = 2048

    def __init__(self, form_values):
        # TODO(dw): Better docstrings, rename form_values
        self.csr_info = self._validate(form_values)
        key_size = self.csr_info.pop('keySize')
        self.keypair = self.generate_rsa_keypair(key_size)

    def _validate(self, form_values):
        valid = {}
        fields = ('C', 'ST', 'L', 'O', 'OU', 'CN', 'keySize')
        optional = ('OU', 'keySize')

        for field in fields:
            try:
                # Check for keys with empty values
                if form_values[field] == "":
                    raise KeyError("%s cannot be empty" % field)
                valid[field] = form_values[field]
            except KeyError:
                if field not in optional:
                    raise

        try:
            valid['keySize'] = int(valid.get('keySize', self.DEFAULT_KEYSIZE))
        except:
            raise ValueError("RSA key size must be an integer")

        return valid

    def generate_rsa_keypair(self, bits):
        """
        Generates a public/private RSA keypair of length bits.
        """

        if bits not in self.SUPPORTED_KEYSIZES:
            raise KeyError("Only 2048 and 4096-bit RSA keys are supported")

        key = crypt.PKey()
        key.generate_key(crypt.TYPE_RSA, bits)

        return key

    @property
    def private_key(self):
        return crypt.dump_privatekey(crypt.FILETYPE_PEM, self.keypair)

    @property
    def csr(self):
        request = crypt.X509Req()
        subject = request.get_subject()

        for (k, v) in self.csr_info.items():
            setattr(subject, k, v)

        request.set_pubkey(self.keypair)
        request.sign(self.keypair, self.DIGEST)
        return crypt.dump_certificate_request(crypt.FILETYPE_PEM, request)
