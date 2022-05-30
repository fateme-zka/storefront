from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class TaggedItemManager(models.Manager):
    def get_tags_for(self, obj_type, obj_id):  # obj_type is the model of our object
        # this content_type object represent the 12th record of django_content_type table(which was record of Product table in db)
        content_type = ContentType.objects.get_for_model(obj_type)
        return TaggedItem.objects.select_related('tag') \
            .filter(content_type=content_type, object_id=obj_id)


class Tag(models.Model):
    label = models.CharField(max_length=255)


class TaggedItem(models.Model):
    objects = TaggedItemManager()
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

