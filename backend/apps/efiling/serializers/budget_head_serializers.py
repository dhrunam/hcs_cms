from rest_framework import serializers

from apps.core.models import BudgetHeadT


class BudgetHeadTSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetHeadT
        fields = '__all__'