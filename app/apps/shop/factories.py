import random
from decimal import Decimal

import factory.django

from apps.shop.models import Purchase, PriceDuration, Product, Discount, Payment, PaySystem, Subscription


class DiscountFactory(factory.django.DjangoModelFactory):
    percent = factory.LazyFunction(lambda: random.choice(range(5, 101, 5)))

    class Meta:
        model = Discount


class PaySystemFactory(factory.django.DjangoModelFactory):
    class_name = factory.Sequence(lambda n: f"PaySystem_{n}")

    class Meta:
        model = PaySystem


class ProductFactory(factory.django.DjangoModelFactory):
    base_price = factory.LazyFunction(lambda: random.choice(range(50, 250, 25)))

    class Meta:
        model = Product


class PriceDurationFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory(ProductFactory)
    discount = factory.SubFactory(DiscountFactory)

    class Meta:
        model = PriceDuration


class SubscriptionFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('bot.UserInfoFactory')
    server = factory.SubFactory('bot.ServerConfInfoFactory')

    class Meta:
        model = Subscription


class PurchaseFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('bot.UserInfoFactory')
    product = factory.SubFactory('shop.ProductFactory')
    price_duration = factory.SubFactory('shop.PriceDurationFactory')

    class Meta:
        model = Purchase


class PaymentFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory('bot.UserInfoFactory')
    purchase = factory.SubFactory('shop.PurchaseFactory')
    pay_system = factory.SubFactory('shop.PaySystemFactory')

    class Meta:
        model = Payment
