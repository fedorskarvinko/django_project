from django import forms
from django.core.exceptions import ValidationError

from catalog.models import Product

ban_words = [
    "казино",
    "биржа",
    "обман",
    "криптовалюта",
    "дешево",
    "полиция",
    "крипта",
    "бесплатно",
    "радар",
]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "purchase_price",
            "image",
            "is_published",
        ]

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)

        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите название"}
        )

        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите описание"}
        )

        self.fields["category"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Выберите категорию"}
        )

        self.fields["purchase_price"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите цену"}
        )

        self.fields["image"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Загрузите изображение"}
        )

    def clean_purchase_price(self):
        purchase_price = self.cleaned_data.get("purchase_price")
        if purchase_price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        return purchase_price

    def clean_name(self):
        """Проверяем название на отсутствие запрещенных слов."""
        name = self.cleaned_data["name"].lower()
        for word in ban_words:
            if word in name:
                raise ValidationError(f'Название содержит запрещенное слово: "{word}".')
        return name

    def clean_description(self):
        """Проверяем описание на отсутствие запрещенных слов."""
        description = self.cleaned_data.get("description", "").lower()
        for word in ban_words:
            if word in description:
                raise ValidationError(f'Описание содержит запрещенное слово: "{word}".')
        return description
