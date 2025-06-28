import factory.django

from apps.bot.models import UserInfo, ServerConfInfo


class UserInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserInfo


class ServerConfInfoFactory(factory.django.DjangoModelFactory):
    product = factory.SubFactory('shop.ProductFactory')

    class Meta:
        model = ServerConfInfo
