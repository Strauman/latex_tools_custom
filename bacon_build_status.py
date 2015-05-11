import sublime, sublime_plugin, os

callback_active=False

file_hidden=False

def hide_build_status_file():
	# if file_hidden:
	# 	return
	file_hidden=True
	prefs = sublime.load_settings('Preferences.sublime-settings')
	hidden_files=prefs.get("file_exclude_patterns")
	if "build_status" in hidden_files:
		return
	
	hidden_files.append("build_status")
	prefs.set("file_exclude_patterns", hidden_files)
	sublime.save_settings('Preferences.sublime-settings')

hide_build_status_file()

def set_status_all_views(status):
	for view in sublime.active_window().views():
		view.set_status("build_status", status)
	
def update_build_status():
	buildstatus=None
	for f in sublime.active_window().folders():
		buildstatus_file=os.path.join(f, "build_status")
		# print(buildstatus_file)
		if os.path.isfile(buildstatus_file):
			buildstatus=open(buildstatus_file, 'r').read()
			break
	# print(buildstatus)
	if buildstatus=="0":
		set_status_all_views("Build failes")
	elif buildstatus=="1":
		set_status_all_views("Build passes")

	sublime.set_timeout(update_build_status, 1000)

if not callback_active:
	callback_active=True
	sublime.set_timeout(update_build_status, 1000)

