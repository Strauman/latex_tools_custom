import sublime
import sublime_plugin
import os
import re
import codecs

# COMMANDS_FILE="/lib/shorts.tex"
COMMANDS_FILES=["/rapport/commands.tex", "~/Documents/LaTeX/preamble/commands.tex","/commands.tex", "/lib/shorts.tex", "/lob/remap.tex"]
# COMMANDS_FILE="/commands.tex"
# class LatexCompleteCommand(sublime_plugin.TextCommand):
#     def run
 
class ShortsCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        point = view.sel()[0].b
        result=[]
        # return result
        if not view.score_selector(point,
                "text.tex.latex"):
            return []
        # result+=self.autocomplete_newcommand(view,prefix,locations,COMMANDS_FILE)
        for fname in COMMANDS_FILES:
            result+=self.autocomplete_newcommand(view,prefix,locations,fname)
        
        return result
        # return (result, sublime.INHIBIT_WORD_COMPLETIONS)
        # return (result, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)
        # return (result, sublime.INHIBIT_EXPLICIT_COMPLETIONS)

    def view_is_selector(self, view, selector):
        point = view.sel()[0].b
        return view.score_selector(point, selector)
    def parse_autocomplete_cwl(self,view,prefix,locations):
        requires_math_mode=["amsmath.sty"]
        result=[]
        cwl_dir=sublime.packages_path()+"/Bacon tools/cwl"
        for file_name in os.listdir(cwl_dir):
            file_path=cwl_dir+"/"+file_name
            if (not file_path.endswith(".cwl")):
                continue
            try:
                src_file = codecs.open(file_path, "r", 'UTF-8')
            except IOError:
                sublime.status_message("bacon_tools WARNING: cannot open cwl files " + file_path)
                print ("WARNING! I can't find it! Check your \\include's and \\input's.")
            src_content = re.sub("%%%%(.*)",r'\1',src_file.read())
            src_content = re.sub("%%.*","",src_file.read())
            src_file.close()
            first_line=src_content.split('\n', 1)[0]
            mode=re.search(r"mode:[\s]*(.*)", first_line)
            if (mode):
                mode=mode.group(1)
                if (mode in requires_math_mode and not self.view_is_selector(view,"text.tex.latex string.other.math")):
                    # print(mode, "requires mathmode")
                    continue
            cwl_commands=re.findall(r"(\\[a-zA-Z0-9]+)(?:{([^}]+)})?", src_content)
            for m in cwl_commands:
                if (len(m) > 1):
                    label=m[0]+"{"+m[1]+"}"
                    content=m[0]+"{${1:"+m[1]+"}}"
                else:
                    content=label=m[0]
                content=content[1:]
                result.append((label, content))
        return result


    def autocomplete_newcommand(self, view, prefix, locations, file_name):
        file_path=False
        result=[]

        # print "p:", prefix
        for folder in sublime.active_window().folders():
            if (os.path.isfile(folder+file_name)):
                file_path=folder+file_name
        if(not file_path):
            return []
        try:
            src_file = codecs.open(file_path, "r", 'UTF-8')
        except IOError:
            sublime.status_message("bacon_tools WARNING: cannot open shorts file " + file_path)
            print ("WARNING! I can't find it! Check your \\include's and \\input's.")
        src_content = src_file.read()#re.sub("%.*","",src_file.read())
        # src_content = re.sub("^%.*","",src_file.read())
        src_file.close()

        ## WORKING: ##
        # newcommands=re.findall(r"\\newcommand{(.*?)}(?:\[\])?(?:{([^}]+)})?.*", src_content)
        ## NEW ##
        # r"\\newcommand{(.*?)}(?:\[([0-9])\])?(?:{([^}]+)})?.*}(%%\([a-zA-Z0-9,]+\)%%)?"
        # Format ish:
        # \newcommand{(|STRINGAZ|)}[|NUMARGS|][|optArgs|]{dostuff}%%(|argname,argname|)%%%DESCRIPTION%
        #                  0            1        2           3                4             5
        # lcontent=src_content.split("\n")

        ## WorkingBackup
        # r"\\newcommand{(.*?)}(?:\[([0-9])\])?(?:\[(.*?)\])?(?:{([^}]+)})?.*}(?:%%\(([a-zA-Z0-9,]+)\)%%)?(?:%([^%]+)%)?"
        #^(?:%%)?\\newcommand{(.*?)}(?:\[([0-9])\])?(?:\[(.*?)\])?(?:%%\(([a-zA-Z0-9,]+)\)%%)?(?:%([^%]+)%)?$
        
        newcommands=re.findall(r"^(?:%%)?\\newcommand{([^}]+)}(?:\[([0-9])\])?(?:\[(.*?)\])?[^%\n]+(?:%%\(([a-zA-Z0-9,]+)\)%%)?(?:%([^%]+)%)?$", src_content, flags=re.M)

        for m in newcommands:
            commandName=m[0]
            numArgs=m[1]
            optArgVals=m[2]
            # body=m[3]
            argnames=m[3]
            description=m[4]
            if (len(m) > 1):
                label=commandName
                content=commandName
                if optArgVals:
                    label+="[{0}]".format(optArgVals)
                    content+="[{0}]".format(optArgVals)
                if argnames:
                    anames=argnames.split(",")
                    for i,nm in enumerate(anames,start=1):
                        label+="{{{0}}}".format(nm)
                        #Snippet syntax ${1:PLACEHOLDER}
                        content+="{{${{{0}:{1}}}}}".format(i,nm)
                elif numArgs and int(numArgs)>0:
                    numReqArgs=int(numArgs)
                    if optArgVals:
                        numReqArgs-=1
                    label+="({0})".format(numReqArgs)

                    for i in range(1,numReqArgs+1):
                        content+="{{${0}}}".format(i)
                if description:
                    label+="\t{0}".format(description)
            else:
                content=label=m[0]
            content=content[1:]
            label=label[1:]
            result.append((label, content))
        return result

    def on_query_context(self,view, key, operator, operand, match_all):
        # print(view, key, operator, operand, match_all)
        pass


