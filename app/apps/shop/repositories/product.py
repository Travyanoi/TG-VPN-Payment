from typing import Optional, List

from apps.shop.models import Product
from apps.shop.domain.product import ProductEntity
from apps.bot.repositories.base import BaseRepository


class ProductRepository(BaseRepository[ProductEntity]):
    def get_by_id(self, pk: int) -> Optional['ProductEntity']:
        try:
            instance = Product.objects.get(pk=pk)
            return ProductEntity.from_model(instance)
        except Product.DoesNotExist:
            return None

    def all(self) -> Optional[List['ProductEntity']]:
        try:
            instances = Product.objects.all()
            return [ProductEntity.from_model(instance) for instance in instances]
        except Product.DoesNotExist:
            return None

    def create(self, **kwargs) -> ProductEntity:
        instance = Product.objects.create(**kwargs)
        return ProductEntity.from_model(instance)

    def save(self, entity: 'ProductEntity') -> ProductEntity:
        instance, _ = Product.objects.update_or_create(
            pk=entity.pk,
            defaults={
                "name": entity.name,
                "description": entity.description,
                "base_price": entity.base_price,
                "is_active": entity.is_active,
            },
        )
        return ProductEntity.from_model(instance)

    def delete(self, entity: 'ProductEntity') -> None:
        Product.objects.filter(pk=entity.pk).delete()
