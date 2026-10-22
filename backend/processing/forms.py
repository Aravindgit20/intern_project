from django import forms
from .models import RawMaterial


class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterial
        fields = ['material_type', 'quantity']