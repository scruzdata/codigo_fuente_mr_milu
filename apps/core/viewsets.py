from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.core.models import (Country, Table1, Feedback, Event, Files)
from apps.core.serializers import Table1Serializer, FeedbackSerializer, EventLiteSerializer, \
    EventSerializer
from utils.constants import CHOISES_CLASSES, DYNAMIC_HELP
from utils.helpers import convert_str_to_date


class TableViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):

    queryset = Table1.objects.all()
    serializer_class = Table1Serializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                now = timezone.now()

                name = request.data.get('name', '')
                if not name:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'name is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                country_code = request.data.get('country_code', None)
                if not country_code:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'country_code is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)
                try:
                    country = Country.objects.get(code=country_code)
                except Country.DoesNotExist:
                    return Response({
                        'result': 'ERROR',
                        'detail': f'Country does not exist for country_code: {country_code}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                latitude = request.data.get('latitude', None)
                if latitude is None:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'latitude is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                longitude = request.data.get('longitude', None)
                if longitude is None:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'longitude is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                area_recommended_operation = request.data.get('area_recommended_operation', None)
                if area_recommended_operation is None:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'area_recommended_operation is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                area_allowed_operation = request.data.get('area_allowed_operation', None)
                if area_allowed_operation is None:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'area_allowed_operation is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                table1 = Table1(name=name,
                                country=country,
                                latitude=latitude,
                                longitude=longitude,
                                area_recommended_operation=area_recommended_operation,
                                area_allowed_operation=area_allowed_operation,
                                created_at=now,
                                updated_at=now)
                table1.save()

                return Response({
                    'result': 'OK',
                    'detail': 'Table1 succesfully created!',
                    'id': table1.get_id()
                }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True)
    def structure(self, request, *args, **kwargs):
        try:
            table1_id = kwargs['pk']
            if not table1_id:
                return Response({
                    'result': 'ERROR',
                    'detail': 'table1_id is missing or empty'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                table1_id = Table1.objects.get(id=table1_id)
            except Table1.DoesNotExist:
                return Response({
                    'result': 'ERROR',
                    'detail': f'Table1 does not exist for table1_id: {table1_id}'
                }, status=status.HTTP_400_BAD_REQUEST)

            results = []
            data_list = []
            for obj in table1_id.relatedtable1_set.all():
                daat2_list = []
                for int_obj in obj.relatedtable2_set.all():
                    data3_list = []
                    for int_obj2 in int_obj.relatedtable3_set.all():
                        data3_list.append(Table1Serializer(int_obj2).data)

                    daat2_list.append({
                        'name': int_obj.name,
                        'id': int_obj.id,
                        'is_horizontal': int_obj.is_horizontal,
                        'cold_pos': int_obj.cold_pos,
                        'hot_pos': int_obj.hot_pos,
                        'racks': data3_list
                    })

                data_list.append({
                    'name': obj.name,
                    'id': obj.id,
                    'rows': daat2_list
                })

            results.append({'data': data_list})

            return Response({
                'result': 'OK',
                'detail': 'Structure succesfully listed!',
                'results': results
            }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)


class FeedbackViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():

                comment = request.data.get('comment', '')
                if not comment:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'comment is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                page = request.data.get('page', None)
                if not page:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'page is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                rating = round(request.data.get('rating', 0), 2)
                type = request.data.get('type', CHOISES_CLASSES)
                component = request.data.get('component', None)
                now = timezone.now()

                feedback = Feedback(created_by=request.user.email,
                                    rating=rating,
                                    type=type,
                                    comment=comment,
                                    component=component,
                                    page=page,
                                    created_at=now,
                                    updated_at=now)
                feedback.save()

                return Response({
                    'result': 'OK',
                    'detail': 'Feedback saved!'
                }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)


class DynamicHelpViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):
        try:
            ui_component = int(request.GET.get("ui_component", 0))
            if not ui_component:
                return Response({
                    'result': 'ERROR',
                    'detail': 'ui_component is required'

                }, status=status.HTTP_400_BAD_REQUEST)

            result = DYNAMIC_HELP[ui_component]
            try:
                image = Files.objects.get(name=result['text1']['image'])
                for key, value in result.items():
                    if value['image'] == image.name:
                        value['image'] = f"{image.file.url}" if image.file else None
            except:
                image = ''

            return Response({
                'result': result,

            }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):

    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def list(self, request, *args, **kwargs):
        try:
            table1 = Table1.objects.get(id=kwargs['table1_pk'])
            query = str(request.GET.get("q", ''))
            date_txt = request.GET.get('date', None)

            if not date_txt and not query:
                docs = Event.objects.filter(table1=table1).order_by('-created_at')[:10]

            elif date_txt and query:
                date = convert_str_to_date(date_txt)
                vector = SearchVector(f'text', weight='A',)
                searchquery = SearchQuery(query)
                docs = Event.objects.filter(created_at__date=date, table1=table1).annotate(rank=SearchRank(vector, searchquery)).filter(rank__gte=0.1)

            elif date_txt and not query:
                date = convert_str_to_date(date_txt)
                docs = Event.objects.filter(created_at__date=date, table1=table1)

            else:
                vector = SearchVector(f'text', weight='A', )
                searchquery = SearchQuery(query)
                docs = Event.objects.annotate(rank=SearchRank(vector, searchquery)).filter(rank__gte=0.1)[:5]

            if not docs:
                docs = Event.objects.filter(table1=table1).order_by('-created_at')[:5]

            results = []
            for result in docs:
                text_id = result.id
                text = result.text
                created_at = result.created_at.date()

                results.append({"id": text_id,
                                "text": text,
                                "created_at": created_at
                                })

            return Response({
                'result': results
            }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():

                table1 = Table1.objects.get(id=kwargs['table_pk'])
                text = request.data.get('text', '')
                if not text:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'text is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                date_txt = request.data.get('date', '')
                if not date_txt:
                    date_txt = timezone.now()

                event = Event(created_by=request.user.email,
                              table1=table1,
                              text=text,
                              created_at=date_txt,
                              updated_at=date_txt)
                event.save()

                return Response({
                    'result': 'OK',
                    'detail': 'Event saved!'
                }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                event_id = kwargs.get('pk', '')
                if not event_id:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'event_id is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                text = request.data.get('text', '')
                if not text:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'text is missing or empty'
                    }, status=status.HTTP_400_BAD_REQUEST)

                date = request.data.get('date', '')
                if not date:
                    date = timezone.now()

                event = Event.objects.get(id=event_id)
                event.text = text
                event.updated_at = date
                event.save()

                return Response({
                    'result': 'OK',
                    'detail': f'Event updated!'
                }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                event_id = kwargs.get('pk', '')
                if not id:
                    return Response({
                        'result': 'ERROR',
                        'detail': 'event_id is missing or empty '
                    }, status=status.HTTP_400_BAD_REQUEST)

                try:
                    event = Event.objects.get(id=event_id)
                    event.delete()

                    return Response({
                        'result': 'OK',
                        'detail': 'Event succesfully deleted!'
                    }, status=status.HTTP_200_OK)

                except Event.DoesNotExist:
                    return Response({
                        'result': 'ERROR',
                        'detail': f'Event does not exist for event_id: {event_id}'
                    }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)


class EventSearchesViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):

    queryset = Event.objects.all()
    serializer_class = EventLiteSerializer

    def list(self, request, *args, **kwargs):
        try:
            table1 = Table1.objects.get(id=kwargs['table1_pk'])
            q = request.GET.get('q', '')
            responses = table1.event_set.filter(text__icontains=q).distinct() if q else None

            results = []
            for response in responses:
                results.append({'text': response.text})

            return Response({
                'result': results
            }, status=status.HTTP_200_OK)

        except Exception as ex:
            return Response({
                'result': 'ERROR',
                'detail': ex.__str__()
            }, status=status.HTTP_400_BAD_REQUEST)
