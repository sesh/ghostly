#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Surely we can do
basic acceptance testing
with just 6 commands

Browser Commands: load, click, fill, submit, wait, switch_to, navigate
Asserts: assert_text
"""

import random
import string
import sys
import time

import click
import yaml

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException


def milli_now():
    return int(time.time() * 1000)


class Ghostly:

    def __init__(self, browser):
        browser = browser.lower()
        if browser == 'firefox':
            self.browser = webdriver.Firefox()
        elif browser == 'chrome':
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

    def navigate(self, navigation):
        """
        Possible navigation methods:
            - forward
            - back
        """
        if navigation not in ['forward', 'back']:
            raise AttributeError("An invalid option was given to the navigation command")
        f = getattr(self.browser, navigation)
        f()


@click.command()
@click.argument('ghostly_files', type=click.File('rb'), nargs=-1)
@click.option('--browser', default='chrome', help='browser to use [chrome, firefox]')
@click.option('--verbose', is_flag=True)
def run_ghostly(ghostly_files, browser, verbose):
    tests = []
    passed = []
    failed = []

    for f in ghostly_files:
        test_yaml = yaml.load(f.read())
        tests.extend(test_yaml)

    click.echo('Running {} tests...'.format(len(tests)))
    for test in tests:
        # we create a new Ghostly instance for each tests, keeps things nice and
        # isolated / ensures there is a clear cache
        g = Ghostly(browser)
        try:
            for step in test['test']:
                # print step
                for f, v in step.items():
                    func = getattr(g, f)
                    if type(v) == list:
                        func(*v)
                    else:
                        func(v)
        # explicitly catch the possible error states and fail the test with an appropriate message
        except NoSuchElementException as e:
            fail(test['name'], "couldn't find element", e, verbose)
            failed.append(test)
        except WebDriverException as e:
            fail(test['name'], "webdriver failed", e, verbose)
            failed.append(test)
        except AssertionError as e:
            fail(test['name'], "couldn't find element", e, verbose)
            failed.append(test)
        else:
            click.echo(click.style("✔", fg='green') + " " + test['name'])
            passed.append(test)
        finally:
            g.end()

    click.echo("{}/{} tests have passed".format(len(passed), len(tests)))
    if failed:
        sys.exit(1)


def fail(name, reason, exception=None, verbose=False):
    click.echo(click.style("✘", fg='red') + " {} ({})".format(name, reason))
    if verbose:
        click.echo(exception)


if __name__ == '__main__':
    run_ghostly()
