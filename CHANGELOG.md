# Changelog

## Version 2.0.0 - 2021-03-09
### Added
- `BaseCompresser` class and subclasses to handle compression streams.
- `BasePicklerIO` class and subclasses to handle dump and load of python objects.
- Registry of `BaseCompresser` classes with the mappings that relate them to compression names, file extensions and default read and write modes.
- Registry of `BasePicklerIO` classes with the mappings that relate them to pickler names.
- Singledispatch functions `compress_pickle.io.base.compress_and_serialize` and `compress_pickle.io.base.uncompress_and_unserialize` that implement the core input/output functionality.
- `pickler_method` and `pickler_kwargs` arguments for all `dump`, `dumps`, `load` and `loads`. This now enables users to choose the pickler backend.
- Added support for several pickler backends such as `marshal`, `dill` and `cloudpickle`.
- Added the ability for compression methods to support more than one file extension. Now `bz2` and `lzma` also are applied for the `.bz2` and `.xz` extensions respectively.

### Removed
- The `optimize` argument of the `dump` and `dumps` function was removed. To use the same functionality, you should pass the argument `pickler_method="optimized_pickle"` to `dump` and `dumps`.
- The argument `unhandled_extensions` has been removed from `dump`, `dumps`, `load` and `loads`. The current behavior is to always raise an exception when the compression protocol is unknown.
- All functions from the `compress_pickle.utils` module with the exception of `_stringify_path`. All of the logic implemented by the old functions has been refactored into the registries, compressers and picklerIO classes.