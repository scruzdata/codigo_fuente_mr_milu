from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, ChoiceDropdownFilter, DropdownFilter

from utils.helpers import MultiDBModelAdmin

CORE_MODELS_ADMIN = {}


class CountryAdmin(MultiDBModelAdmin):
    list_display = ('code', 'name', 'id', 'get_created_at')
    search_fields = ('code', 'name')
    list_filter = ('name', )
    ordering = ('code',)


class Table1Admin(MultiDBModelAdmin):
    list_display = ('name', 'country', 'latitude', 'longitude',
                    'area_recommended_operation', 'area_allowed_operation',
                    'is_active', 'get_created_at', 'id')
    search_fields = ('id', 'name')
    ordering = ('name', )


class RelatedTable1Admin(MultiDBModelAdmin):
    list_display = ('name', 'table1', 'x_max', 'y_max', 'z_max',
                    'square_size', 'building', 'get_created_at', 'id')
    search_fields = ('id', 'name', 'building')
    list_filter = ('table1', )
    ordering = ('table1', 'name')


class RelatedTable2Admin(MultiDBModelAdmin):
    list_display = ('name', 'related_table2', 'is_horizontal', 'cold_pos', 'hot_pos', 'get_created_at', 'id')
    search_fields = ('id', 'name')
    list_filter = ('related_table2', )
    ordering = ('related_table2', 'name')


class RelatedTable3Admin(MultiDBModelAdmin):
    list_display = ('name', 'type', 'power_on', 'x_center', 'y_center', 'x_size', 'y_size',
                    'get_created_at', 'get_updated_at', 'id')
    search_fields = ('id', 'name')
    list_filter = ('related_table2__related_table1__table1', )
    ordering = ('related_table2', 'name')

    def get_count_of_data(self, obj):
        return obj.data_set.count()

    get_count_of_data.short_description = 'Shortname'


class DataAdmin(MultiDBModelAdmin):
    list_display = ('mac_address', 'name', 'source', 'x', 'y', 'z',
                    'type', 'firmware_version',
                    'table1', 'related_table1', 'related_table2', 'related_table3',
                    'get_created_at', 'id')
    search_fields = ('id', 'name', 'mac_address')
    list_filter = ('table1', 'related_table1', ('source', ChoiceDropdownFilter),
                   ('related_table2', RelatedDropdownFilter), ('related_table3', RelatedDropdownFilter))
    ordering = ('source', 'name', 'mac_address')


class FeedbackAdmin(MultiDBModelAdmin):
    list_display = ('get_created_at', 'created_by', 'page', 'component', 'type', 'rating', 'comment')
    search_fields = ('created_by', 'comment')
    list_filter = ('page', 'component', 'type', 'rating')


class EventAdmin(MultiDBModelAdmin):
    list_display = ('id', 'created_by', 'table1', 'text', 'created_at', 'updated_at')
    search_fields = ('created_by', 'text')
    list_filter = ('created_by', )


CORE_MODELS_ADMIN.update({'Country': CountryAdmin})
CORE_MODELS_ADMIN.update({'Feedback': FeedbackAdmin})
CORE_MODELS_ADMIN.update({'Event': EventAdmin})

CORE_MODELS_ADMIN.update({'Table1': Table1Admin})
CORE_MODELS_ADMIN.update({'RelatedTable1': RelatedTable1Admin})
CORE_MODELS_ADMIN.update({'RelatedTable2': RelatedTable2Admin})
CORE_MODELS_ADMIN.update({'RelatedTable3': RelatedTable3Admin})
CORE_MODELS_ADMIN.update({'Data': DataAdmin})

