# Mispy, the audio library curator.
#
#	python Mis.py [dir] [rd] [rf] [rds] [rfs]
#		dir = The directory to look inside
#		rd  = Rename directories by
#
# Supported filetypes: MP3, M4A, FLAC, WAV

import os, sys, re
from tinytag import TinyTag
from colorama import init as cinitx
cinitx()

MESSAGE_SYNTAX = "Syntax:\npython Mis.py [dir] [rd] [rf] [rds] [rfs] [dbg]\n\
\tdir = The directory to look inside (encased in \"quotes\"). Current by default.\n\
\trd  = Rename directories by \"Artist - 2012 - Album\". y(es) by default. [y/n]\n\
\trf  = Rename files by \"01 - Title\", or <rfs> if set. n(o) by default. [y/n]\n\
\trds = Optional directory renaming syntax (encased in \"quotes\"). Possible values:\n\
\t\t%TRACK%, %TITLE%, %ARTIST%, %ALBUM%, %ALBUM_ARTIST%, %YEAR%\n\
\t\tOr, use \"default\".\n\
\trfs = Optional file renaming syntax (encased in \"quotes\"). This uses the same values as above.\n\
\tdbg = Optional debugging mode. If enabled, this will only log intentions.\n\
\t\tNo files will be changed. n(o) by default. [y/n]\n"
THIS_DIRECTORY = os.path.abspath(".")

XCOLOURS = {
	'red':		"\033[1;31m",
	'blue':		"\033[1;34m",
	'cyan':		"\033[1;36m",
	'green':	"\033[0;32m",
	'reset':	"\033[0;0m",
	'bold':		"\033[;1m" }
def printx(string, col='reset', debug=False):
	if (debug):
		if (ARGS['debug']):
			sys.stdout.write(XCOLOURS[col])
			print("* " + str(string))
			sys.stdout.write(XCOLOURS['reset'])
		else:
			pass
	else:
		sys.stdout.write(XCOLOURS[col])
		print(str(string))
		sys.stdout.write(XCOLOURS['reset'])

def exit_error(str):
	printx(("ERROR (fatal): " + str), 'red')
	exit()

ARGS = { "scan_directory": THIS_DIRECTORY,
	"rename_directories": True,
	"rename_files": False,
	"rename_dir_syntax": "default",
	"rename_file_syntax": "default",
	"debug": False }
##################
def parse_cli_arguments(args):
	for p in range(1, len(args)):
		if (p == 1):
			if (args[p].startswith('-')):
				ARGS['scan_directory'] = THIS_DIRECTORY
			elif (os.path.exists(args[p])):
				ARGS['scan_directory'] = str(args[p])
			else:
				exit_error("If '"+args[p]+"' is a path, Mis.py can't access it.")

		if (args[p].startswith('-')):
			# Options without extra arguments
			if (args[p] == "-h" or args[p] == "--help"):
				printx(MESSAGE_SYNTAX, 'cyan')
				exit()
			if (args[p] == "-d"):
				ARGS['rename_directories'] = False
			if (args[p] == "-f"):
				ARGS['rename_files'] = True
			if (args[p] == "--debug"):
				ARGS['debug'] = True

			# Options with arguments
			if (args[p].startswith('--')):
				if (args[p] == "--dname"):
					ARGS['rename_dir_syntax'] = str(args[p+1])
				if (args[p] == "--fname"):
					ARGS['rename_file_syntax'] = str(args[p+1])
##################

parse_cli_arguments(sys.argv)

if (ARGS['debug'] == True):
	printx("Debug mode enabled.\n\tLines starting with '*' show exactly what \n\
\tWOULD happen if debugging mode was disabled.", 'green')

printx(("Arguments (raw): " + str(sys.argv)), 'cyan', True)
printx(("Arguments: " + str(ARGS)), 'cyan', True)

def read_tags(filename): # todo: read tags from every file in directory, set albumartist to most common
	"""Read audio tags from a file"""
	tags = TinyTag.get(filename)
	printx(("> Tags: " + str(tags)), 'green', True)
	return tags

def rename(path, filetype, new_name):
	"""Rename directory or file"""
	if (ARGS['debug'] == 1):
		printx(("Rename '"+path+"' to '"+new_name+"'."), 'green')
	else:
		pass #os.rename(path, new_name)

