from scrapy.item import Item, Field

class Product(Item):
    description = Field()
    discountcode = Field()
    image = Field()
    name = Field()
    number = Field()
    pricing = Field()
    title = Field()
    url = Field()
