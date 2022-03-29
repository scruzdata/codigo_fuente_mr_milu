import base64
import datetime
import itertools
import math
import random
import statistics
import string
import uuid
from collections import defaultdict

import numpy as np
from django.contrib import admin
from django.core.files.base import ContentFile
from django.db import models
from django.db.models import Func, Aggregate, FloatField, JSONField
from django.utils import timezone

from code_setting.middleware import db_ctx


# # # # # BASE MODEL # # # # #

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(blank=True, null=True, db_index=True)
    calculation_vars = JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_id(self):
        return self.id.__str__()


# # # # # BASE ADMIN MODEL # # # # #

class MultiDBModelAdmin(admin.ModelAdmin):
    list_per_page = 20

    @property
    def db_name(self):
        return db_ctx.get()

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.db_name)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.db_name)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(MultiDBModelAdmin, self).get_queryset(request)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_foreignkey(db_field, request, using=self.db_name, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query on the 'other' database.
        return super(MultiDBModelAdmin, self).formfield_for_manytomany(db_field, request, using=self.db_name, **kwargs)

    # # # methods to format datetimes and dates # # #
    def get_date(self, obj):
        if obj.date:
            return obj.date.strftime("%d/%m/%Y")
        return ''

    def get_df_datetime(self, obj):
        if obj.df_datetime:
            return obj.df_datetime.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_data_datetime(self, obj):
        if obj.data_datetime:
            return obj.data_datetime.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_updated_at(self, obj):
        if obj.updated_at:
            return obj.updated_at.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_battery_datetime(self, obj):
        if obj.battery_datetime:
            return obj.battery_datetime.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_last_battery_date(self, obj):
        if obj.last_battery_date:
            return obj.last_battery_date.strftime("%d/%m/%Y %H:%M")
        return ''

    def get_manufacturing_date(self, obj):
        if obj.manufacturing_date:
            return obj.manufacturing_date.strftime("%d/%m/%Y")
        return ''

    get_date.short_description = 'date'
    get_df_datetime.short_description = 'df_datetime'
    get_data_datetime.short_description = 'data_datetime'
    get_created_at.short_description = 'created_at'
    get_updated_at.short_description = 'updated_at'
    get_battery_datetime.short_description = 'battery_datetime'
    get_last_battery_date.short_description = 'last_battery_date'
    get_manufacturing_date.short_description = 'manufacturing_date'


# # # # # BASE CLASS FOR CONSTANTS # # # # #

class ConstantEntity:

    def __init__(self, obj):
        self.id = obj[0]
        self.name = obj[1]

    def to_dict(self):
        return self.__dict__


# # # # # Func classes # # # # #

class Median(Aggregate):
    function = 'PERCENTILE_CONT'
    name = 'median'
    output_field = FloatField()
    template = '%(function)s(0.5) WITHIN GROUP (ORDER BY %(expressions)s)'

    def __rand__(self, other):
        pass

    def __ror__(self, other):
        pass


class ArrayLength(Func):
    function = 'CARDINALITY'

    def __rand__(self, other):
        pass

    def __ror__(self, other):
        pass


# # # # # GENERAL FUNCTIONS # # # # #

def get_configuration_variables(var_id, db=None):
    """
    Get configuration variable
    @param var_id: variable id
    @param db: database
    @return: variable value
    """

    from apps.core.models import ConfigurationVariable
    if not db:
        db = db_ctx.get()
    obj = ConfigurationVariable.objects.using(db).get(id=var_id)

    return obj.value / 100 if obj.is_percent else obj.value


def convert_str_to_datetime(s):
    """
    Convert str to datetime
    :param s: str ex: "31/12/2020 12:40" or "31/12/20 12:40"
    :return: datetime
    """
    try:
        # parse date with only 2 digits in year
        if len(s.split(' ')[0]) == 8:
            return datetime.datetime.strptime(s, "%d/%m/%y %H:%M")
        # parse date with 4 digits in year
        return datetime.datetime.strptime(s, "%d/%m/%Y %H:%M")
    except Exception:
        return None


def convert_str_to_date(s):
    """
    Convert str to date
    :param s: str ex: "31/12/2020"
    :return: date
    """
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y").date()
    except:
        return None


def convert_str_to_datetime_for_services(s):
    """
    Convert str to date
    :param s: str ex: "31/12/2020"
    :return: date
    """
    try:
        return datetime.datetime.strptime(s, "%d/%m/%Y")
    except:
        return timezone.now()


def convert_datetime_to_str(d):
    """
    Convert date to string
    :param d: date ex: 31/12/2020 12:40
    :return: string
    """
    try:
        return datetime.datetime.strftime(d, "%Y-%m-%dT%H:%M:%SZ")
    except:
        return None


def convert_date_to_str(d):
    """
    Convert date to string
    :param d: date ex: 31/12/2020
    :return: string
    """
    try:
        return datetime.datetime.strftime(d, "%d/%m/%Y")
    except:
        return None


def get_random_alphanumeric_string(chars):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=chars))


