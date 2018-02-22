pypre
=====

A python preprocessor

This package is meant to pre-process raw python 3 files.

Usage:

::

    pypre [ -i INPUT_FILE or --input INPUT_FILE ] [ -o OUTPUT_FILE --output OUTPUT_FILE ]

| If an input file is not given, pypre will read input on stdin.
  Likewise, if an output file is not
| given, pypre will write output to stdout.

The syntax for the preprocessor is fairly simple:

::

    * `#define <CONST> [<VALUE>]`
        > This defines a new constant name "CONST", optionally with the value "VALUE". If a VALUE
        > is not specified, "CONST" will be assigned the value `None`. "VALUE" **must** be a python
        > literal value. The primitive objects currently supported are:
            >> * `int`
            >> * `float`
            >> * `str`
            >> * `bytes`
        > This also includes the following primitive collections of these types:
            >> * `list`
            >> * `tuple`
            >> * `dict`
            >> * `set`
        > Finally, values **MUST** be literal. pypre cannot and will not interpret `#define`s that
        > include `#define`d constant names.
        > *NOTE:* This preprocessor (unlike the C/C++ preprocessors) will not replace instances of
        > names of `#define`d constants with their values in the code. It's only meant for
        > conditional compilation, and replacing names with constants saves a miniscule amount of
        > time at runtime for the vast majority of Python scripts.
    * `#ifdef <CONST>`
        > Begins a block of conditionally-compiled code. All code up to the _next_ terminator will
        > be included in the output if and only if the constant named by "CONST" has been defined.
        > (see `#endif`)
    * `#ifndef <CONST>`
        > Provided mainly for historical reasons, this begins a block of conditionally-compiled
        > code similar to `#ifdef`, but will include the enclosed block if and only if the named
        > constant "CONST" is _not_ defined.
    * `#if <EXPR>`
        > The real meat of pypre. This begins a block of conditionally-compiled code based on
        > the truth-y value of "EXPR". "EXPR" can take two forms. In the first form, it takes a
        > single value. It can be - somewhat uselessly - a python literal that would be valid as the
        > "VALUE" of a `#define`, or it can be the name of a previously-`#define`d value.
        > In its second form, "EXPR" looks like:
            >> `<VALUE> <OP> <VALUE>`
        > Where each "VALUE" is anything that would be valid for a "VALUE" in the first form, and
        > "OP" is a boolean operator. Valid operators and their definition are:
            >> * `=`
                >>> The Equality Operator - tests that the two values are equal.
            >> * `!`
                >>> The Inequality Operator - tests that the two values are NOT equal.
            >> * `<`
                >>> The Less-Than Operator - tests that the first value is strictly less than the
                >>> second.
            >> * `>`
                >>> The Greater-Than Operator - tests that the first value is strictly greater than
                >>> the second.
    * `#else`
        > If found within a block of conditionally-compiled code, will begin a section of
        > conditionally-code that will be included if and only if the lines between the directive
        > that started the block and the line containing `#else` are *not* included.
    * `#endif`
        > Ends a block of conditionally-compiled code. For every `#if`, `#ifdef` and `ifndef`,
        > there must be exactly one `#endif`.

| The following values are defined at runtime, and can be overridden
  with an environment variable
| of the same name:

::

    * `PYTHON_VERSION` - A tuple of the form "(MAJOR, MINOR, MICRO)" where each element is of
       type `int`. It will default to the version information of the interpreter used to run
       pypre. Setting this will set `PYTHON_MAJOR_VERSION`, `PYTHON_MINOR_VERSION`, and
       `PYTHON_MICRO_VERSION` accordingly.
    * `PYTHON_MAJOR_VERSION` - An `int` representing a Python major version number. Will default
       to the major version number of the interpreter used to run pypre. If you set this variable
       through the environment variable of the same name, it will set `PYTHON_MINOR_VERSION`
       and `PYTHON_MICRO_VERSION` both to `0` (unless those are set as well, in which case they
       will use their defined values).
    * `PYTHON_MINOR_VERSION` - An `int` representing a Python minor version number. Will default
       to the minor version number of the interpreter used to run pypre. If you set this variable
       through the environment variable of the same name, it will set `PYTHON_MAJOR_VERSION` to
       `3` and `PYTHON_MICRO_VERSION` to `0`. (unless those are set as well, in which case they
       will use their defined values).
    * `PYTHON_MINOR_VERSION` - An `int` representing a Python micro version number. Will default
       to the micro version number of the interpreter used to run pypre. If you set this variable
       through the environment variable of the same name, it will set `PYTHON_MAJOR_VERSION` to
       `3` and `PYTHON_MINOR_VERSION` to `0`. (unless those are set as well, in which case they
       will use their defined values).
    * `OS` - A `str` naming the operating system. Defaults to the `sysname` part of the output of
       `os.uname()`.
    * `ARCH` - A string specifying the system's architecture. Defaults to the output of
       `platform.machine()`
    * `IS64` - True if the host processor is 64-bit, otherwise 32-bit. Default is determined using
       the `bits` part of the output of `platform.architecture()`.

| Note that if you do choose to override these values, you MUST match
  their type. For example, if
| the name ``FOO`` is provided with a value of (b'\\x69', 15.2), you
  must provide a value that is a
| 2-tuple of the form (``bytes``, ``float``). In bash, this example
  would look like:

.. code:: bash

    FOO="(b'my overridden bytes', -1.1)"

| Some caveats and disclaimers:
| \* pypre does **not** as of this time support nested conditions.
  Placing an ``#if``, ``#ifdef`` or
| ``#ifndef`` in between an ``#if*`` and its ``#endif`` will almost
  always result in an error.
| \* Do not use spaces in your names or values (except between elements
  in collections) as this
| will instantly crash the preprocessor.
| \* pypre is only built for, and only tested against Python 3 versions.
  Don't be surprised if
| it doesn't work if run through your Python 2 interpreter. (Note that
  you can easily include
| pypre directives in Python 2 code as long as pypre itself is run
  through Python 3, although
| it will require you to set ``PYTHON_VERSION`` yourself if you plan to
  use it.)
| \* Setting ``PYTHON_VERSION`` and one of the more specific
  "MAJOR"/"MINOR"/"MICRO" variables to
| non-compatible values will cause the preprocessor to immediately exit.
  For example, you
| can't have ``PYTHON_VERSION=(2,7,0)`` and ``PYTHON_MAJOR_VERSION=3`` -
  be sure your environment
| makes sense.
