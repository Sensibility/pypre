"""
A python preprocessor

Usage
-----

::

    pypre [ -i INPUT_FILE or --input INPUT_FILE ] [ -o OUTPUT_FILE --output OUTPUT_FILE ]

| If an input file is not given, pypre will read input on stdin.
  Likewise, if an output file is not
| given, pypre will write output to stdout.

Syntax
------

The syntax for the preprocessor is fairly simple:

-  ``#define <CONST> [<VALUE>]``

       This defines a new constant name "CONST", optionally with the
       value "VALUE". If a VALUE is not specified, "CONST" will be
       assigned the value ``None``. "VALUE" **must** be a python literal
       value. The primitive objects currently supported are:

       -  ``int``
       -  ``float``
       -  ``str``
       -  ``bytes``
          This also includes the following primitive collections of
          these types:
       -  ``list``
       -  ``tuple``
       -  ``dict``
       -  ``set``
          Finally, values **MUST** be literal. pypre cannot and will not
          interpret ``#define``\ s that include ``#define``\ d constant
          names.  
          Just like the C/C++ preprocessor, anywhere a ``#define``d constant
          is found within the source code (except on lines containing directives)
          it will be replaced with its value. *WARNING:* This does not yet check
          whether names are inside of string literals or comments.

-  ``#undef <CONST>``

       Removes the definition of the name specified by "CONST". If the
       name wasn't defined in the first place, nothing happens (or at
       least it shouldn't).

-  ``#ifdef <CONST>``

       Begins a block of conditionally-compiled code. All code up to the
       matching terminator will be included in the output if and only if
       the constant named by "CONST" has been defined. (see ``#endif``)

-  ``#ifndef <CONST>``

       Provided mainly for historical reasons, this begins a block of
       conditionally-compiled code similar to ``#ifdef``, but will
       include the enclosed block if and only if the named constant
       "CONST" is *not* defined.

-  ``#if <EXPR>``

       The real meat of pypre. This begins a block of
       conditionally-compiled code based on the truth-y value of "EXPR".
       "EXPR" can take two forms. In the first form, it takes a single
       value. It can be - somewhat uselessly - a python literal that
       would be valid as the "VALUE" of a ``#define``, or it can be the
       name of a previously-\ ``#define``\ d value. In its second form,
       "EXPR" looks like: ``<VALUE> <OP> <VALUE>`` Where each "VALUE" is
       anything that would be valid for a "VALUE" in the first form, and
       "OP" is a boolean operator. Valid operators and their definition
       are:

       -  ``=``

              The Equality Operator - tests that the two values are
              equal.

       -  ``!``

              The Inequality Operator - tests that the two values are
              NOT equal.

       -  ``<``

              The Less-Than Operator - tests that the first value is
              strictly less than the second.

       -  ``>``

              The Greater-Than Operator - tests that the first value is
              strictly greater than the second.

-  ``#else``

       If found within a block of conditionally-compiled code, will
       begin a section of conditionally-code that will be included if
       and only if the lines between the directive that started the
       block and the line containing ``#else`` are *not* included.

-  ``#endif``

       Ends a block of conditionally-compiled code. For every ``#if``,
       ``#ifdef`` and ``ifndef``, there must be exactly one ``#endif``.

Guaranteed Values
-----------------

| The following values are defined at runtime, and can be overridden
  with an environment variable
| of the same name:

-  ``PYTHON_VERSION``

       A tuple of the form "(MAJOR, MINOR, MICRO)" where each element is
       of type ``int``. It will default to the version information of
       the interpreter used to run pypre. Setting this will set
       ``PYTHON_MAJOR_VERSION``, ``PYTHON_MINOR_VERSION``, and
       ``PYTHON_MICRO_VERSION`` accordingly.

-  ``PYTHON_MAJOR_VERSION``

       An ``int`` representing a Python major version number. Will
       default to the major version number of the interpreter used to
       run pypre. If you set this variable through the environment
       variable of the same name, it will set ``PYTHON_MINOR_VERSION``
       and ``PYTHON_MICRO_VERSION`` both to ``0`` (unless those are set
       as well, in which case they will use their defined values).

-  ``PYTHON_MINOR_VERSION``

       An ``int`` representing a Python minor version number. Will
       default to the minor version number of the interpreter used to
       run pypre. If you set this variable through the environment
       variable of the same name, it will set ``PYTHON_MAJOR_VERSION``
       to ``3`` and ``PYTHON_MICRO_VERSION`` to ``0``. (unless those are
       set as well, in which case they will use their defined values).

-  ``PYTHON_MICRO_VERSION``

       An ``int`` representing a Python micro version number. Will
       default to the micro version number of the interpreter used to
       run pypre. If you set this variable through the environment
       variable of the same name, it will set ``PYTHON_MAJOR_VERSION``
       to ``3`` and ``PYTHON_MINOR_VERSION`` to ``0``. (unless those are
       set as well, in which case they will use their defined values).

-  ``PYTHON_IMPLEMENTATION``

       A ``str`` that names the Python implementation. Defaults to the
       output of ``platform.python_implementation()``. Some examples
       include: ‘CPython’, ‘IronPython’, ‘Jython’, ‘PyPy’.

-  ``OS``

       A ``str`` naming the operating system. Defaults to the
       ``sysname`` part of the output of ``os.uname()``.

-  ``ARCH``

       A string specifying the system's architecture. Defaults to the
       output of ``platform.machine()``

-  ``IS64``

       True if the host processor is 64-bit, otherwise False. Default is
       determined using the ``bits`` part of the output of
       ``platform.architecture()``.

-  ``__DATE__``

       A literal ``str`` containing the date on which the pre-processing
       is occurring, in the same format as the C++ macro of the same
       name: "Mmm dd yyyy". The default value is obtained from the
       output of ``time.strftime("%b %d %Y")``.

-  ``__TIME__``

       A literal ``str`` containing the local time at which the
       pre-processing is occurring, in the same format as the C++ macro
       of the same name: "hh:mm:ss". The default value is obtained from
       the output of ``time.strftime("%H:%M:%S")``.

-  ``__IPV6__``

       ``True`` if the system supports IPv6 addressing, ``False``
       otherwise. Default value is obtained from the value of
       ``socket.has_ipv6``.

-  ``__BYTE_ORDER__``

       This is a value representing the native byte order of the host
       machine. Its default value is calculated using the ``struct``
       library and it has no particular guaranteed value. The only thing
       that can be depended upon is that it will be equal to either
       ``__BIG_ENDIAN__`` or ``__LITTLE_ENDIAN__``; never both and never
       neither. *Implementation Note:* As of the time of this writing,
       ``__BIG_ENDIAN__`` is set to the value ``1`` and
       ``__LITTLE_ENDIAN__`` is set to the value ``0``. This is subject
       to change as I may need to specify the endian-ness of bits or
       gods only knows what else in the future.

| Note that if you do choose to override these values, you MUST match
  their type. For example, if
| the name ``FOO`` is provided with a value of (b'\\x69', 15.2), you
  must provide a value that is a
| 2-tuple of the form (``bytes``, ``float``). In bash, this example
  would look like:

.. code:: bash

    FOO="(b'my overridden bytes', -1.1)" pypre

Some caveats and disclaimers:
-----------------------------

-  Do not use spaces in your names or values (except between elements in
   collections) as this will instantly crash the preprocessor.
-  pypre is only built for, and only tested against Python 3 versions.
   Don't be surprised if it doesn't work if run through your Python 2
   interpreter. (Note that you can easily include pypre directives in
   Python 2 code as long as pypre itself is run through Python 3,
   although it will require you to set ``PYTHON_VERSION`` yourself if
   you plan to use it.)
-  Setting ``PYTHON_VERSION`` and one of the more specific
   "MAJOR"/"MINOR"/"MICRO" variables to non-compatible values will cause
   the preprocessor to immediately exit. For example, you can't have
   ``PYTHON_VERSION=(2,7,0)`` and ``PYTHON_MAJOR_VERSION=3`` - be sure
   your environment makes sense.

"""

