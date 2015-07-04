import unittest
from prawler.spiders.product import ProductSpider
from scrapy.http import HtmlResponse

class TestProductSpider(unittest.TestCase):

    def setUp(self):
        self.spider = ProductSpider('test/example.com.json')

    def test_json_import(self):
        config = {
            u'name': u'body div#name',
            u'description': u'body div#description',
            u'image': u'body div#image img',
            u'number': u'body div#number',
        }

        self.assertEqual('example.com', self.spider.name),
        self.assertEqual('example.com', self.spider.allowed_domains[0])
        self.assertEqual('http://www.example.com/', self.spider.start_urls[0])
        self.assertEqual(config, self.spider.selectors)

    def test_parse(self):
        html = HtmlResponse('http://www.example.com/product.html',
            body=(
                '<html><head><title>Product</title></head>'
                '<body>'
                '<div id="name">Name</div>'
                '<div id="description">Description</div>'
                '<div id="pricing">'
                '<table>'
                '<tr><th></th><th>50</th><th>100</th><th>Discount</th></tr>'
                '<tr><td>P01</td><td>$1.50</td><td>$1.25</td><td>3C</td></tr>'
                '</table>'
                '</div>'
                '<div id="image"><img src="image.png"/></div>'
                '<div id="number">P01</div>'
                '</body></html>'
            )
        )

        product = next(self.spider.parse_product(html))

        self.assertEqual('Name', product['name'])
        self.assertEqual('Description', product['description'])
        self.assertEqual('P01', product['number'])
        self.assertEqual('3C', product['discountcode'])
        self.assertEqual([
            {
                'name': u'P01',
                'columns': [
                    { 'price': '1.50', 'quantity': '50' },
                    { 'price': '1.25', 'quantity': '100' }
                ]
            }
        ], product['pricing'])
        self.assertEqual('http://www.example.com/image.png', product['image'])

if __name__ == '__main__':
    unittest.main()
