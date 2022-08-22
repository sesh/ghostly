# Ghostly

## Installation

```shell
> pip install -U git+https://github.com/sesh/ghostly
```

### Running the sample tests

```shell
> ./ghostly.py google/search.yml
```

---

The actions and asserts available in ghostly are simple and straight forward. Check the source for better documentation.

## Actions

- load <url>
- click <selector>
- fill <selector> <contents>
- submit <selector> <contents>
- wait <time>
- switch_to <selector>
- navigate <back|forward>
- dump <selector>
- screenshot <filename>

## Asserts

- assert_text <text> <parent-selector>
- assert_not_text <text> <parent-selector>
- assert_element <selector>
- assert_value <selector> <value>
- assert_title <value>
- assert_url <url>

## Browsers

Currently ghostly supports running tests with one or more of `chrome` (via chromedriver), `firefox` and `phantomjs`.

### Browser Stack

Use [this form](https://www.browserstack.com/automate/python#setting-os-and-browser) to create compatible combinations
of browser capabilities, then create a `remote` dict in your yaml file like this:

```yaml
browsers:
  - remote:
      url: "http://<username>:<password>@hub.browserstack.com:80/wd/hub"
      os: "Windows"
      os_version: "10"
      browser: "IE"
      browser_version: "11"
      resolution: "1680x1050"
```
