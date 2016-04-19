# Ghostly

### Running our sample tests

```shell
./ghostly.py google/search.yml
```


### Browser Stack

Use [this form](https://www.browserstack.com/automate/python#setting-os-and-browser) to create compatible combinations
of browser capabilities, then create a `remote` dict in your yaml file like this:

```
browsers:
  - remote:
      url: "http://<username>:<password>@hub.browserstack.com:80/wd/hub"
      os: "Windows"
      os_version: "10"
      browser: "IE"
      browser_version: "11"
      resolution: "1680x1050"
```
