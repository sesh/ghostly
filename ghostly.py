#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Surely we can do
basic acceptance testing
with just 6 commands

Browser Commands: load, click, fill, submit, wait, switch_to
Asserts: assert_text
"""

import random
import string

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
                        parent.find_element_by_name,
                        parent.find_element_by_id,
                        parent.find_element_by_css_selector,
                        parent.find_element_by_tag_name,
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
        """
        Load the provided URL in the web browser
        """
        self.browser.get(url)

    def click(self, selector):
        """
        Click on an element that's currently visble on the page. The element can be selected
        with a range of selectors:
            - .class_name
            - #element_id
            - element
            - "Link Text"
        """
        element = self._get_element(selector)
        element.click()

    def submit(self, selector, *contents):
        """
        Fill out and submit a form
        """
        form = self.fill(selector, *contents)
        form.submit()

    def fill(self, selector, *contents):
        """
        Fill out a form without submitting it.

        Provide a list where the first item is the selector to use to find the form and
        all following items are <selector>: <value> pairs to be used to complete the form.

        Use the `submit` function if you also want to submit the form.
        """
        r = ''.join(random.choice(string.letters + string.digits) for _ in range(12))
        form = self._get_element(selector)
        for c in contents:
            for k, v in c.items():
                v = v.replace('<random>', r)
                element = self._get_element(k, parent=form)
                element.send_keys(v)
        return form

    def assert_text(self, text, selector='body'):
        """
        Assert that a piece of text exists on the currently displayed page.
        """
        self.wait(1)
        element = self._get_element(selector)
        assert text in element.text

    def wait(self, seconds):
        """
        Wait for a specified number of seconds
        """
        if type(seconds) == str:
            seconds = int(seconds)
        time.sleep(seconds)

    def switch_to(self, selector):
        """
        Switch to a new frame (useful for navigating between iFrames)
        """
        self.browser.switch_to_frame(selector)

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        test_yaml = yaml.load(open(arg).read())
        for test in test_yaml:
            g = Ghostly()
            try:
                for step in test['test']:
                    # print step
                    for f, v in step.items():
                        func = getattr(g, f)
                        if type(v) == list:
                            func(*v)
                        else:
                            func(v)
            # explicitly catch the error states for now
            except NoSuchElementException:
                print "✘ {} (couldn't find element)".format(test['name'])
            except AssertionError:
                print "✘ {} (assertion failed)".format(test['name'])
            else:
                print '✔ {}'.format(test['name'])
            finally:
                g.end()