def is_valid_file(path):
	"""
	Returns [path, filetype] if a file can be read by Mis.py, otherwise returns [False, ""]
	"""
	if (path.endswith(".mp3")):
		return ([path, ".mp3"])
	if (path.endswith(".m4a")):
		return ([path, ".m4a"])
	if (path.endswith(".flac")):
		return ([path, ".flac"])
	if (path.endswith(".wav")):
		return ([path, ".wav"])
	else:
		return (False, "")

def get_first_valid_filename(path):
	items = os.listdir(path)
	for it in items:
		if (is_valid_file(it)[0]):
			return os.path.join(path, it[0])
		else:
			printx(("Error: Couldn't find a supported file in '" + path + "'."), 'red')
			return False

def is_directory(path):
	return os.path.isdir(path)

def parse_rename_syntax(syntax_raw, directory):
	"""
	Parse the naming syntax. It's recommended to pass any "default" value here too.

	directory	True/False	Is this a directory?
	"""
	if (syntax_raw == "default"):
		if (directory == True):
			syntax_raw = "%ALBUM_ARTIST% - %YEAR% - %ALBUM%"
		else:
			syntax_raw = "%TRACK% - %ARTIST% - %TITLE%"

	return syntax_raw.split("%")

def get_new_filename(filename, syntax_raw, tags):
	"""Get the new, customized name for a file or directory."""
	split_syntax = parse_rename_syntax(syntax_raw, is_directory(filename))

	output_filename = ""

	for piece in split_syntax:
		if (piece == "TRACK"):
			printx(piece, 'blue', True)
			output_filename += str(tags.track) if (tags.track!=None) else "00"
		elif (piece == "TITLE"):
			printx(piece, 'blue', True)
			output_filename += str(tags.title) if (tags.title!=None) else "NO TITLE"
		elif (piece == "ARTIST"):
			printx(piece, 'blue', True)
			output_filename += str(tags.artist) if (tags.track!=None) else "NO ARTIST"
		elif (piece == "ALBUM"):
			printx(piece, 'blue', True)
			output_filename += str(tags.album) if (tags.track!=None) else "NO ALBUM"
		elif (piece == "ALBUM_ARTIST"): # todo: work out a way to handle split/collective albums
			printx(piece, 'blue', True)
			if (tags.albumartist == None):
				output_filename += str(tags.artist) if (tags.artist!=None) else "NO ALBUMARTIST"
		elif (piece == "YEAR"):
			printx(piece, 'blue', True)
			if (len(tags.year) > 4):
				sx = (tags.year).split('-')[1]
				if (len(sx) == 4):
					printx(("Guessed year '"+str(sx)+"' from '"+str(filename)+"'."), 'cyan')
					output_filename += str(sx)
				else:
					printx(("Failed to retrieve a properly formatted year from: '"+str(filename)+"'."), 'red')
					output_filename += str("NOYR")

			output_filename += str(tags.year)
		else:
			printx(piece, 'blue', True)
			output_filename += str(piece)

	# Removes all characters that aren't alphanumeric or -.,!?()'
	# and replaces them with _
	return os.path.join(ARGS['scan_directory'], \
		(str(re.sub(r'(?u)[^\w -.,!?()\']', '-', output_filename.strip()))))

# Everything in set directory
def recurse(item):
	printx(("Current: " + item), 'cyan', True)

	if (is_directory(item)):
		if (get_first_valid_filename(item) != False):
			first_valid_filename = get_first_valid_filename(item)
		else:
			return

		for item_nested in os.listdir(item):
			recurse(os.path.join(item, item_nested))

		nf = get_new_filename(item, ARGS['rename_dir_syntax'], read_tags(first_valid_filename))
		printx(("New filename: " + nf), 'cyan', True)

	else:
		if (is_valid_file(item)[0]):
			nf = get_new_filename(item, ARGS['rename_file_syntax'], read_tags(item))
		else:
			printx(("Skipped over unsupported file: " + item), 'red')
			return False

	rename(is_valid_file(item)[0], is_valid_file(item)[1], nf)

for item in os.listdir(ARGS['scan_directory']):
	item = os.path.join(ARGS['scan_directory'], item)
	recurse(item)

	# if (is_valid_file(item)):
	# 	printx(("1"), 'red')
	# 	recurse(item)
	# else:
	# 	if (is_directory(item)):
	# 		printx(("2a"), 'red')
	# 		recurse(item)
	# 	else:
	# 		printx(("2b"), 'red')
	# 		print(("Skipped over unsupported file: " + item), 'red')
# todo: fields in syntax are repeating their names after the fields
