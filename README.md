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

