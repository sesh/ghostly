#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic acceptance testing with just 7 commands
(& 5 asserts)

Browser Commands: load, click, fill, submit, wait, switch_to, navigate
Asserts: assert_text, assert_element, assert_value, assert_title, assert_url
"""

import random
import string
import sys
import time

import click
import yaml

from PIL import Image
from io import BytesIO

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys


def milli_now():
    return int(time.time() * 1000)


class GhostlyTestFailed(Exception):
    def __init__(self, message):
        self.message = message


class Ghostly:

    def __init__(self, browser, width, height):
        if isinstance(browser, dict):
            self.browser_name = 'remote'
        else:
            self.browser_name = browser.lower()

        if self.browser_name == 'firefox':
            self.browser = webdriver.Firefox()
        elif self.browser_name == 'chrome':
            self.browser = webdriver.Chrome()
        elif self.browser_name == 'phantomjs':
            self.browser = webdriver.PhantomJS()
        elif self.browser_name == 'safari':
            self.browser = webdriver.Safari()
        elif self.browser_name == 'remote':
            self.browser = webdriver.Remote(
                command_executor=browser['remote']['url'],
                desired_capabilities=browser['remote']
            )
            self.browser_name = "{} - {} {}".format(self.browser_name,
                                                   browser['remote']['browser'],
                                                   browser['remote']['browser_version'])

        self.browser.set_window_size(width, height)
        self.width = width
        self.height = height

    def end(self):
        self.browser.quit()

    def _get_element(self, selector, parent=None, wait=10, retries=10):
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

        # automatically retry
        if not retries:
            retries = 1

        for x in range(retries):
            while milli_now() < start + wait:
                if not parent:
                    parent = self.browser

                try:
                    if selector.startswith('#'):
                        elements = parent.find_elements_by_id(selector.replace('#', ''))
                    elif selector.startswith('.'):
                        elements = parent.find_elements_by_class_name(selector.replace('.', ''))
                    elif selector.startswith('//'):
                        elements = parent.find_elements_by_xpath(selector)
                    else:
                        funcs = [
                            parent.find_elements_by_tag_name,
                            parent.find_elements_by_name,
                            parent.find_elements_by_id,
                            parent.find_elements_by_css_selector,
                            parent.find_elements_by_link_text
                        ]

                        for f in funcs:
                            try:
                                elements = f(selector)
                                if elements:
                                    break
                            except NoSuchElementException:
                                pass

                    if elements:
                        for element in elements:
                            # ignore hidden form elements
                            if element.tag_name.lower() == 'input' and element.get_attribute('type') == 'hidden':
                                continue
                            return element

                except NoSuchElementException:
                    time.sleep(2)

        raise NoSuchElementException('Could not find element matching {}'.format(selector))

    def load(self, url):
        """
        Load the provided URL in the web browser.
        """
        self.browser.get(url)

    def click(self, selector):
        """
        Click on an element that's currently visble on the page. The element can be selected
        with a range of selectors:
            - .class_name
            - #element_id
            - element
            - //button[text()="Next"]
            - "Link Text"

        Example:

            - click: '//button[text()="Next"]'
        """
        element = self._get_element(selector)
        element.click()

    def submit(self, selector, *contents):
        """
        Fill out and submit a form. See `fill` for details.
        """
        form = self.fill(selector, *contents)
        form.submit()

    def fill(self, selector, *contents):
        """
        Fill out a form without submitting it.

        Provide a list where the first item is the selector to use to find a parent to the the form elements and
        all following items are <selector>: <value> pairs to be used to complete the form.

        The string `<random>` will be replaced with a random string, unique for each `fill` command.

        Use the `submit` function if you also want to submit the form.

        Example:

            - fill:
              - 'create-account'
              - username: 'testuser'
              - password: '<random>'
              - confirm_password: '<random'
        """
        r = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
        form = self._get_element(selector)
        for c in contents:
            for k, v in c.items():
                if '<random>' in v:
                    v = v.replace('<random>', r)
                    print(v)
                element = self._get_element(k, parent=form)
                element.send_keys(v)
        return form

    def send_keypress(self, keys):
        keys = getattr(Keys, keys, keys)
        element = self._get_element('body')
        element.send_keys(keys)

    def wait(self, seconds):
        """
        Wait for a specified number of seconds

        Example:

            - wait: 10
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

    def assert_text(self, text, selector='body'):
        """
        Assert that a piece of text exists on the currently displayed page.
        """
        self.wait(1)
        element = self._get_element(selector)

        if text not in element.text:
            text = ' '.join(element.text.splitlines())
            if len(text) > 30:
                text = text[:30] + '...'

            raise GhostlyTestFailed("{} not in {}".format(text, text))

    def assert_element(self, selector):
        """
        Ensure that at least one element exists that matches the selector
        """
        self.wait(1)
        element = self._get_element(selector)
        if not element:
            raise GhostlyTestFailed("no element matched {}".format(selector))

    def assert_value(self, selector, value):
        """
        Assert that the value of a form element is the provided value

        - assert_value:
          - "input"
          - "Hello World"
        """
        self.wait(1)
        element = self._get_element(selector)
        if element.get_attribute('value') != value:
            raise GhostlyTestFailed("{} != {}".format(element.get_attribute('value'), value))

    def assert_title(self, value):
        self.wait(1)
        if self.browser.title != value:
            raise GhostlyTestFailed("title is {} not {}".format(self.browser.title, value))

    def assert_url(self, url):
        self.wait(1)
        if self.browser.current_url != url:
            raise GhostlyTestFailed("url is {} not {}".format(self.browser.current_url, url))

    def screenshot(self, filename):
        filename, ext = filename.rsplit('.')
        filename = '{}_{}.{}'.format(filename, self.browser_name, ext)

        png_data = BytesIO(self.browser.get_screenshot_as_png())
        i = Image.open(png_data)
        i = i.crop((0, 0, self.width, self.height))
        i.save(filename)

    def scroll_to(self, y):
        self.browser.execute_script("window.scrollTo(0, {});".format(y))


