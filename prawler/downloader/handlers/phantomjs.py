from scrapy.http import Headers, HtmlResponse
from scrapy.utils.decorator import inthread
from selenium import webdriver

class PhantomJSDownloadHandler(object):
    def __init__(self, settings):
        pass

    @inthread
    def download_request(self, request, spider):
        args = ['--ignore-ssl-errors=true', '--load-images=false']
        # Remove 'phantomjs-' prefix
        url = request.url[10:]

        driver = webdriver.PhantomJS(service_args=args)

        driver.get(url)
        body = driver.find_element_by_xpath('//*').get_attribute("outerHTML")
        driver.quit()

        # Set header so httpcache chooses the appropriate Response class
        headers = Headers({'Content-Type': 'text/html'})
        body = body.encode('utf-8')

        return HtmlResponse(url=url, headers=headers, body=body)
