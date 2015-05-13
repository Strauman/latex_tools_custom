import sublime, sublime_plugin, os, re
from os import path


class BaconUnimplementedBase(sublime_plugin.WindowCommand):
	def __init__(self, *args, **kwargs):
		super(BaconUnimplementedBase, self).__init__(*args, **kwargs)
		self.input_dirname="inputs"
		self.rootfiles_dirname="pages"
		self.topfolder=""
		self.mode=False

	def diff_lists(a, b):
		b = set(b)
		return [aa for aa in a if aa not in b]

	def is_enabled(self):
		self.window=sublime.active_window()
		for f in self.window.folders():
			print(path.join(f, self.input_dirname))
			if path.isdir(path.join(f, self.rootfiles_dirname)) and path.isdir(path.join(f, self.input_dirname)):
				return True
		return False
	def is_visible(self):
		return True
	def setvars(self):
		self.window=sublime.active_window()
		for f in self.window.folders():
			if path.isdir(path.join(f, self.input_dirname)) and path.isdir(path.join(f, self.input_dirname)):
				self.topfolder=f
				self.input_files=self.get_tex_files(path.join(f, self.input_dirname))
				self.root_files=self.get_tex_files(path.join(f, self.rootfiles_dirname))

	def run(self):
		self.setvars()
		self.show_list()

	def rreplace(self,s,old,new,occurrence=1):
		li = s.rsplit(old, occurrence)
		return new.join(li)

	def show_list(self):
		self.awaits_files=[]
		for rf in self.root_files:
			self.searchFileForAwaits(rf)

		self.unimplemented=list(set(self.input_files)-set(self.awaits_files))
		self.missing=list(set(self.awaits_files)-set(self.input_files))

		if (self.mode=="unimplemented"):
			diff=self.unimplemented
		elif self.mode=="missing":
			diff=self.missing
		else:
			return
		self.window.show_quick_panel(diff, self.setChosenToClipboard)

	def setChosenToClipboard(self, index):
		if index==-1:
			return
		sublime.set_clipboard("\\awaits{"+self.not_implemented[index]+"}")

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
		
class BaconListUnimplementedCommand(BaconUnimplementedBase):	
	def __init__(self, *args, **kwargs):
		super(BaconListUnimplementedCommand, self).__init__(*args, **kwargs)
		self.mode="unimplemented"

class BaconListMissingCommand(BaconUnimplementedBase):	
	def __init__(self, *args, **kwargs):
		super(BaconListMissingCommand, self).__init__(*args, **kwargs)
		self.mode="missing"
class BaconInsertAllUnimplementedCommand(BaconUnimplementedBase):
	def __init__(self, *args, **kwargs):
		super(BaconInsertAllUnimplementedCommand, self).__init__(*args, **kwargs)
		self.mode=False

	def run(self):
		self.setvars()
		self.show_list()
		view=self.window.active_view()
		for reg in view.sel():
			line=view.line(reg)
			contents=u''
			for f in self.unimplemented:
				contents+=u'\\awaits{'+f+'}\n'
			print(contents)
			edit=view.begin_edit()
			view.insert(edit, line.begin(), contents)
			view.end_edit(edit)
			return
