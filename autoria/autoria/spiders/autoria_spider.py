import scrapy
from time import sleep
import random


# spider for auto.ria.com
class AutoriaSpider(scrapy.Spider):
    name = 'autoria'

    def start_requests(self):
        for page in range(0, 123):
            url = f'https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&year[0].gte=2015&year[0].lte=2023&categories.main.id=1&brand.id[0]=47&country.import.usa.not=-1&price.currency=1&abroad.not=0&custom.not=1&page={page}&size=10'
            # sleep for random time to avoid getting blocked within a short period of time (1-3 seconds)
            sleep(random.randint(1, 3))
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        all_listings = response.css('div.content')
        for mazda in all_listings:
            # check if title exists (banners don't have title)
            if mazda.css('a.address::attr(title)').get() is None:
                continue
            url = mazda.css('a::attr(href)').get()
            title_list = mazda.css('a.address::attr(title)').get().split()
            brand = title_list[0]
            model = title_list[1]
            year = title_list[2]
            price_usd = mazda.css('span.bold.green.size22[data-currency="USD"]::text').get().replace(' ', '')
            price_uah = mazda.css('span.i-block span[data-currency="UAH"]::text').get().replace(' ', '')
            mileage = mazda.css('li.item-char:nth-child(1)::text').get().strip()
            location = mazda.css('li.item-char:nth-child(2)::text')[1].get().strip()
            engine = mazda.css('li.item-char:nth-child(3)::text').get().strip()
            transmission = mazda.css('li.item-char:nth-child(4)::text').get().strip()

            # check if description exists (some listings don't have description)
            if mazda.css('p.descriptions-ticket span::text').get() is None:
                description = ''
            else:
                description = mazda.css('p.descriptions-ticket span::text').get().strip()

            # check if state_num exists (some listings don't have state_num)
            if mazda.css('span.state-num.ua::text').get() is None:
                state_num = ''
            else:
                state_num = mazda.css('span.state-num.ua::text').get().strip()

            mazda_data = {
                'url': url,
                'brand': brand,
                'model': model,
                'year': year,
                'price_usd': price_usd,
                'price_uah': price_uah,
                'mileage': mileage,
                'location': location,
                'engine': engine,
                'transmission': transmission,
                'state_num': state_num,
                'description': description,
            }

            yield mazda_data