INPUT_PATH="/inputs/"
class AwaitsCompletions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        point = view.sel()[0].b
        if not view.score_selector(point,
                "text.tex.latex"):
            return []
        line_contents=False
        self.view=view
        should_list_files=False
        searchdir=False
        for folder in sublime.active_window().folders():
            if (os.path.isdir(folder+INPUT_PATH)):
                searchdir=folder+INPUT_PATH
                break
        if not searchdir:
            # print("not in search dir")
            return []

        for region in self.view.sel():
            line = self.view.line(region)
            line_contents = self.view.substr(line)
            (row, col)=self.view.rowcol(point)
            left_of_cursor=line_contents[:col]
            right_of_cursor=line_contents[col:]
            if (re.search(r"\\awaits{[\s]*$", left_of_cursor) and re.search(r"[\s]*}$", right_of_cursor)):
                should_list_files=True
                # print("loc:", left_of_cursor, "roc:", right_of_cursor)
                # print("pnt:", col)
                # print("Approved for listing files")
                break
        
        if(not should_list_files):
            return []
        files=self.filter_files(prefix, searchdir, "tex")
        print("Filtered files")
        # return (files, sublime.INHIBIT_WORD_COMPLETIONS)
        return files

    def rreplace(self,s,old,new,occurrence):
        li = s.rsplit(old, occurrence)
        return new.join(li)

    def on_query_context(self,view, key, operator, operand, match_all):
        
        # print("V:",view,"k:",key,"operator:",operator,"operand:",operand,"m_a:",match_all)
        return False
        point = view.sel()[0].b
        if not view.score_selector(point, "text.tex.latex"):
            return []
        for region in view.sel():
            line = view.line(region)
            line_contents = view.substr(line)
            if (re.search(r"\\awaits.*", line_contents)):
                # print("Context for files approved")
                return True                
                break
        # print("Context not for files")
        True

    def filter_files(self, prefix, searchdir, extension=False):
        files=[]
        for filename in os.listdir(searchdir):
            if extension:
                if (not filename.endswith(extension)):
                    continue
                else:
                    filename=self.rreplace(filename, '.tex','', 1)
            files.append((filename.replace(".", " "), filename))
        return files 