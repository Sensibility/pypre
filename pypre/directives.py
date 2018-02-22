"""
This module defines the acceptable directives and methods for adding them.
"""

import platform
import sys
import os

DIRECTIVES = {"PYTHON_VERSION": sys.version_info[:3],
              "PYTHON_MAJOR_VERSION": sys.version_info[0],
              "PYTHON_MINOR_VERSION": sys.version_info[1],
              "PYTHON_MICRO_VERSION": sys.version_info[2],
              "OS": os.uname()[0],
              "ARCH": platform.machine(),
              "IS64": platform.architecture()[0] == "64bit"}

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
