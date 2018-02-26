"""
This package defines the way the preprocessor parses input files.
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

import re
import sys

from . import directives

class ParserError(Exception):
	"""
	An object indicating a generic error that occurred during parsing.
	"""


	def __init__(self, fname, msg, line=None):
		"""
		docstring for ParserError.__init__
		"""

		super(ParserError, self).__init__()
		self.fname = fname
		self.msg = msg
		self.line = line

	def __str__(self):
		"""
		Implements 'str(self)'
		"""
		if self.line is not None:
			return "%s:%d %s" % (self.fname, self.line, self.msg)
		return "%s: %s" % (self.fname, self.msg)

_compare = {'=': lambda x,y: x == y,
            '>': lambda x,y: x > y,
            '<': lambda x,y: x < y,
            '!': lambda x,y: not x == y}

_keywords = {}

def warn(fname, line, lineNo, ctxt):
	"""
	Generates a warning message, but does not stop processing
	"""
	print("%s:%d" % (fname, lineNo), line.lstrip()[6:], file=sys.stderr)
	return ctxt

def error(fname, line, lineNo, unused_ctxt):
	"""
	Generates an error message and ceases processing
	"""
	raise ParserError(fname, line.lstrip()[7:], lineNo)

def addDefine(fname, line, lineNo, ctxt):
	"""
	Adds a '#define'd constant to the list of directives.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
		value = line[2] if len(line) == 3 else None
	except IndexError:
		raise ParserError(fname, "Could not parse new/redefined constant", lineNo)

	if value is not None:
		try:
			#pylint: disable=W0123
			value = eval(value)
			#pylint: enable=W0123
		except:
			raise ParserError(fname, "Error parsing literal value for '%s'" % name, lineNo)

	directives.DIRECTIVES[name] = value

	return ctxt

def removeDefine(unused_fname, line, unused_lineNo, ctxt):
	"""
	Handles '#undef' directives.
	"""
	line = line.strip().split(' ')

	if line[1] in directives.DIRECTIVES:
		del directives.DIRECTIVES[line[1]]

	return ctxt

def ifdef(fname, line, lineNo, ctxt):
	"""
	Handles a single `#ifdef` directive.

	Also handles any `#else` clauses.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
	except IndexError:
		raise ParserError(fname, "'#ifdef' without argument", lineNo)

	endifPos = 0
	elsePos = None
	nest = 0
	for n, srcLine in enumerate(ctxt):
		strippedline = srcLine.strip()
		if srcLine.strip().startswith('#if'):
			nest += 1
		elif strippedline.split(' \t')[0] == "#else" and not nest:
			elsePos = n
		elif strippedline.split(' \t')[0] == "#endif":
			if not nest:
				endifPos = n
				break
			nest -= 1
			if nest < 0:
				raise ParserError(fname, "Extraneous '#endif'", lineNo)
	else:
		raise ParserError(fname, "'#ifdef' without '#endif'!", lineNo)

	if name in directives.DIRECTIVES:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]

def ifndef(fname, line, lineNo, ctxt):
	"""
	Handles a single `#ifdef` directive.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
	except IndexError:
		raise ParserError(fname, "'#ifndef' without argument", lineNo)

	endifPos = 0
	elsePos = None
	nest = 0
	for n, srcLine in enumerate(ctxt):
		strippedline = srcLine.strip()
		if srcLine.strip().startswith('#if'):
			nest += 1
		elif strippedline.split(' \t')[0] == "#else" and not nest:
			elsePos = n
		elif strippedline.split(' \t')[0] == "#endif":
			if not nest:
				endifPos = n
				break
			nest -= 1
			if nest < 0:
				raise ParserError(fname, "Extraneous '#endif'", lineNo)
	else:
		raise ParserError(fname, "'#ifndef' without '#endif'!", lineNo)

	if name not in directives.DIRECTIVES:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]

def condition(fname, line, lineNo, ctxt):
	"""
	Handles a basic condition of the form `#if <VALUE> [<OP> <VALUE>]`
	"""
	global _compare

	line = [field for field in line.strip().split(' ') if field]

	#pylint: disable=W0123
	if len(line) == 2:
		if line[1] in directives.DIRECTIVES:
			cnd = directives.DIRECTIVES[line[1]]
		else:
			try:
				cnd = eval(line[1])
			except:
				raise ParserError(fname, "Error parsing literal value", lineNo)

	elif len(line) == 4:
		if line[1] in directives.DIRECTIVES:
			line[1] = directives.DIRECTIVES[line[1]]
		else:
			try:
				line[1] = eval(line[1])
			except:
				raise ParserError(fname, "Error parsing literal value", lineNo)

		if line[3] in directives.DIRECTIVES:
			line[3] = directives.DIRECTIVES[line[1]]
		else:
			try:
				line[3] = eval(line[3])
			except:
				raise ParserError(fname, "Error parsing literal value", lineNo)

		cnd = _compare[line[2]](line[1], line[3])

	else:
		raise ParserError(fname, "Malformed condition: '%s'" % ' '.join(line), lineNo)
	#pylint: enable=W0123

	endifPos, elsePos, nest = 0, None, 0
	for n, srcLine in enumerate(ctxt):
		strippedline = srcLine.strip()
		if srcLine.strip().startswith('#if'):
			nest += 1
		elif strippedline.split(' \t')[0] == "#else" and not nest:
			elsePos = n
		elif strippedline.split(' \t')[0] == "#endif":
			if not nest:
				endifPos = n
				break
			nest -= 1
			if nest < 0:
				raise ParserError(fname, "Extraneous '#endif'", lineNo)
	else:
		raise ParserError(fname, "'#if' without '#endif'!", lineNo)

	if cnd:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]

_keywords = {re.compile(r"^#define \w+( .*)?$"): addDefine,
             re.compile(r"^#undef \w+"): removeDefine,
			 re.compile(r"^#ifdef \w+$"): ifdef,
			 re.compile(r"^#ifndef \w+$"): ifndef,
			 re.compile(r"^#if .+ (=|<|>|!) .+$"): condition,
			 re.compile(r"^#if .+$"): condition,
			 re.compile(r"^#warn .*$"): warn,
			 re.compile(r"^#error .*$"): error}

def Parse(infile):
	"""
	Parses the given input.
	Raises a 'ParserError' when anything goes wrong.
	"""
	global _keywords

	lines = infile.read().split('\n')
	lineNo = 1

	while True:
		for keyword in _keywords:
			if keyword.match(lines[lineNo-1].strip()) is not None:
				lines = lines[:lineNo-1] + _keywords[keyword](infile.name,
				                                              lines[lineNo-1],
				                                              lineNo,
				                                              lines[lineNo:])
				break
		else:
			for define, value in directives.DIRECTIVES.items():
				lines[lineNo-1] = lines[lineNo-1].replace(define, str(value))

		lineNo += 1

		if lineNo >= len(lines):
			break

	return "\n".join(lines)
