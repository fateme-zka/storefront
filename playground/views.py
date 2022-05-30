from django.shortcuts import render
from django.http import HttpResponse

from tags.models import TaggedItem, Tag
from store.models import (Product,
                          OrderItem,
                          Order,
                          Customer,
                          Collection,
                          Cart,
                          CartItem)


def say_hello(request):
    queryset = Product.objects.all()
    return render(request, 'hello.html', {'queryset': queryset})
