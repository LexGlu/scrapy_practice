from scrapy import Spider
from random_settings import get_user_agent, get_random_delay


class AlloSpider(Spider):
    """
    Scrapy spider for scraping products from allo.ua from different categories.
    To alter categories, change the start_urls list, but make sure that the URL matches the following pattern:
    - https://allo.ua/ua/<category_path>/p-1/seller-allo/

    Data is saved to allo_products.jsonl file.
    """
    name = 'allo'
    allowed_domains = ['allo.ua']
    start_urls = [
        'https://allo.ua/ua/products/mobile/p-1/seller-allo/',
        'https://allo.ua/ua/televizory/p-1/seller-allo/',
        'https://allo.ua/ua/igrovye-pristavki/p-1/seller-allo/',
        'https://allo.ua/ua/products/notebooks/p-1/seller-allo/',
        'https://allo.ua/ua/products/internet-planshety/p-1/seller-allo/',
        'https://allo.ua/ua/monitory/p-1/seller-allo/',
    ]

    custom_settings = {
        'FEED_FORMAT': 'jsonlines',
        'FEED_URI': 'allo_products.jsonl',
        'LOG_FILE': 'allo_products.log',
        'USER_AGENT': get_user_agent(),
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': get_random_delay(),
    }

    def parse(self, response, **kwargs):
        products = response.css('div.product-card')
        category = response.css('span.b-crumbs__link::text').get()
        for product in products:
            product_sku = product.css('span.product-sku__value::text').get()
            product_url = product.css('div.product-card__content a::attr(href)').get()
            product_image_url = product.css('img.gallery__img::attr(data-src)').get()
            product_name = product.css('div.product-card__content a::attr(title)').get()

            product_price_old_uah = product.css('div.v-pb__old span.sum::text').get('').replace(' ', '')
            product_price_current_uah = product.css('div.v-pb__cur span.sum::text').get('').replace(' ', '')

            product_in_stock = product.css('div.v-pb__text::text').get('')
            if not product_in_stock:
                product_in_stock = product.css('div.v-pb span.v-pb__text').get('')
                if not product_in_stock:
                    product_in_stock = product.css('div.v-pb span.v-pb__text::text').get('')

            description_string = product.css('div.product-card__detail dl').get('')
            if description_string:
                description = product.css('div.product-card__detail dl')
                # extract all the keys and values from the description
                description_keys = description.css('dt::text').getall()
                description_values = description.css('dd::text').getall()
                # create a JSON object from the keys and values
                description_object = dict(zip(description_keys, description_values))
            else:
                description_object = {}

            phone_data = {
                'category': category,
                'product_sku': product_sku,
                'product_url': product_url,
                'product_img_url': product_image_url,
                'product_name': product_name,
                'product_price_old_uah': product_price_old_uah,
                'product_price_current_uah': product_price_current_uah,
                'product_in_stock': product_in_stock,
                'product_description': description_object,
            }

            yield phone_data

        # follow pagination link
        next_page = response.css('div.pagination__next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
