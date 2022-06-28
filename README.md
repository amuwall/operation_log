# Operation Log

operation_log is used to record operation log for web api.

## Features

1. Non-intrusive to record operation log

## Requirements

1. Python 3.x

## Getting started

1. install operation log

```shell
pip install operation-log 
```

2. use record_operation_log decorator to wrap api function

```python
from operation_log import Operator, record_operation_log


def get_operator() -> Operator:
    return Operator(1, 'test_user')


@record_operation_log(get_operator, 'hello world')
async def hello(request):
    return Response()
```

3. use record_operation_log decorator with context

```python
import typing

from operation_log import Operator, record_operation_log


def get_operator() -> Operator:
    return Operator(1, 'test_user')


def before_execute_context(request) -> typing.Dict:
    return {'msg': 'hello old world'}


def after_execute_context(request) -> typing.Dict:
    return {'msg': 'hello new world'}


@record_operation_log(
    get_operator,
    'hello {{ before_execute.msg }} {{ after_execute.msg }}',
    before_execute_contexts=[before_execute_context],
    after_execute_contexts=[after_execute_context]
)
async def hello(request):
    return Response()
```

The context functions will receive params such as the execute function.

4. custom log writer

```python
import logging

from operation_log import Operator, OperationLogWriter, OperationLog, record_operation_log


def get_operator() -> Operator:
    return Operator(1, 'test_user')


class CustomOperationLogWriter(OperationLogWriter):
    def write(self, operation_log: OperationLog):
        logging.info(f'this is custom log writer {operation_log.text}')


@record_operation_log(
    get_operator,
    'hello world',
    writer=CustomOperationLogWriter()
)
async def hello(request):
    return Response()
```

If you want to save the operation log to the database, you can subclass the `OperationLogWriter` class and implement
your own `write` method.
