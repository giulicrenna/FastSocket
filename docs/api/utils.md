# Utils

::: fastsocket.utils.chunks

::: fastsocket.utils.file_transfer

::: fastsocket.utils.framing

::: fastsocket.utils.exceptions

::: fastsocket.utils.logger

## Logger configuration

Since 2.2.0, the logger uses Python's `logging` module internally and is thread-safe by default.

| Method | Description |
|--------|-------------|
| `Logger.print_log_error(msg, instance)` | Log at ERROR level (red) |
| `Logger.print_log_normal(msg, instance)` | Log at INFO level (green) |
| `Logger.print_log_debug(msg)` | Log at DEBUG level (yellow) |
| `Logger.set_level(level)` | Change the minimum level, e.g. `logging.WARNING` to silence debug output |
| `Logger.add_file_handler(path)` | Append plain-text logs to a file (no ANSI codes) |

```python
import logging
from fastsocket import Logger

Logger.set_level(logging.WARNING)          # silence INFO and DEBUG
Logger.add_file_handler("/var/log/app.log")  # also write to file
```

::: fastsocket.utils.types
