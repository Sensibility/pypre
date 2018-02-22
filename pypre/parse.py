"""
This package defines the way the preprocessor parses input files.
"""

import re
import pdb

from . import directives

class ParserError(Exception):
	"""
	An object indicating a generic error that occurred during parsing.
	"""


	def __init__(self, msg, line=None):
		"""
		docstring for ParserError.__init__
		"""

		super(ParserError, self).__init__()
		self.msg = msg
		self.line = line

	def __str__(self):
		"""
		Implements 'str(self)'
		"""
		if self.line is not None:
			return "%s - Line #%d" % (self.msg, self.line)
		return self.msg

_compare = {'=': lambda x,y: x == y,
            '>': lambda x,y: x > y,
            '<': lambda x,y: x < y,
            '!': lambda x,y: not x == y}

def addDefine(line, lineNo=None, ctxt=None):
	"""
	Adds a '#define'd constant to the list of directives.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
		value = line[2] if len(line) == 3 else None
	except IndexError:
		if lineNo is not None:
			raise ParserError("Could not parse new/redefined constant", lineNo)
		raise ParserError("Could not parse new/redefined constant.")

	if value is not None:
		try:
			#pylint: disable=W0123
			value = eval(value)
			#pylint: enable=W0123
		except:
			if lineNo is not None:
				raise ParserError("Error parsing literal value for '%s'" % name, lineNo)
			raise ParserError("Error parsing literal value for %s" % name)

	directives.DIRECTIVES[name] = value

	return ctxt

def ifdef(line, lineNo=None, ctxt=None):
	"""
	Handles a single `#ifdef` directive.

	Also handles any `#else` clauses.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
	except IndexError:
		if lineNo is not None:
			raise ParserError("'#ifdef' without argument", lineNo)
		raise ParserError("'#ifdef' without argument")

	endifPos = 0
	elsePos = None
	for n, srcLine in enumerate(ctxt):
		if srcLine.strip().split(' \t')[0] == "#else":
			elsePos = n
		elif srcLine.strip().split(' \t')[0] == "#endif":
			endifPos = n
			break
	else:
		if lineNo is not None:
			raise ParserError("'#ifdef' without '#endif'!", lineNo)
		raise ParserError("'#ifdef' without '#endif'!")

	if name in directives.DIRECTIVES:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]

def ifndef(line, lineNo=None, ctxt=None):
	"""
	Handles a single `#ifdef` directive.
	"""
	line = line.strip().split(' ')

	try:
		name = line[1]
	except IndexError:
		if lineNo is not None:
			raise ParserError("'#ifndef' without argument", lineNo)
		raise ParserError("'#ifndef' without argument")

	endifPos = 0
	elsePos = None
	for n, srcLine in enumerate(ctxt):
		if srcLine.strip().split(' \t')[0] == "#else":
			elsePos = n
		elif srcLine.strip().split(' \t')[0] == "#endif":
			endifPos = n
			break
	else:
		if lineNo is not None:
			raise ParserError("'#ifndef' without '#endif'!", lineNo)
		raise ParserError("'#ifndef' without '#endif'!")

	if name not in directives.DIRECTIVES:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]

def condition(line, lineNo=None, ctxt=None):
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
				if lineNo is not None:
					raise ParserError("Error parsing literal value", lineNo)
				raise ParserError("Error parsing literal value")

	elif len(line) == 4:
		if line[1] in directives.DIRECTIVES:
			line[1] = directives.DIRECTIVES[line[1]]
		else:
			try:
				line[1] = eval(line[1])
			except:
				if lineNo is not None:
					raise ParserError("Error parsing literal value", lineNo)
				raise ParserError("Error parsing literal value")

		if line[3] in directives.DIRECTIVES:
			line[3] = directives.DIRECTIVES[line[1]]
		else:
			try:
				line[3] = eval(line[3])
			except:
				pdb.set_trace()
				if lineNo is not None:
					raise ParserError("Error parsing literal value", lineNo)
				raise ParserError("Error parsing literal value")

		cnd = _compare[line[2]](line[1], line[3])

	elif lineNo is not None:
		raise ParserError("Malformed condition: '%s'" % ' '.join(line), lineNo)
	else:
		raise ParserError("Malformed condition: '%s'" % ' '.join(line))
	#pylint: enable=W0123

	endifPos, elsePos = 0, None
	for n, srcLine in enumerate(ctxt):
		if srcLine.strip().split(' \t')[0] == '#else':
			elsePos = n
		elif srcLine.strip().split(' \t')[0] == '#endif':
			endifPos = n
			break
	else:
		if lineNo is not None:
			raise ParserError("'#if' without '#endif'!", lineNo)
		raise ParserError("'#if' without '#endif'!")

	if cnd:
		if elsePos is not None:
			return ctxt[:elsePos] + ctxt[endifPos+1:]
		return ctxt[:endifPos] + ctxt[endifPos+1:]

	if elsePos is not None:
		return ctxt[elsePos+1:endifPos] + ctxt[endifPos+1:]
	return ctxt[endifPos+1:]


_keywords = {re.compile(r"^#define \w+ .*$"): addDefine,
			 re.compile(r"^#ifdef \w+$"): ifdef,
			 re.compile(r"^#ifndef \w+$"): ifndef,
			 re.compile(r"^#if .+ (=|<|>|!) .+$"): condition}

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
			try:
				if keyword.match(lines[lineNo-1].strip()) is not None:
					lines = lines[:lineNo-1] + _keywords[keyword](lines[lineNo-1], lineNo, lines[lineNo:])
					break
			except IndexError:
				pdb.set_trace()
		lineNo += 1

		if lineNo >= len(lines):
			break

	return "\n".join(lines)
