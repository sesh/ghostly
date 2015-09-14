#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

Surely we can do
basic acceptance testing
with just 5 commands

load, click, submit, wait, assertText
"""

import sys
import time

import yaml

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


def milli_now():
    return int(time.time() * 1000)


class Ghostly:

    def __init__(self):
        self.browser = webdriver.Chrome()

    def end(self):
        self.browser.quit()


    def _get_element(self, selector, parent=None, wait=10):
        """
        Returns a single element using a stripped down version of the jQuery lookup
        functions. Options are:
            - #element_id
            - .element_class
            - element_name
            - Link Text
        """

        # using our own wait-for-element logic
        wait = wait * 1000
        start = milli_now()

        # disable the browser/selenium wait time so that we can use our own logic
        self.browser.implicitly_wait(0)

        element = None
        while milli_now() < start + wait:
            if not parent:
                parent = self.browser

            try:
                if selector.startswith('#'):
                    return parent.find_element_by_id(selector.replace('#', ''))

                elif selector.startswith('.'):
                    return parent.find_element_by_class_name(selector.replace('.', ''))

                else:
                    funcs = [
                        parent.find_element_by_css_selector,
                        parent.find_element_by_tag_name,
                        parent.find_element_by_name,
                        parent.find_element_by_link_text
                    ]

                    for f in funcs:
                        try:
                            element = f(selector)
                            return element
                        except NoSuchElementException:
                            pass

            except NoSuchElementException:
                pass

        raise NoSuchElementException('Could not find element matching {}'.format(selector))


    def load(self, url):
        self.browser.get(url)


    def click(self, selector):
        element = self._get_element(selector)
        element.click()


    def submit(self, selector, contents):
        form = self._get_element(selector)
        for k, v in contents.items():
            element = self._get_element(k, parent=form)
            element.send_keys(v)
        form.submit()


    def assertText(self, text, selector='body'):
        self.wait(1)
        element = self._get_element(selector)
        assert text in element.text


    def wait(self, seconds):
        time.sleep(seconds)



if __name__ == '__main__':
    for arg in sys.argv[1:]:
        test_yaml = yaml.load(open(arg).read())
        for test in test_yaml:
            g = Ghostly()
            try:
                for step in test['test']:
                    for f, v in step.items():
                        func = getattr(g, f)
                        if type(v) == list:
                            func(*v)
                        else:
                            func(v)

            # explicitly catch the error states for now
            except NoSuchElementException:
                print '✘ {}'.format(test['name'])
            except AssertionError:
                print '✘ {}'.format(test['name'])
            else:
                print '✔ {}'.format(test['name'])
            finally:
                g.end()
