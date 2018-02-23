"""
This module defines the acceptable directives and methods for adding them.
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

import platform
import sys
import os
import time
import socket
import struct

DIRECTIVES = {"PYTHON_VERSION": sys.version_info[:3],
              "PYTHON_MAJOR_VERSION": sys.version_info[0],
              "PYTHON_MINOR_VERSION": sys.version_info[1],
              "PYTHON_MICRO_VERSION": sys.version_info[2],
              "PYTHON_IMPLEMENTATION": platform.python_implementation(),
              "OS": os.uname()[0],
              "ARCH": platform.machine(),
              "IS64": platform.architecture()[0] == "64bit",
              "__DATE__": time.strftime("%b %d %Y"),
              "__TIME__": time.strftime("%H:%M:%S"),
              "__IPV6__": socket.has_ipv6,
              "__BIG_ENDIAN__": 1,
              "__LITTLE_ENDIAN__": 0}

# Idk of any other way to do this
DIRECTIVES["__BYTE_ORDER__"] = int(struct.unpack("=I", b'\x00\x00\x00\x01')[0] == 1)

_overridden = set()


def readEnv():
	"""
	Checks the execution environment for directive variables.

	Raises a ValueError if the environment specifies an invalid configuration.
	Raises a TypeError if an environment variable is set to a value of the wrong type.
	Raises a SyntaxError if the environment specifies a syntactically invalid value.
	"""
	global DIRECTIVES, _overridden

	for directive, preset in DIRECTIVES.items():
		override = os.getenv(directive)
		if override is not None:
			try:
				#pylint: disable=W0123
				override = eval(override)
				#pylint: enable=W0123
			except Exception as e:
				raise SyntaxError("Error parsing value '%s' for constant named '%s':\n%s" %\
				                                    (override,              directive, e))
			if not isinstance(override, type(preset)):
				raise TypeError("Value of '%s' must be of type %s!" %\
				                     (directive,    type(preset).__name__))

			DIRECTIVES[directive] = override

			_overridden.add(directive)

	# Check for invalid version specification
	if "PYTHON_VERSION" in _overridden:
		pv = DIRECTIVES["PYTHON_VERSION"]

		specifiers = {0: "PYTHON_MAJOR_VERSION",
		              1: "PYTHON_MINOR_VERSION",
		              2: "PYTHON_MICRO_VERSION"}

		for n, var in specifiers.items():
			if var in _overridden:
				if DIRECTIVES[var] != pv[n]:
					raise ValueError("'PYTHON_VERSION' and '%s' specify conflicting Python"\
					                 " versions!" % var)
			else:
				DIRECTIVES[var] = pv[n]
	# Set appropriate default values
	else:

		if "PYTHON_MAJOR_VERSION" in _overridden:
			if "PYTHON_MINOR_VERSION" not in _overridden:
				DIRECTIVES["PYTHON_MINOR_VERSION"] = 0

			if "PYTHON_MICRO_VERSION" not in _overridden:
				DIRECTIVES["PYTHON_MICRO_VERSION"] = 0
		elif "PYTHON_MINOR_VERSION" in _overridden:
			DIRECTIVES["PYTHON_MAJOR_VERSION"] = 3

			if "PYTHON_MICRO_VERSION" not in _overridden:
				DIRECTIVES["PYTHON_MICRO_VERSION"] = 0
		elif "PYTHON_MICRO_VERSION" in _overridden:
			DIRECTIVES["PYTHON_MAJOR_VERSION"] = 3
			DIRECTIVES["PYTHON_MICRO_VERSION"] = 0

		DIRECTIVES["PYTHON_VERSION"] = (DIRECTIVES["PYTHON_MAJOR_VERSION"],
		                                DIRECTIVES["PYTHON_MINOR_VERSION"],
		                                DIRECTIVES["PYTHON_MICRO_VERSION"])
