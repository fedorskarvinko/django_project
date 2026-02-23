from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from catalog.models import Category, Product


class CatalogListView(ListView):
    model = Product
    queryset = Product.objects.order_by("-created_at")[:8]


class ContactView(TemplateView):
    template_name = "catalog/contacts.html"

    def get(self, request, *args, **kwargs):
        """Обработка GET запроса - показ формы"""
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        """Обработка POST запроса - получение данных формы"""
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        print(f"Новое сообщение от {name} ({email}): {message}")
        return HttpResponse(
            f"Спасибо, {name}! Ваше сообщение получено. Мы свяжемся с вами по {email}."
        )


class CatalogDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.name} - Детальная информация"
        return context


class ProductCreateView(CreateView):
    model = Product
    template_name = "catalog/product_create.html"
    fields = ["name", "description", "category", "purchase_price", "image"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy(
            "catalog:product_detail", kwargs={"product_id": self.object.id}
        )
