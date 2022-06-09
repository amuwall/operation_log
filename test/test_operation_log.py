import ipaddress
import time
import unittest

from src.operation_log.operation_log import Operator, OperationLog


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


class OperatorLogTestCase(unittest.TestCase):
    def test_init_normal(self):
        expect_operation_logs = [
            {'operator': Operator(1, 'test'), 'text': '测试', 'category': 1},
            {'operator': Operator(1, 'test'), 'text': '测试', 'category': None},
        ]

        for expect_operation_log in expect_operation_logs:
            start_timestamp = int(time.time())

            actual_operation_log = OperationLog(
                expect_operation_log['operator'],
                expect_operation_log['text'],
                expect_operation_log['category']
            )

            end_timestamp = int(time.time())

            self.assertEqual(actual_operation_log.operator, expect_operation_log['operator'])
            self.assertEqual(actual_operation_log.text, expect_operation_log['text'])
            self.assertEqual(
                actual_operation_log.category,
                expect_operation_log['category'] if expect_operation_log['category'] else 0
            )
            self.assertTrue(start_timestamp <= actual_operation_log.timestamp <= end_timestamp)


if __name__ == '__main__':
    unittest.main()
