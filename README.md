# prawler

Prawler scrapes product data from sites into JSON files.

## Install

    pip install -r requirements.txt

## Site config files

Prawler uses CSS selectors to recognize and scrape product pages from each site.
To add a new site, create a JSON file with the following structure:

```json
{
  "domain": "localhost",
  "selectors": {
    "name": "span#name",
    "number": "span#number",
    "image": "div#left div img",
    "description": "div#description p"
  }
}
```
## Usage

    ./crawl.py example-sites
