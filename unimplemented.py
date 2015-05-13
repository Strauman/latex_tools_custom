import sublime, sublime_plugin, os, re
from os import path

		
class BaconCheckUnimplementedCommand(sublime_plugin.WindowCommand):

	def __init__(self, *args, **kwargs):
		super(BaconCheckUnimplementedCommand, self).__init__(*args, **kwargs)
		self.not_implemented=[]
		self.input_dirname="inputs"
		self.rootfiles_dirname="pages"
		self.topfolder=""

	def diff_lists(a, b):
		b = set(b)
		return [aa for aa in a if aa not in b]

	def is_enabled(self):
		self.window=sublime.active_window()
		for f in self.window.folders():
			if path.isdir(path.join(f, self.input_dirname)) and path.isdir(path.join(f, self.input_dirname)):
				return True
		return False
	def is_visible(self):
		return True

	def run(self):
		self.window=sublime.active_window()
		for f in self.window.folders():
			if path.isdir(path.join(f, self.input_dirname)) and path.isdir(path.join(f, self.input_dirname)):
				self.topfolder=f
				return self.show_unimplemented(f)

	def rreplace(self,s,old,new,occurrence=1):
		li = s.rsplit(old, occurrence)
		return new.join(li)

	def show_unimplemented(self, root):
		input_files=self.get_tex_files(path.join(root, self.input_dirname))
		root_files=self.get_tex_files(path.join(root, self.rootfiles_dirname))
		self.awaits_files=[]
		for rf in root_files:
			self.searchFileForAwaits(rf)

		diff=list(set(input_files)-set(self.awaits_files))
		self.not_implemented=diff
		self.window.show_quick_panel(diff, self.setChosenToClipboard)

	def setChosenToClipboard(self, index):
		if index==-1:
			return
		sublime.set_clipboard(self.not_implemented[index])

	def searchFileForAwaits(self, file):
		awaitsfiles=[]
		file_contents=open(path.join(self.topfolder, self.rootfiles_dirname, file)+".tex", 'r').read()
		for awaits in re.findall(r"\\awaits{([^}]+)}", file_contents):
			self.awaits_files.append(awaits)

	def get_tex_files(self, searchdir, extension="tex"):
		files=[]
		for filename in os.listdir(searchdir):
			if extension:
				if (not filename.endswith(extension)):
					continue
			files.append(self.rreplace(filename, '.tex', ''))
		return files