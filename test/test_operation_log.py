import logging
import time
import typing
import unittest

from src.operation_log.operation_log import Operator, OperationLog, OperationLogWriter, DefaultOperationLogWriter, \
    OperationFailedError, record_operation_log


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


class DefaultOperationLogWriterTestCase(unittest.TestCase):
    def test_write_normal(self):
        expect_operation_log = OperationLog(Operator(1, 'test', '127.0.0.1'), 'test text', 1)

        writer = DefaultOperationLogWriter()
        with self.assertLogs() as logs:
            writer.write(expect_operation_log)

        self.assertEqual(
            logs.output,
            [
                'INFO:root:'
                f'operator id {expect_operation_log.operator.id} '
                f'operator name {expect_operation_log.operator.name} '
                f'operator ip {expect_operation_log.operator.ip} '
                f'category {expect_operation_log.category} '
                f'text {expect_operation_log.text} '
                f'timestamp {expect_operation_log.timestamp}'
            ]
        )


class OperationFailedErrorTestCase(unittest.TestCase):
    def test_init_normal(self):
        expect_reason = 'operation failed'

        actual_error = OperationFailedError(expect_reason)

        self.assertIsInstance(actual_error, Exception)
        self.assertEqual(actual_error.reason, expect_reason)


class RecordOperationLogTestCase(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def get_test_operator() -> Operator:
        return Operator(1, 'test', '127.0.0.1')

    async def test_record_success_log(self):
        @record_operation_log(self.get_test_operator, 'test op')
        async def test_func():
            logging.info('test_record_success_log')

        with self.assertLogs() as logs:
            await test_func()

        test_operator = self.get_test_operator()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_success_log')
        self.assertIn(
            'INFO:root:'
            f'operator id {test_operator.id} '
            f'operator name {test_operator.name} '
            f'operator ip {test_operator.ip} '
            'category 0 '
            f'text test op '
            f'timestamp ',
            logs.output[1]
        )

    async def test_record_success_log_with_context(self):
        def before_execute_context() -> typing.Dict:
            return {'msg': 'hello old world'}

        def after_execute_context() -> typing.Dict:
            return {'msg': 'hello new world'}

        @record_operation_log(
            self.get_test_operator,
            'test op {{ before_execute.msg }} {{ after_execute.msg }}',
            before_execute_contexts=[before_execute_context],
            after_execute_contexts=[after_execute_context]
        )
        async def test_func():
            logging.info('test_record_success_log_with_context')

        with self.assertLogs() as logs:
            await test_func()

        test_operator = self.get_test_operator()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_success_log_with_context')
        self.assertIn(
            'INFO:root:'
            f'operator id {test_operator.id} '
            f'operator name {test_operator.name} '
            f'operator ip {test_operator.ip} '
            'category 0 '
            f'text test op hello old world hello new world '
            f'timestamp ',
            logs.output[1]
        )

    async def test_record_failed_log(self):
        @record_operation_log(self.get_test_operator, 'test success op', failed_text='test failed op')
        async def test_func():
            logging.info('test_record_failed_log')
            raise OperationFailedError('test failed reason')

        with self.assertLogs() as logs:
            await test_func()

        test_operator = self.get_test_operator()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_failed_log')
        self.assertIn(
            'INFO:root:'
            f'operator id {test_operator.id} '
            f'operator name {test_operator.name} '
            f'operator ip {test_operator.ip} '
            'category 0 '
            f'text test failed op '
            f'timestamp ',
            logs.output[1]
        )

    async def test_record_failed_log_with_context(self):
        def before_execute_context() -> typing.Dict:
            return {'msg': 'hello old world'}

        def after_execute_context() -> typing.Dict:
            return {'msg': 'hello new world'}

        @record_operation_log(
            self.get_test_operator,
            'test op {{ before_execute.msg }} {{ after_execute.msg }}',
            failed_text='test failed op {{ before_execute.msg }} {{ after_execute.msg }} {{ failed_reason }}',
            before_execute_contexts=[before_execute_context],
            after_execute_contexts=[after_execute_context]
        )
        async def test_func():
            logging.info('test_record_failed_log_with_context')
            raise OperationFailedError('test failed reason')

        with self.assertLogs() as logs:
            await test_func()

        test_operator = self.get_test_operator()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_failed_log_with_context')
        self.assertIn(
            'INFO:root:'
            f'operator id {test_operator.id} '
            f'operator name {test_operator.name} '
            f'operator ip {test_operator.ip} '
            'category 0 '
            f'text test failed op hello old world hello new world test failed reason '
            f'timestamp ',
            logs.output[1]
        )

    async def test_record_failed_log_without_failed_text(self):
        @record_operation_log(self.get_test_operator, 'test op')
        async def test_func():
            logging.info('test_record_failed_log_without_failed_text')
            raise OperationFailedError('test failed reason')

        with self.assertLogs() as logs:
            await test_func()

        test_operator = self.get_test_operator()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_failed_log_without_failed_text')
        self.assertIn(
            'INFO:root:'
            f'operator id {test_operator.id} '
            f'operator name {test_operator.name} '
            f'operator ip {test_operator.ip} '
            'category 0 '
            f'text test op '
            f'timestamp ',
            logs.output[1]
        )

    async def test_record_log_with_custom_writer(self):
        class TestOperationLogWriter(OperationLogWriter):
            def write(self, operation_log: OperationLog):
                logging.info(f'this is custom log writer {operation_log.text}')

        test_custom_writer = TestOperationLogWriter()

        @record_operation_log(
            self.get_test_operator,
            'test op',
            writer=test_custom_writer
        )
        async def test_func():
            logging.info('test_record_log_with_custom_writer')

        with self.assertLogs() as logs:
            await test_func()

        self.assertEqual(len(logs.output), 2)
        self.assertEqual(logs.output[0], 'INFO:root:test_record_log_with_custom_writer')
        self.assertEqual(logs.output[1], 'INFO:root:this is custom log writer test op')


if __name__ == '__main__':
    unittest.main()
