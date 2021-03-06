"""
Test Factory to make fake objects for testing
"""
from datetime import datetime
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion, PromoType, Product


class ProductFactory(factory.Factory):
    """ Creates fake products """

    class Meta:
        model = Product

    id = factory.Sequence(lambda n: n * 100)


class PromotionFactory(factory.Factory):
    """ Creates fake promotions """

    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n * 100)
    title = "title"
    description = "description"
    promo_code = "promo_code"
    promo_type = FuzzyChoice(
        choices=[PromoType.BOGO, PromoType.DISCOUNT, PromoType.FIXED]
    )
    amount = 10
    start_date = datetime(2020, 10, 17)
    end_date = datetime(2020, 10, 18)
    is_site_wide = True
