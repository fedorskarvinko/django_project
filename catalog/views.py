from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from catalog.forms import ProductForm
from catalog.models import Product, Category


class ContactsView(TemplateView):
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


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"

    # queryset = Product.objects.order_by("-created_at")[:8]

    def get_queryset(self):
        queryset = cache.get("product_queryset")
        if not queryset:
            queryset = super().get_queryset()
            cache.set(
                "product_queryset", queryset, 60 * 15
            )  # Кешируем данные на 15 минут
        return queryset


@method_decorator(cache_page(60 * 15), name="dispatch")
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = f"{self.object.name} - Детальная информация"
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"

    def get_success_url(self):
        return reverse_lazy(
            "catalog:product_detail", kwargs={"pk": self.object.id}
        )

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    pk_url_kwarg = "pk"

    def test_func(self):
        product = self.get_object()
        return product.owner == self.request.user

    def form_valid(self, form):
        if "is_published" in form.changed_data and not form.instance.is_published:
            if not self.request.user.has_perm("catalog.can_unpublish_product"):
                messages.error(self.request, "У вас нет прав на отмену публикации")
                return redirect("catalog:product_detail", pk=self.object.pk)

        messages.success(self.request, "Продукт успешно обновлен!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "catalog:product_detail", kwargs={"pk": self.object.id}
        )


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("catalog:product_list")

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return product.owner == user or user.has_perm("catalog.delete_product")


class CategoryProductListView(ListView):
    model = Category
    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        from django.shortcuts import get_object_or_404
        from .services import get_products_by_category

        self.category = get_object_or_404(Category, id=self.kwargs["category_id"])
        return get_products_by_category(self.category.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context
