# Changelog

## Version 2.0.0

- The argument `unhandled_extensions` has been removed from `dump`, `dumps`, `load` and `loads`. The current behavior is to always raise an exception when the compression protocol is unknown.