import ipaddress
import unittest

from src.operation_log.operation_log import Operator


class OperatorTestCase(unittest.TestCase):
    def test_init_normal(self):
        expect_operators = [
            {'id': 1, 'name': 'test', 'ip': '127.0.0.1'},
            {'id': 1, 'name': 'test', 'ip': ''},
            {'id': 1, 'name': 'test', 'ip': None},
        ]

        for expect_operator in expect_operators:
            actual_operator = Operator(
                expect_operator['id'],
                expect_operator['name'],
                expect_operator['ip']
            )
            self.assertEqual(actual_operator.id, expect_operator['id'])
            self.assertEqual(actual_operator.name, expect_operator['name'])
            self.assertEqual(actual_operator.ip, expect_operator['ip'] if expect_operator['ip'] else '')

    def test_init_with_invalid_ip(self):
        expect_operator = {'id': 1, 'name': 'test', 'ip': '1'}

        with self.assertRaises(ValueError):
            Operator(
                expect_operator['id'],
                expect_operator['name'],
                expect_operator['ip']
            )


if __name__ == '__main__':
    unittest.main()
