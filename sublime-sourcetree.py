import os
import sublime
import sublime_plugin
import subprocess


def find_sourcetree():
    for p in ('%PROGRAMFILES(x86)%\\Atlassian\\SourceTree\\SourceTree.exe',
              '%PROGRAMFILES%\\Atlassian\\SourceTree\\SourceTree.exe',
              '/usr/local/bin/stree',
              '/Applications/SourceTree.app'):
        bin_path = os.path.expandvars(p)
        if os.path.exists(bin_path):
            return bin_path

    return None


repo_root_cache = {}


def find_repo_root(file_name):
    global repo_root_cache

    leaf_dir = os.path.dirname(file_name)
    if leaf_dir in repo_root_cache:
        return repo_root_cache[leaf_dir]

    prev_directory = ""
    directory = leaf_dir
    while prev_directory != directory:
        if any([os.path.exists(os.path.join(directory, repo)) for repo in ['.git', '.hg']]):
            repo_root_cache[leaf_dir] = directory
            return directory
        prev_directory = directory
        directory = os.path.abspath(os.path.join(directory, os.path.pardir))

    return None


class SourceTreeCommand(sublime_plugin.WindowCommand):
    def sourcetree_path(self):
        if hasattr(self, 'cached_sourcetree_path'):
            return self.cached_sourcetree_path

        settings = sublime.load_settings('sublime-sourcetree.sublime-settings')

        if settings.get('detect_sourcetree', True):
            bin_path = find_sourcetree()
            if bin_path:
                self.cached_sourcetree_path = bin_path
                return bin_path
            return None

        explicit_path = settings.get('sourcetree_path')
        if explicit_path:
            bin_path = os.path.expandvars(explicit_path)
            if os.path.exists(bin_path):
                self.cached_sourcetree_path = bin_path
                return bin_path

        return None

    def execute_sourcetree_cmd(self, sourcetree_path, args):
        if sourcetree_path.endswith('.App'):
            subprocess.call(['open', '-a', sourcetree_path] + args)
        else:
            subprocess.Popen([sourcetree_path] + args)

    def get_main_args(self, report_errors=False):
        file_name = self.window.active_view().file_name()
        if file_name is None or len(file_name) <= 0:
            if report_errors:
                sublime.error_message(__name__ + ': No file to execute command on.')
            file_name = None
            repo_root = None
        else:
            repo_root = find_repo_root(file_name)
            if repo_root is None and report_errors:
                sublime.error_message(__name__ + ': Unable to find repository root.')

        sourcetree = self.sourcetree_path()
        if sourcetree is None and report_errors:
            sublime.error_message(__name__ + ': Unable to find SourceTree executable.')

        return (sourcetree, repo_root, file_name)

    def is_enabled(self):
        return self.is_visible()

    def is_visible(self):
        (sourcetree, repo_root, file_name) = self.get_main_args()
        return sourcetree is not None and repo_root is not None and file_name is not None


class SourceTreeFileLogCommand(SourceTreeCommand):
    def run(self):
        (sourcetree, repo_root, file_name) = self.get_main_args(True)
        if sourcetree is not None and repo_root is not None and file_name is not None:
            self.execute_sourcetree_cmd(sourcetree, ['-f', repo_root, 'filelog', file_name])


class SourceTreeSearchCommand(SourceTreeCommand):
    def get_search_term(self):
        view = self.window.active_view()
        selections = view.sel()
        if len(selections) == 1 and len(view.lines(selections[0])) == 1:
            text = view.substr(selections[0])
            if len(text) > 0:
                return text
        return None

    def run(self):
        (sourcetree, repo_root, file_name) = self.get_main_args(True)
        search_term = self.get_search_term()
        if sourcetree is not None and repo_root is not None and search_term is not None:
            self.execute_sourcetree_cmd(sourcetree, ['-f', repo_root, 'search', search_term])

    def is_enabled(self):
        return super(SourceTreeSearchCommand, self).is_enabled() and self.get_search_term() is not None


class SourceTreeCommitCommand(SourceTreeCommand):
    def run(self):
        (sourcetree, repo_root, file_name) = self.get_main_args(True)
        if sourcetree is not None and repo_root is not None:
            self.execute_sourcetree_cmd(sourcetree, ['-f', repo_root, 'commit'])