def run_test(test, browser, tests, verbose=False, base_url=None):
    # we create a new Ghostly instance for each tests, keeps things nice and
    # isolated / ensures there is a clear cache
    width, height = [int(x) for x in test.get('screen_size', '1280x720').split('x')]
    g = Ghostly(browser, width, height)

    try:
        click.echo('\n[{}] {}:'.format(g.browser_name, test['name']))
        for step in test['test']:
            # print step
            for f, v in step.items():
                if f == 'load' and base_url:
                    v = base_url

                print('  - {} {}'.format(f, v), end="\r")
                func = getattr(g, f)
                if type(v) == list:
                    func(*v)
                else:
                    func(v)
                click.echo('  {} {} {}'.format(click.style("✔", fg='green'), f, v))

    # explicitly catch the possible error states and fail the test with an appropriate message
    except NoSuchElementException as e:
        fail(test['name'], "couldn't find element", e, verbose)
        passed = False
    except WebDriverException as e:
        fail(test['name'], "webdriver failed", e, verbose)
        passed = False
    except GhostlyTestFailed as e:
        fail(test['name'], e.message, e, verbose)
        passed = False
    else:
        click.echo(click.style("✔", fg='green') + " " + test['name'])
        passed = True
    finally:
        g.end()

    return passed

@click.command()
@click.argument('ghostly_files', type=click.File('rb'), nargs=-1)
@click.option('--verbose', is_flag=True)
@click.option('--base-url', default=None)
@click.option('--browser', default=None)
def run_ghostly(ghostly_files, verbose, base_url, browser):
    start = time.time()
    tests = {}
    passed = []
    failed = []

    for f in ghostly_files:
        test_yaml = yaml.load(f.read())
        for t in test_yaml:
            tests[t['name']] = t

    plural = len(tests) != 1 and "s" or ""
    click.echo('Running {} test{}...'.format(len(tests), plural))
    for test in tests.values():
        browsers = [browser, ] if browser else test.get('browsers', ['chrome',])
        for browser in browsers:
            print(browser)
            if run_test(test, browser, tests, verbose, base_url):
                passed.append(test)
            else:
                failed.append(test)

    stop = time.time()

    taken = float(stop - start)
    click.echo("Ran {} test{} in {:.2f}s".format(len(tests), plural, taken))

    if failed:
        sys.exit(1)


def fail(name, reason, exception=None, verbose=False):
    print('  ' + click.style("✘", fg='red'))  # mark the current (indented) test line as failed
    click.echo(click.style("✘", fg='red') + " {} ({})".format(name, reason))
    if verbose:
        click.echo(exception)


if __name__ == '__main__':
    run_ghostly()
