from rest_framework import serializers
from apps.core.models import DocumentIndex

class DocumentIndexSerializer(serializers.ModelSerializer):
  
    class Meta:
        model = DocumentIndex
        fields =('id','name',"case_type", "for_new_filing", "fee_amount")