def get_file_from_base64(file):
    output, filestr = file.split(';base64,')
    return ContentFile(base64.b64decode(filestr), name=f'{get_random_alphanumeric_string(8)}.png')


def reject_outliers(data, m=2):
    """
    Function to remove outliers in a list
    @param data: list of data
    @param m: outlier thresholds m * np.std(data)
    @return: list data without outliers
    """
    if data:
        try:
            data = np.array(data)
            return data[abs(data - np.mean(data)) < m * np.std(data)].tolist()
        except:
            return None
    else:
        return None


def round_function(value):
    """
    Round value with 2 decimals
    :param value: value
    :return float
    """
    try:
        return round(value, 2) if value is not None and not math.isnan(value) and not math.isinf(value) else None
    except:
        return None


def round_function_4decimals(value):
    """
    Round value with 4 decimals
    :param value: value
    :return float
    """
    try:
        return round(value, 4) if value is not None and not math.isnan(value) and not math.isinf(value) else None
    except:
        return None


def calculate_trend(last_value, new_value):
    """
    Function to get "variable_trend" taking the last value calculated
    returns 1 if new_value > last_value, -1 if new_value < last_value, 0 if new_value == last_value
    :param last_value: Last variable value
    :param new_value: New variable value
    :return: int
    """
    if not last_value or not new_value or new_value == last_value:
        return 0
    elif new_value > last_value:
        return 1
    else:
        return -1


def calculate_deviation(items):
    """
    Function to calculate deviations in a list
    :param items: list
    :return: float
    """
    try:
        items = list(filter(None, items))
        return round(statistics.stdev(items), 2)
    except:
        return None


def calculate_deviation_power(items):
    """
    Function to calculate deviations in a list
    :param items: list
    :return: float
    """
    try:
        items = list(filter(None, items))
        return round(statistics.stdev(items), 4)
    except:
        return None


def calculate_idwr(distance_list, values_list):
    """Function to get the data with the Inverse Distance Weighting from the values of different positions
    :param distance_list: list of distances
    :param values_list: list of values measured by sensors
    :return calculated value
    """
    try:
        if distance_list:
            distances_without_none = [i for i, elem in enumerate(distance_list) if elem is None]
            for index in sorted(distances_without_none, reverse=True):
                del distance_list[index]
                del values_list[index]
            distances_0 = [i for i, elem in enumerate(distance_list) if elem == 0]
            if distances_0:
                sum_val = 0
                for i in distances_0:
                    sum_val += values_list[i]
                val = sum_val / len(distances_0)
            else:
                distance_inverse = list((1 / np.power(distance_list, 3)))
                suminf = np.sum(distance_inverse)
                temp_ponderation = np.array(distance_inverse) * np.array(values_list)
                sum_temp_ponderation = np.sum(temp_ponderation)
                val = sum_temp_ponderation / suminf
            return round_function(val)
    except Exception:
        return 0


def calculate_idwr_by_2_dict(list_distances, value_list):
    """
    Function to join 2 dictionaries with similar key value "rack__id" and get the data with the Inverse Distance
    Weighting

    example:
    list_distances = [{'rack__id': id1, 'dist': 4.05}, {'rack__id': id2, 'dist': 2.55}]
    value_list = [{'rack__id': id1, 'median': 21.215}, {'rack__id': id2, 'median': 16.73}}]
    result = [{'rack__id': id1, 'dist': 4.05,'median': 21.215 }, {'rack__id': id2, 'dist': 2.55, 'median': 16.73}]

    @param list_distances: list of distances
    @param value_list: list of values
    @return: calculated weighted value
    """
    try:
        d = defaultdict(dict)
        for elem in itertools.chain(list_distances, value_list):
            d[elem['relatedtable1_id']].update(elem)

        return_values_list = list(d.values())
        distances_return = list(x['dist'] for x in return_values_list)
        temp_return = list(x['median'] for x in return_values_list)
        value = round_function(calculate_idwr(distances_return, temp_return))
        return value
    except Exception:
        return None


def closest_node(node, nodes_list, ratio):
    """
    Calculate distance between 1 node to node list
    @param node: main node -> (x,y,z)
    @param nodes_list: [(x,y,z),(x,y,z),(x,y,z)...]
    @param ratio: max distance in meters
    @return: boolean list inside ratio main node
    """

    nodes = np.asarray(nodes_list)
    distance_node_allnodes = list(np.sum((nodes - node) ** 2, axis=1))
    sqrt_distances = [math.sqrt(x) for x in distance_node_allnodes]
    list_index_closest_nodes = [x < ratio for x in sqrt_distances]
    index_closest_node = np.argmin(sqrt_distances)
    return list_index_closest_nodes, index_closest_node


class AddParamsToStr(dict):
    def __missing__(self, key):
        return '{' + key + '}'


