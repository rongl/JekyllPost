# -*- coding: utf-8 -*-
# @author           RonGL
# @link             https://github.com/rongl/JekyllPost
import re
import os
import datetime
import sublime
import sublime_plugin


class JekyllPostCommand(sublime_plugin.TextCommand):

    def run(self, edit, **args):
        _type = 'create'
        if 'type' in args and args['type'] in ['rename', 'delete', 'drafts', 'posts']:
            _type = args['type']
        if _type == 'create':
            self._createPost()
        else:
            self._updatePost(edit, _type)

    def _updatePost(self, edit, type):
        view = self.view
        orgFilePath = view.file_name()
        orgFileName = os.path.basename(orgFilePath)
        extension = self._getSetting('fileExt')
        checkDir = self._getSetting('searchFolder')
        if type == 'posts':
            checkDir = self._getSetting('drafts')
        if (re.match(r'^(?P<date>[\d]{4}\-[\d]{2}\-[\d]{2})\-(?P<info>.*)\.' + extension + '$', orgFileName,  re.I | re.M | re.X)
                and os.path.basename(os.path.dirname(orgFilePath)) == checkDir):
            if type == 'delete' and sublime.ok_cancel_dialog('确定删除文档(' + orgFileName + ')', '删除'):
                os.path.islink(orgFilePath) or (os.path.isfile(orgFilePath) and os.remove(orgFilePath))
                view.set_scratch(True)
                view.window().run_command("close")
            elif type == 'rename':
                self.orgFilePath = orgFilePath
                self._showInput(os.path.splitext(orgFilePath.replace(self._getRoot() + os.sep, ''))[0], self.on_change)
            elif type == 'drafts':
                self._mvFile({'fullPath': orgFilePath,
                              'view': view,
                              'current': self._getSetting('searchFolder'),
                              'traget': self._getSetting('drafts'),
                              'tragetName': '草稿箱'})
            elif type == 'posts':
                self._mvFile({'fullPath': orgFilePath,
                              'view': view,
                              'current': self._getSetting('drafts'),
                              'traget': self._getSetting('searchFolder'),
                              'tragetName': '发报箱'})

    def _mvFile(self, args):
        removePath = os.path.abspath(args['fullPath'].replace(args['current'], args['traget']))
        removePathDir = os.path.dirname(removePath)
        msg = '把文档(' + args['fullPath'] + ')移动到' + args['tragetName'] + '里(' + removePath.replace(self._getRoot() + os.sep, '') + ')'
        if os.path.exists(removePathDir) and os.path.isdir(removePathDir):
            os.path.islink(args['fullPath']) or (os.path.isfile(args['fullPath']) and os.rename(args['fullPath'], removePath))
            args['view'].set_scratch(True)
            args['view'].window().run_command("close")
        elif sublime.ok_cancel_dialog(msg, '移动'):
            sublime.error_message(args['tragetName'] + "目录(" + removePathDir + ")不存在,无法移动")

    def _setPostsDir(self):
        self.targtDir = ''
        searchFolder = self._getSetting('searchFolder')
        if re.match(r'^_\w+$', searchFolder) == None:
            searchFolder = '_posts'
        dirRoot = self._getRoot()
        findedDir = []
        for root, dirs, files in os.walk(dirRoot, False):
            for name in dirs:
                if name == searchFolder:
                    findedDir.append(os.path.join(root, name))
                    continue
        self.targtDir = dirRoot
        if len(findedDir) > 0:
            if len(findedDir) > 0:
                findedDir.sort(key=lambda x: len(x.split('/')))
            self.targtDir = findedDir[0]

    def _createPost(self):
        self._setPostsDir()
        self._showInput(None, self.on_done)

    def _showInput(self, input_string=None, fun=None):
        self.view.window().show_input_panel(
            '文档名称:',
            input_string or self.targtDir.lstrip(self._getRoot()) + os.sep + self._getFileNamePrefix(),
            fun,
            None,
            None
        )

    def _getRoot(self):
        return (self.view.window().folders())[0]

    def _getFileNamePrefix(self):
        return datetime.datetime.now().strftime("%Y-%m-%d-")

    def _getSetting(self, key):
        settings = sublime.load_settings('JekyllPost.sublime-settings')
        value = settings.get(key, None)
        if key == 'fileExt':
            value = (value if re.match(r'^([_\w]+)$', (value or '')) else 'md').strip()
        elif key == 'searchFolder':
            value = (value or '_posts').strip()
        elif key == 'drafts':
            value = (value or '_drafts').strip()
        elif key == 'template':
            value = value or []
        elif key == 'categories':
            value = value or {}
        return value

    def on_done(self, input_string):
        if input_string == self.targtDir.lstrip(self._getRoot()) + os.sep + self._getFileNamePrefix():
            self._showInput(None, self.on_done)
        else:

            if re.match(r'^[\w\/\-]+$', input_string) == None:
                self._showInput(None, self.on_done)
            else:
                extension = self._getSetting('fileExt')
                createFile = (
                    self._getRoot() + os.sep + input_string + '.' + extension).strip()
                inputTextMatch = re.match(
                    r'^(?P<date>[\d]{4}\-[\d]{2}\-[\d]{2})\-(?P<info>.*)\.' + extension + '$', os.path.basename(createFile), re.I | re.M | re.X)
                self.inputTextDict = {}
                self.inputTextDict['filename'] = os.path.basename(createFile)
                if inputTextMatch:
                    inputTextSet = inputTextMatch.group('info').split('_')
                    self.inputTextDict['tags'] = ", ".join(
                        list(map(lambda x: x.replace('-', ' ').title(), inputTextSet)))
                    self.inputTextDict['title'] = self.inputTextDict[
                        'tags'].replace(',', '')
                    self.inputTextDict['categories'] = inputTextSet[0]
                if os.path.exists(createFile):
                    sublime.error_message("文档已存在,请使用其它名称")
                    self._showInput(input_string)
                else:
                    fs = open(createFile, 'w+')
                    fs.writelines(
                        map(self._mapText, self._getSetting('template')))
                    fs.close()
                    self.view.window().open_file(createFile)

    def _mapText(self, text):
        for match in re.finditer(r'.*?(?P<string>\$\{\{(?P<type>\w+)\:?(?P<mark>.*?)\}\})', text, re.I | re.M | re.X):
            formater = {
                'date': lambda: datetime.datetime.now().strftime(match.group('mark')),
                'title': lambda: self.inputTextDict['title'] or self.inputTextDict['filename'],
                'tags': lambda: self.inputTextDict['tags'] or self.inputTextDict['filename'],
                'categories': lambda: self._getCate(self.inputTextDict['categories'])
            }

            if match.group('type') in formater:
                text = text.replace(match.group('string'), formater[match.group('type')]())
            else:
                text = text.replace(match.group('string'), match.group('type'))
        return text + "\n"

    def _getCate(self, cate):
        cates = self._getSetting('categories')
        for c in cates:
            if c.startswith(cate):
                return cates[c]
        return (cate or 'other').replace('-', '_')

    def on_change(self, input_string):
        newFilePath = self._getRoot() + os.sep + input_string + '.' + self._getSetting('fileExt')
        orgFilePath = self.orgFilePath
        view = self.view
        if orgFilePath != newFilePath and os.path.exists(newFilePath):
            sublime.error_message("文档已存在,请使用其它名称")
            self._showInput(input_string, self.on_change)
        else:
            view.window().run_command("save")
            os.path.islink(orgFilePath) or (os.path.isfile(orgFilePath) and os.rename(orgFilePath, newFilePath))
            nview = view.window().open_file(newFilePath)
            view.window().focus_view(view)
            view.set_scratch(True)
            view.window().run_command("close")
            nview.window().focus_view(nview)
