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
    settings = sublime.load_settings('sublime-sourcetree.sublime-settings')

    def sourcetree_path(self):
        if hasattr(self, 'cached_sourcetree_path'):
            return self.cached_sourcetree_path

        if self.settings.get('detect_sourcetree', True):
            bin_path = find_sourcetree()
            if bin_path:
                self.cached_sourcetree_path = bin_path
                return bin_path
            return None

        explicit_path = self.settings.get('sourcetree_path')
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


class SourceTreeFileComand(SourceTreeCommand):
    def get_main_args(self, report_errors=False):
        file_name = self.window.active_view().file_name()
        if not file_name or len(file_name) <= 0:
            if report_errors:
                sublime.error_message(__name__ + ': No file to execute command on.')
            repo_root = None
        else:
            repo_root = find_repo_root(file_name)
            if not repo_root and report_errors:
                sublime.error_message(__name__ + ': Unable to find repository root.')

        sourcetree = self.sourcetree_path()
        if not sourcetree and report_errors:
            sublime.error_message(__name__ + ': Unable to find SourceTree executable.')

        return (sourcetree, repo_root, file_name)

    def is_enabled(self):
        file_name = self.window.active_view().file_name()
        return file_name and len(file_name) > 0 and self.sourcetree_path() and find_repo_root(file_name)


class SourceTreeFileLogCommand(SourceTreeFileComand):
    def run(self):
        (sourcetree, repo_root, file_name) = self.get_main_args(True)
        self.execute_sourcetree_cmd(sourcetree, ['-f', repo_root, 'filelog', file_name])
