import unittest

from crypto_funcs import crypto


class testCrypto(unittest.TestCase):
    def testEncrypt(self):
        crypto()
        plaintext = "test"
        password = "test"
        expected = "test"
        result = crypto.decrypt(
            self, crypto.encrypt(self, plaintext, password), password
        )
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
