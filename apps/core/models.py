from django.db import models

from utils.constants import (CHOISES_CLASSES, CHOISE_0, CHOISE_1)
from utils.helpers import (BaseModel)


class Country(BaseModel):
    code = models.CharField(max_length=100, blank=True, null=True, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        db_table = 'countries'
        ordering = ('name',)


class Table1(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    country = models.ForeignKey(Country, blank=True, null=True, on_delete=models.SET_NULL)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    custom_recommended_operation_limit_area = models.JSONField(blank=True, null=True)
    custom_allowed_operation_limit_area = models.JSONField(blank=True, null=True)
    area_recommended_operation = models.SmallIntegerField(choices=CHOISES_CLASSES, default=CHOISE_0)
    area_allowed_operation = models.SmallIntegerField(choices=CHOISES_CLASSES, default=CHOISE_1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Table1'
        verbose_name_plural = 'Tables1'
        db_table = 'core_table1'


class RelatedTable1(BaseModel):
    table1 = models.ForeignKey(Table1, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    x_max = models.FloatField(blank=True, null=True, verbose_name='Xmax (m)')
    y_max = models.FloatField(blank=True, null=True, verbose_name='Ymax (m)')
    z_max = models.FloatField(blank=True, null=True, verbose_name='Zmax (m)')
    square_size = models.PositiveSmallIntegerField(blank=True, null=True)
    building = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.table1.name} - {self.name}"

    class Meta:
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'
        db_table = 'core_rooms'
        unique_together = ('table1', 'name')

    def get_my_related_table2(self):
        return self.related_table2_set.all()


class RelatedTable2(BaseModel):
    related_table1 = models.ForeignKey(RelatedTable1, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    cold_pos = models.FloatField(blank=True, null=True, verbose_name='Cold Position (m)')
    hot_pos = models.FloatField(blank=True, null=True, verbose_name='Hot Position (m)')
    cold_row_temperature_median = models.FloatField(blank=True, null=True)
    hot_row_temperature_median = models.FloatField(blank=True, null=True)
    hot_row_pressure_median = models.FloatField(blank=True, null=True)
    cold_row_pressure_median = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.related_table1}"

    class Meta:
        verbose_name = 'Row'
        verbose_name_plural = 'Rows'
        db_table = 'core_rows'
        unique_together = ('related_table1', 'name')

    def get_my_related_table3(self):
        return self.related_table3_set.all()

    def get_my_related_table3_by_db(self, db):
        return self.related_table3_set.using(db).all()

    def get_my_data(self):
        return Data.objects.filter(unit__rack__row=self)


class RelatedTable3(BaseModel):
    related_table2 = models.ForeignKey(RelatedTable2, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, default=CHOISE_0)
    total_units = models.PositiveSmallIntegerField(default=40)
    x_center = models.FloatField(blank=True, null=True, verbose_name='Xcenter (m)')
    y_center = models.FloatField(blank=True, null=True, verbose_name='Ycenter (m)')
    x_size = models.FloatField(blank=True, null=True, verbose_name='Xsize (m)')
    y_size = models.FloatField(blank=True, null=True, verbose_name='Ysize (m)')
    power_on = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Rack'
        verbose_name_plural = 'Racks'
        db_table = 'core_racks'
        unique_together = ('related_table2', 'name')


class Data(BaseModel):
    mac_address = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    source = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, blank=True, null=True)
    type = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, blank=True, null=True)
    firmware_version = models.CharField(max_length=32, blank=True, null=True)

    # Location
    x = models.FloatField(blank=True, null=True)
    y = models.FloatField(blank=True, null=True)
    z = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.mac_address} ({self.get_source_display()})'

    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensors'
        db_table = 'core_sensors'
        unique_together = (('source', 'unit', 'x', 'y'),
                           ('mesh', 'unicast_address'))


class ConfigurationVariable(BaseModel):
    element = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, blank=True, null=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=250, blank=True, null=True)
    value = models.FloatField()
    default = models.FloatField(blank=True, null=True)
    is_percent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.value})"

    class Meta:
        verbose_name = 'Configuration Variable'
        verbose_name_plural = 'Configuration Variables'
        db_table = 'core_configuration_variables'


class Feedback(BaseModel):
    created_by = models.CharField(max_length=255, db_index=True)
    rating = models.FloatField(default=0)
    type = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, default=CHOISE_0)
    comment = models.TextField(blank=True, null=True)
    component = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, blank=True, null=True)
    page = models.PositiveSmallIntegerField(choices=CHOISES_CLASSES, blank=True, null=True)

    def __str__(self):
        return f"{self.created_by} - {self.get_type_display()}"

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        db_table = 'core_feedbacks'
        ordering = ('-created_at', )


class Event(BaseModel):
    created_by = models.CharField(max_length=255, blank=True, null=True)
    table1 = models.ForeignKey(Table1, blank=True, null=True, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.id}({self.created_by})"

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        db_table = 'core_events'
        ordering = ('-created_at', )


class Files(BaseModel):
    name = models.CharField(max_length=50, blank=True, null=True)
    file = models.FileField(max_length=100, upload_to='files', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'
        db_table = 'files'
        ordering = ('type', )
