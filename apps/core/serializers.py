from rest_framework import serializers

from apps.core.models import Table1, Feedback, Country, Event


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = ('id', 'code', 'name_en', 'name_es', 'name_pt', 'created_at')


class Table1Serializer(serializers.ModelSerializer):
    country = CountrySerializer()

    class Meta:
        model = Table1
        fields = ('id', 'name', 'country', 'area_recommended_operation',
                  'area_allowed_operation', 'is_active', 'created_at')


class FeedbackSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    component = serializers.SerializerMethodField()
    page = serializers.SerializerMethodField()

    class Meta:
        model = Feedback
        fields = ('id', 'created_by', 'rating', 'type', 'comment', 'component', 'page', 'created_at')

    @staticmethod
    def get_type(obj):
        if obj.type:
            return {
                'id': obj.type,
                'name': obj.get_type_display()
            }
        return None

    @staticmethod
    def get_component(obj):
        if obj.component:
            return {
                'id': obj.component,
                'name': obj.get_component_display()
            }
        return None

    @staticmethod
    def get_page(obj):
        if obj.page:
            return {
                'id': obj.page,
                'name': obj.get_page_display()
            }
        return None


class EventSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('id', 'created_by', 'table', 'text', 'created_at', 'updated_at')


class EventLiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event
        fields = ('text',)