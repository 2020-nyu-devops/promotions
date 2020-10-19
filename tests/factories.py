"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Promotion, Product, PromoType


class PromotionFactory(factory.Factory):
    """ Creates fake promotions """

    class Meta:
        model = Promotion

    id = factory.Sequence(lambda n: n)
    title = "title"
    description = "description"
    promo_code = "promo_code"
    promo_type = FuzzyChoice(choices=[PromoType.BOGO, PromoType.DISCOUNT, PromoType.FIXED])
    amount = 10
    start_date = "Sat, 17 Oct 2020 00:00:00 GMT"
    end_date = "Sun, 18 Oct 2020 00:00:00 GMT"
    is_site_wide = True