"""
Copyright 2018, Github (https://github.com/) user ocket8888 (https://github.com/ocket8888),
                Github organization Sensibility (https://github.com/Sensibility)
"""

"""
This file is part of pypre.

    pypre is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pypre is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pypre.  If not, see <http://www.gnu.org/licenses/>.
"""


__author__ = "ocket8888"
__version__ = "0.3.0"

import argparse
import sys
from . import directives, parse

def main() -> int:
	"""
	The main routine of the processor.
	"""

	parser = argparse.ArgumentParser(description='A preprocessor for Python.',
	epilog='Uses somewhat C-like syntax. For full usage help see https://github.com/Sensibility/pypre')

	parser.add_argument("-i",
	                    "--input",
	                    dest='input',
	                    help='Input file to read from. If not given, pypre reads from stdin.',
	                    default=None,
	                    type=str)

	parser.add_argument("-o",
	                    "--output",
	                    dest='output',
	                    help='Output file to write to. If not given, pypre writes to stdout.',
	                    default=None,
	                    type=str)

	args = parser.parse_args()

	try:
		infile = open(args.input) if args.input is not None else sys.stdin
	except OSError as e:
		print("Error getting input: %s" % e, file=sys.stderr)
		return 1

	try:
		outfile = open(args.output, 'w') if args.output is not None else sys.stdout
	except OSError as e:
		infile.close()
		print("Error getting file handle for output: %s", file=sys.stderr)
		return 1

	try:
		directives.readEnv()
	except (ValueError, TypeError, SyntaxError) as e:
		print(e, file=sys.stderr)
		infile.close()
		outfile.close()
		return 2

	try:
		parsedOutput = parse.Parse(infile)
	except parse.ParserError as e:
		print(e, file=sys.stderr)
		outfile.close()
		return 1
	finally:
		infile.close()

	try:
		outfile.write(parsedOutput)
	except OSError as e:
		print("Error occurred when writing output: %s" % e, file=sys.stderr)
	finally:
		outfile.close()

	return 0
