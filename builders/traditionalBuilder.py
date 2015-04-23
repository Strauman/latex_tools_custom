# ST2/ST3 compat
from __future__ import print_function 
import sublime
if sublime.version() < '3000':
    # we are on ST2 and Python 2.X
	_ST3 = False
else:
	_ST3 = True

from pdfBuilder import PdfBuilder
import sublime_plugin
import re
import os, os.path
import codecs

DEBUG = False

DEFAULT_COMMAND_LATEXMK = ["latexmk", "-cd",
				"-e", "$pdflatex = '%E -interaction=nonstopmode -synctex=1 -aux-directory=%F -output-directory=%F %S %O'",
				"-f", "-pdf", "-aux-directory=%F"]

DEFAULT_CLEAN_COMMAND = ["latexmk", "-c %F"]

DEFAULT_COMMAND_WINDOWS_MIKTEX = ["texify", 
					"-b", "-p", "--engine=%E",
					"--tex-option=\"--synctex=1\""]


#----------------------------------------------------------------
# TraditionalBuilder class
#
# Implement existing functionality, more or less
# NOTE: move this to a different file, too
#
class TraditionalBuilder(PdfBuilder):

	def __init__(self, tex_root, output, builder_settings, platform_settings, tool_settings):
		self.out_setting=False
		self.output_settings=tool_settings.get("output")
		# Sets the file name parts, plus internal stuff
		super(TraditionalBuilder, self).__init__(tex_root, output, builder_settings, platform_settings) 
		# Now do our own initialization: set our name
		self.name = "Traditional Builder"
		# Display output?
		self.display_log = builder_settings.get("display_log", False)
		# Build command, with reasonable defaults
		plat = sublime.platform()
		# Figure out which distro we are using
		try:
			distro = platform_settings["distro"]
		except KeyError: # default to miktex on windows and texlive elsewhere
			if plat == 'windows':
				distro = "miktex"
			else:
				distro = "texlive"
		if distro in ["miktex", ""]:
			default_command = DEFAULT_COMMAND_WINDOWS_MIKTEX
		else: # osx, linux, windows/texlive, everything else really!
			default_command = DEFAULT_COMMAND_LATEXMK
		self.cmd = builder_settings.get("command", default_command)
		# Default tex engine (pdflatex if none specified)
		self.engine = builder_settings.get("program", "pdflatex")
		# Sanity check: if "strange" engine, default to pdflatex (silently...)
		if not(self.engine in ['pdflatex', "pdftex", 'xelatex', 'xetex', 'lualatex', 'luatex']):
			self.engine = 'pdflatex'



	#
	# Very simple here: we yield a single command
	# Only complication is handling custom tex engines
	#
	def commands(self):
		# Print greeting
		self.display("\n\nTraditionalBuilder: ")

		# See if the root file specifies a custom engine
		engine = self.engine
		cmd = self.cmd[:] # Warning! If I omit the [:], cmd points to self.cmd!
		file_lines=codecs.open(self.tex_root, "r", "UTF-8", "ignore").readlines()
		out_dir=""
		if file_lines[1].startswith('%?'):
			print(file_lines[1])
			outs=re.match(r"%\?([a-z0-9]+)\s*$", file_lines[1])
			print("outs"+outs.group(1))
			if outs:
				self.out_setting=outs.group(1)
				out_dir=self.output_settings.get(self.out_setting, "bin")
				print("\nout_set: "+self.out_setting+"\n")

		for line in file_lines:
			if not line.startswith('%'):
				break
			else:
				# We have a comment match; check for a TS-program match
				mroot = re.match(r"%\s*!TEX\s+(?:TS-)?program *= *(xe(la)?tex|lua(la)?tex|pdf(la)?tex)\s*$",line)
				if mroot:
					engine = mroot.group(1)
					if cmd[0] == "texify":
						if not re.match(r"--engine\s?=\s?%E", cmd[3]):
							cmd.append("--engine=%E")
					if cmd[0] == "latexmk":
					  # Sanity checks
					  if not re.match(r"\$pdflatex\s?=\s?'%E", cmd[3]): # fixup blanks (linux)
						  sublime.error_message("You are using a custom build command.\n"\
							  "Cannot select engine using a %!TEX program directive.\n")
						  yield("", "Could not compile.")
					
					break

		if cmd[0] == "texify":
			engine = engine.replace("la","") # texify's --engine option takes pdftex/xetex/luatex as acceptable values

		if engine != self.engine:
			self.display("Engine: " + self.engine + " -> " + engine + ". ")
			
		cmd[3] = cmd[3].replace("%E", engine)

		
		cmd[3] = cmd[3].replace("%F", out_dir)
		cmd[6] = cmd[6].replace("%F", out_dir)
		# texify wants the .tex extension; latexmk doesn't care either way
		yield (cmd + [self.tex_name], "Invoking " + cmd[0] + "... ")
		if (self.output_settings.get("auto_clean", True)):
			clcmd=DEFAULT_CLEAN_COMMAND[:]
			for tmproot, dirs, files in os.walk(out_dir):
				for currentFile in files:
					temp_exts = ('.blg','.bbl','.aux','.log','.brf','.nlo','.out','.dvi','.ps','.lof','.toc','.fls','.fdb_latexmk','.pdfsync','.synctex.gz','.ind','.ilg','.idx')
					if any(currentFile.lower().endswith(ext) for ext in temp_exts):
						os.remove(os.path.join(tmproot, currentFile))
			
		self.display("done.\n")
		
		# This is for debugging purposes 
		if self.display_log:
			self.display("\nCommand results:\n")
			self.display(self.out)
			self.display("\n\n")	
