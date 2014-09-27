# coding: utf-8

import sublime
import sublime_plugin
import commands
import re


class GetHtmlTitleCommand(sublime_plugin.TextCommand):
    """get the title in html file for selected URL
    """
    STATUS_KEY = 'htmlTitle'
    STATUS_DURATION = 3000

    def run(self, edit):
        """main process of the command
        """
        # 01 get the first of selected texts
        self.show_status_message('retrieving title for URL...')

        selected_text, start_index = self.get_selected_text_with_index()
        if not self.is_valid_url(selected_text):
            self.show_status_message('usage: select an url before calling the command')
            return

        # 02 get the html
        result = self.get_html(selected_text)
        if not result:
            self.show_status_message('curl command not found')
            return

        # 03 extract the title in the html text
        title = self.get_title_in_html(result)
        if not title:
            self.show_status_message('title not found in html')

        # 04 insert the title just before the selected text
        # the argument to be inserted should be a unicode
        title_to_insert = title.strip().decode('utf-8')
        self.view.insert(edit, start_index, title_to_insert + ' ')
        self.show_status_message('title for URL gotten!')

    def get_selected_text_with_index(self):
        """get selected text and start index as a tuple (selected_text, index)
        """
        # returned value of self.view.sel() is
        # a list with composed of tuples: (start, end)
        selected_regions = self.view.sel()
        selected_region_first = selected_regions[0]
        selected_text = self.view.substr(selected_region_first).strip()

        return (selected_text, selected_region_first.begin())

    def is_valid_url(self, url):
        """check if the url is valid or not in a simple logic
        """
        return url and url.startswith('http')

    def get_html(self, url):
        """get html for the url with curl command
        """
        curl_result = commands.getoutput('curl ' + url)
        if not 'command not found' in curl_result:
            return curl_result
        else:
            return False

    def get_title_in_html(self, html):
        """get the value of title element in a html text
        """
        pattern = re.compile('<title>(.+)<\/title>')
        matched = pattern.search(html)
        if matched:
            # title is a str type
            title = matched.groups()[0]
            return title
        else:
            return False

    def show_status_message(self, message):
        """show status for this package with key STATUS_KEY and duration STATUS_DURATION
        """
        self.view.set_status(self.STATUS_KEY, message)
        erase_callback = lambda: self.view.erase_status(self.STATUS_KEY)
        sublime.set_timeout(erase_callback, self.STATUS_DURATION)
