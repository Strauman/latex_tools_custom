import sublime, sublime_plugin, os

callback_active=False

file_hidden=False

SHOULD_EXCLUDE=False

def add_to_exclude_files(filename):
	prefs = sublime.load_settings('Preferences.sublime-settings')
	hidden_files=prefs.get("file_exclude_patterns")
	if (filename in hidden_files) and not SHOULD_EXCLUDE:
		hidden_files.remove(filename)
	elif(filename not in hidden_files) and SHOULD_EXCLUDE:
		hidden_files.append(filename)
	
	prefs.set("file_exclude_patterns", hidden_files)
	sublime.save_settings('Preferences.sublime-settings')

# server_file_hidden=False
# if not server_file_hidden:
	# add_to_exclude_files("build_status")

def set_status_all_views(status):
	for view in sublime.active_window().views():
		view.set_status("build_status", status)
	
def update_build_status():
	buildstatus=None
	for f in sublime.active_window().folders():
		buildstatus_file=os.path.join(f, "build_status")
		if not os.path.isfile(buildstatus_file):
			continue
		try:
			buildstatus=open(buildstatus_file, 'r').read()
			break
		except IOError:
			continue
	if buildstatus=="0":
		set_status_all_views("Build failes")
	elif buildstatus=="1":
		set_status_all_views("Build passes")

	sublime.set_timeout(update_build_status, 1000)

if not callback_active:
	callback_active=True
	sublime.set_timeout(update_build_status, 1000)

