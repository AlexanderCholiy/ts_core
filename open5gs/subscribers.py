import json
from io import BytesIO
from typing import Callable, Optional, Union

import pandas as pd
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from core.logger import subscriber_logger

from .constants import (
    MAX_FILE_SIZE,
    REQUIRED_HEADERS_FOR_SUBSCRIBERS_DELETE,
    REQUIRED_HEADERS_FOR_SUBSCRIBERS_UPLOAD
)


class SubscriberManager:

    def _process_subscribers_excel(
        self, file: Union[str, bytes], required_headers: list[str]
    ) -> tuple[Optional[pd.DataFrame], dict, set]:
        """
        Общая функция для обработки Excel-файла абонентов.

        Args:
            - file: путь или байты Excel
            - required_headers: обязательные колонки
        """
        errors = {}
        success_imsi = set()
        df = None

        try:
            df = pd.read_excel(file)
        except Exception as e:
            subscriber_logger.exception(e)
            errors[0] = 'Ошибка чтения файла'
            return df, errors, success_imsi

        # Проверка обязательных колонок:
        missing_headers = [h for h in required_headers if h not in df.columns]
        if missing_headers:
            errors[0] = (
                'Отсутствуют обязательные колонки: '
                f'{", ".join(missing_headers)} на первом листе Excel'
            )
            return df, errors, success_imsi

        # Проверка пустых строк:
        empty_rows = df[df[required_headers].isna().any(axis=1)]
        if not empty_rows.empty:
            for idx in empty_rows.index:
                row_index = idx + 2  # учёт заголовков в Excel
                missing = [
                    col for col in required_headers
                    if (
                        pd.isna(df.at[idx, col])
                        or str(df.at[idx, col]).strip() == ''
                    )
                ]
                errors[row_index] = (
                    f'Отсутствуют значения: {", ".join(missing)}'
                )
            return df, errors, success_imsi

        return df, errors, success_imsi

    def upload_subscribers_from_excel(
        self, file: Union[str, bytes]
    ) -> tuple[dict, set]:
        """Добавление абонентов из excel файла"""
        df, errors, success_imsi = self._process_subscribers_excel(
            file, REQUIRED_HEADERS_FOR_SUBSCRIBERS_UPLOAD
        )

        if errors:
            return errors, success_imsi

        duplicate_imsi = df[df['IMSI'].duplicated(keep=False)]['IMSI'].tolist()
        if duplicate_imsi:
            errors[0] = (
                'В файле присутствуют дубликаты IMSI: '
                f'{", ".join(map(str, set(duplicate_imsi)))}'
            )
            return errors, success_imsi

        from .constants import (
            DEFAULT_AMF,
            DEFAULT_SESSION_SCHEMA_NAME,
            EMPTION_CHOICES,
            MIN_SST_VALUE,
            SESSION_TYPE_CHOICES,
            UNIT_CHOICES
        )
        from .forms import SubscriberForm

        for idx, row in df.iterrows():
            row_index = idx + 2  # учёт заголовков в Excel

            imsi = row['IMSI']
            security_k = row['K']
            security_opc = row['OPC']

            form = SubscriberForm(
                data={
                    'imsi': imsi,
                    'subscriber_status': 0,
                    'operator_determined_barring': 0,
                    'msisdn': json.dumps([]),
                    'security': json.dumps({
                        'k': security_k,
                        'amf': DEFAULT_AMF,
                        'opc': security_opc,
                        'op': None,
                    }),
                    'ambr': json.dumps({
                        'uplink': {'value': 1, 'unit': UNIT_CHOICES[3][0]},
                        'downlink': {'value': 1, 'unit': UNIT_CHOICES[3][0]},
                    }),
                    'slice': json.dumps([{
                        'sst': MIN_SST_VALUE,
                        'default_indicator': True,
                        'session': [{
                            'name': DEFAULT_SESSION_SCHEMA_NAME,
                            'type': SESSION_TYPE_CHOICES[2][0],
                            'qos': {
                                'index': 9,
                                'arp': {
                                    'priority_level': 8,
                                    'pre_emption_capability': (
                                        EMPTION_CHOICES[1][0]
                                    ),
                                    'pre_emption_vulnerability': (
                                        EMPTION_CHOICES[1][0]
                                    )
                                }
                            },
                            'ambr': {
                                'uplink': {
                                    'value': 1, 'unit': UNIT_CHOICES[3][0]
                                },
                                'downlink': {
                                    'value': 1, 'unit': UNIT_CHOICES[3][0]
                                },
                            },
                            'ue': {},
                            'smf': {},
                            'pcc_rule': []
                        }]
                    }])
                }
            )

            if not form.is_valid():
                error_messages = []

                for field, field_errors in form.errors.items():
                    for err in field_errors:
                        error_messages.append(f'{field} [{err}]')

                errors[row_index] = ', '.join(error_messages)
                continue

            try:
                form.save()
            except ValidationError as e:
                errors[row_index] = ', '.join(e.messages)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                subscriber_logger.exception(e)
                errors[row_index] = 'Неизвестная ошибка'
            else:
                success_imsi.add(imsi)

        if success_imsi:
            subscriber_logger.info(
                f'Добавлено {len(success_imsi)} абонентов: {set(success_imsi)}'
            )

        return errors, success_imsi

    def delete_subscribers_from_excel(
        self, file: Union[str, bytes]
    ) -> tuple[dict, set]:
        """Удаление абонентов из excel файла"""
        df, errors, success_imsi = self._process_subscribers_excel(
            file, REQUIRED_HEADERS_FOR_SUBSCRIBERS_DELETE
        )

        if errors:
            return errors, success_imsi

        imsi_list = df['IMSI'].tolist()

        from .models import Subscriber

        to_delete_qs = Subscriber.objects.filter(imsi__in=imsi_list)
        found_imsi_set = set(to_delete_qs.values_list('imsi', flat=True))

        missing_imsi = set(imsi_list) - found_imsi_set
        if missing_imsi:
            for idx, row in df.iterrows():
                row_index = idx + 2
                imsi = row['IMSI']
                if imsi in missing_imsi:
                    errors[row_index] = 'Абонент с таким IMSI не найден'

        try:
            deleted_count, _ = to_delete_qs.delete()
            success_imsi.update(found_imsi_set)
            if success_imsi:
                subscriber_logger.info(
                    f'Удалено {deleted_count} абонентов: {set(found_imsi_set)}'
                )
        except Exception as e:
            subscriber_logger.exception(e)
            errors[0] = 'Внутренняя ошибка при удалении абонентов'

        return errors, success_imsi

    def handle_subscribers_excel(
        self,
        request: HttpRequest,
        action_func: Callable[[BytesIO], tuple[dict, set]],
    ) -> Union[HttpResponse, HttpResponseRedirect]:
        """Обработка Excel-файлов для добавления/удаления абонентов"""
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, 'Файл не найден')
            return redirect('open5gs:index')

        if excel_file.size > MAX_FILE_SIZE:
            messages.error(
                request,
                (
                    f'Файл слишком большой ({excel_file.size / 1024:.1f} КБ). '
                    f'Максимальный размер: {MAX_FILE_SIZE / 1024 / 1024:.0f} '
                    'МБ'
                )
            )
            return redirect('open5gs:index')

        excel_bytes = BytesIO(excel_file.read())
        errors, success_imsi = action_func(excel_bytes)
        if success_imsi:
            messages.success(
                request,
                f'Обработано {len(success_imsi)} '
                f'записей из {len(success_imsi) + len(errors)}.'
            )

        if errors:
            context = {'errors': errors, 'filename': excel_file.name}
            return render(request, 'open5gs/subscribers_err.html', context)
        else:
            if not success_imsi:
                messages.warning(
                    request,
                    (
                        f'Файл "{excel_file.name}" не содержит данных для '
                        'обработки.'
                    )
                )

        return redirect('open5gs:index')

    def handle_subscribers_download(
        self, request: HttpRequest
    ) -> Union[HttpResponse, HttpResponseRedirect]:
        from .models import Subscriber

        subscribers = Subscriber.objects.all().values('imsi')

        if not subscribers.exists():
            return render(request, 'open5gs/subscribers_err.html', {
                'errors': {0: 'Абоненты не найдены'},
                'filename': 'subscribers.xlsx'
            })

        df = pd.DataFrame(subscribers)

        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Subscribers')

        output.seek(0)

        response = HttpResponse(
            output.read(),
            content_type=(
                'application/vnd.openxmlformats-officedocument.spreadsheetml'
                '.sheet'
            )
        )
        response['Content-Disposition'] = (
            'attachment; filename=subscribers.xlsx'
        )

        return response
