from django import forms
from django.core import validators
from django.db import models

from . import util

color_validator = validators.RegexValidator("^#?[0-9A-F]{3,6}$")


class ColorField(models.CharField):
    default_validators = [color_validator]

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs.setdefault("max_length", 7)
        kwargs.setdefault("default", util.color)
        super().__init__(verbose_name, name, **kwargs)

    def formfield(self, **kwargs):
        kwargs["widget"] = forms.TextInput(attrs={"type": "color"})
        return super().formfield(**kwargs)
