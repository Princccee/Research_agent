from rest_framework import serializers

class ResearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200, required=True)
