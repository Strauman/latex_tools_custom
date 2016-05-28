import sublime, sublime_plugin, os, re
from os import path


class BaconUnimplementedBase(sublime_plugin.WindowCommand):
	def __init__(self, *args, **kwargs):
		super(BaconUnimplementedBase, self).__init__(*args, **kwargs)
		self.input_dirname="inputs"
		self.rootfiles_dirname="pages"
		self.topfolder=""
		self.mode=False

	def beforeRun(self):
		pass

	def diff_lists(a, b):
		b = set(b)
		return [aa for aa in a if aa not in b]

	def is_enabled(self):
		self.window=sublime.active_window()
		for f in self.window.folders():
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
		self.beforeRun()
		self.setvars()
		self.show_list()

	def rreplace(self,s,old,new,occurrence=1):
		li = s.rsplit(old, occurrence)
		return new.join(li)

	def show_list(self):
		self.awaits_files=[]
		self.missing=[]
		for rf in self.root_files:
			files=[]
			if rf.isnumeric():
				files=self.searchFileForAwaits(rf)
				self.awaits_files+=(files)
				for f in files:
					if f not in self.input_files:
						self.missing.append("Page {pagefile}: {awaitname}.tex".format(awaitname=f, pagefile=rf))
			

		self.unimplemented=list(set(self.input_files)-set(self.awaits_files))
		# self.missing=list(set(self.awaits_files)-set(self.input_files))

		if (self.mode=="unimplemented"):
			diff=list(set(self.unimplemented))
			self.window.show_quick_panel(sorted(set(diff)), self.setChosenToClipboard)
		elif self.mode=="all":
			diff=list(set(self.unimplemented))
			awaits_code=""
			for i in sorted(set(diff)):
				awaits_code+="\\awaits{"+i+"}\n"
			sublime.set_clipboard(awaits_code)
		elif self.mode=="missing":
			self.window.show_quick_panel(sorted(set(self.missing)), self.passby)
		else:
			return
		
	def passby(self, index):
		pass
	def setChosenToClipboard(self, index):
		if index==-1:
			return
		
		unimp=sorted(set(self.unimplemented))
		awaits_code="\\awaits{"+unimp[index]+"}"
		# self.insert_on_sel(awaits_code)
		sublime.set_clipboard(awaits_code)

	def searchFileForAwaits(self, file):
		files=[]
		file_contents=open(path.join(self.topfolder, self.rootfiles_dirname, file)+".tex", 'r').read()
		for awaits in re.findall(r"\\awaits{([^}]+)}", file_contents):
			if awaits.endswith('.tex'):
				awaits=self.rreplace(awaits, '.tex', '')
			files.append(awaits)
		return files

	def get_tex_files(self, searchdir, extension="tex"):
		files=[]
		for filename in os.listdir(searchdir):
			if extension:
				if (not filename.endswith(extension)):
					continue
			files.append(self.rreplace(filename, '.tex', ''))
		return files
	def insert_on_sel(self, contents):
		view=self.window.active_view()
		for reg in view.sel():
			line=view.line(reg)
			edit=view.begin_edit()
			view.insert(edit, reg, contents)
			view.end_edit(edit)
			return


class BaconListDuplicatesCommand(BaconUnimplementedBase):	
	def beforeRun(self):
		self.mode=False

	def show_list(self):
		self.awaits_files=[]
		self.dupes=[]
		for rf in self.root_files:
			self.dupeFile(rf)
		
		self.window.show_quick_panel(sorted(set(self.dupes)), self.setChosenToClipboard)
	
	def setChosenToClipboard(self, index):
		if index==-1:
			return
		awaits_code="\\awaits{"+self.dupes[index]+"}"
		self.insert_on_sel(awaits_code)
		# sublime.set_clipboard(awaits_code)
	def dupeFile(self, file):
		file_contents=open(path.join(self.topfolder, self.rootfiles_dirname, file)+".tex", 'r').read()
		for awaits in re.findall(r"\\awaits{([^}]+)}", file_contents):
			if awaits.endswith('.tex'):
				awaits=self.rreplace(awaits, '.tex', '')
			if(awaits in self.awaits_files):
				self.dupes.append(awaits)
			else:
				self.awaits_files.append(awaits)

		
class BaconListUnimplementedCommand(BaconUnimplementedBase):	
	def beforeRun(self):
		self.mode="unimplemented"
class BaconCopyUnimplementedCommand(BaconUnimplementedBase):	
	def beforeRun(self):
		self.mode="all"

class BaconListMissingCommand(BaconUnimplementedBase):	
	def beforeRun(self):
		self.mode="missing"

class BaconInsertAllUnimplementedCommand(BaconUnimplementedBase):
	def run(self):
		self.mode=False
		self.setvars()
		self.show_list()
		view=self.window.active_view()
		for reg in view.sel():
			line=view.line(reg)
			contents=u''
			for f in self.unimplemented:
				contents+=u'\\awaits{'+f+'}\n'
			edit=view.begin_edit()
			view.insert(edit, line.begin(), contents)
			view.end_edit(edit)
			return
