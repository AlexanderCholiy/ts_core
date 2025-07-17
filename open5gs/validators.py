from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .constants import (
    MAX_SESSION_NAME_LEN,
    MIN_PRIORITY_LEVEL_VALUE,
    MAX_PRIORITY_LEVEL_VALUE,
    SESSION_TYPE_CHOICES,
    UNIT_CHOICES,
    EMPTION_CHOICES,
)


hexadecimal_validator = RegexValidator(
    regex=r'^[0-9A-Fa-f]+$',
    message='Разрешены только шестнадцатеричные цифры.'
)

digits_validator = RegexValidator(
    regex=r'^\d+$',
    message='Разрешены только цифры.'
)


def validate_hex_value(
    value: str,
    name: str,
    max_value_len: Optional[int] = None,
    min_value_len: Optional[int] = None,
) -> str:
    try:
        hexadecimal_validator(value)
    except ValidationError:
        invalid_chars = set(
            c for c in value.upper() if c not in '0123456789ABCDEF')
        if invalid_chars:
            raise ValidationError(
                f'{name} содержит недопустимые символы: '
                f'{", ".join(invalid_chars)}'
            )
        raise ValidationError(f'Проверьте {name}')

    if max_value_len is not None and len(value) > max_value_len:
        raise ValidationError(
            f'{name} должен быть не более {max_value_len} символов')
    if min_value_len is not None and len(value) < min_value_len:
        raise ValidationError(
            f'{name} должен быть не менее {min_value_len} символов')


def validate_arp(arp_data):
    required_arp_fields = [
        'priority_level', 'pre_emption_capability', 'pre_emption_vulnerability'
    ]
    if not all(field in arp_data for field in required_arp_fields):
        raise ValidationError(
            'ARP должен содержать "ARP Priority Level", "Capability" и '
            '"Vulnerability"'
        )

    if not isinstance(arp_data['priority_level'], int):
        raise ValidationError('"ARP Priority Level" должен быть целым числом')

    if not (
        MIN_PRIORITY_LEVEL_VALUE
        <= arp_data['priority_level']
        <= MAX_PRIORITY_LEVEL_VALUE
    ):
        raise ValidationError(
            '"ARP Priority Level" должен быть между '
            f'{MIN_PRIORITY_LEVEL_VALUE} и {MAX_PRIORITY_LEVEL_VALUE}'
        )

    available_capability: list[int] = [value for value, _ in EMPTION_CHOICES]

    if (
        not isinstance(arp_data['pre_emption_capability'], int)
        or arp_data['pre_emption_capability'] not in available_capability
    ):
        raise ValidationError(
            '"Capability" должен принимать одно из следующих значений: '
            f'{", ".join(available_capability)}'
        )

    if (
        not isinstance(arp_data['pre_emption_vulnerability'], int)
        or arp_data['pre_emption_vulnerability'] not in available_capability
    ):
        raise ValidationError(
            '"Vulnerability" должен принимать одно из следующих значений: '
            f'{", ".join(available_capability)}'
        )


def validate_qos(qos_data: dict, is_pcc_rule: bool):
    required_qos_fields = ['index', 'arp']
    if is_pcc_rule:
        required_qos_fields.extend(['mbr', 'gbr'])

    if not all(field in qos_data for field in required_qos_fields):
        if is_pcc_rule:
            raise ValidationError(
                'QoS должен содержать "5QI/QCI", "ARP Parameters", '
                '"MBR Parameters" и "GBR Parameters"'
            )
        raise ValidationError(
            'QoS должен содержать "5QI/QCI" и "ARP Parameters"'
        )

    validate_arp(qos_data['arp'])

    if is_pcc_rule:
        validate_br(qos_data['mbr'], 'PCC Rules MBR')
        validate_br(qos_data['gbr'], 'PCC Rules GBR')


def validate_pcc_rule(pcc_rule_data: dict):
    if 'qos' not in pcc_rule_data:
        raise ValidationError('PCC Rules должен содержать "QOS Parameters"')

    validate_qos(pcc_rule_data['qos'], is_pcc_rule=True)


def validate_br(br: dict, br_name: str):
    required_fields = ['downlink', 'uplink']
    if (
        not all(field in br for field in required_fields)
        or any(br[field] is None for field in required_fields)
    ):
        raise ValidationError(f'{br_name} должен содержать downlink и uplink')

    for field in required_fields:
        required_sub_fields = ['value', 'unit']
        if not all(
            sub_field in br[field] for sub_field in required_sub_fields
        ):
            raise ValidationError(
                f'{br_name} ({field}) должен содержать value и unit')

        if any(
            br[field][sub_field] is None for sub_field in required_sub_fields
        ):
            if ('pcc rules' in br_name.lower() and br[field]['unit'] is None):
                raise ValidationError(
                    f'{br_name} ({field}) должен содержать value и unit')
            elif 'pcc rules' not in br_name.lower():
                raise ValidationError(
                    f'{br_name} ({field}) должен содержать value и unit')

        if 'pcc rules' in br_name.lower():
            if (
                isinstance(br[field]['value'], int)
                and br[field]['value'] < 0
            ):
                raise ValidationError(
                    f'{br_name} ({field}) - value должно быть больше 0')
            elif br[field]['value'] is None:
                pass
            else:
                raise ValidationError(
                    f'{br_name} ({field}) - value должно быть больше 0')
        else:
            if (
                not isinstance(br[field]['value'], int)
                or br[field]['value'] < 0
            ):
                raise ValidationError(
                    f'{br_name} ({field}) - value должно быть больше 0')

        available_units: list[int] = [value for value, _ in UNIT_CHOICES]
        if br[field]['unit'] not in available_units:
            raise ValidationError(
                f'{br_name} ({field}) - unit должнен принимать одно из '
                f'следующих значений: {", ".join(available_units)}'
            )


def validate_session(session_data: dict):
    required_fields = ['name', 'type', 'qos', 'ambr', 'pcc_rule']
    if not all(field in session_data for field in required_fields):
        raise ValidationError(
            'Session должна содержать "DNN/APN", "Type", '
            '"QoS Parameters", "AMBR Parameters", "PCC Rules"'
        )

    if not isinstance(session_data['name'], str):
        raise ValidationError('DNN/APN сессии должен быть строкой')

    available_types: list[int] = [value for value, _ in SESSION_TYPE_CHOICES]
    if (
        not isinstance(session_data['type'], int)
        or session_data['type'] not in available_types
    ):
        raise ValidationError(
            'Type сессии должнен принимать одно из следующих значений: '
            f'{", ".join(available_types)}'
        )

    if len(session_data['name']) > MAX_SESSION_NAME_LEN:
        raise ValidationError(
            f'Длина имени сессии не должна превышать {MAX_SESSION_NAME_LEN}')

    validate_br(session_data['ambr'], 'Session-AMBR')
    validate_qos(session_data['qos'], is_pcc_rule=False)

    for pcc_rule in session_data['pcc_rule']:
        validate_pcc_rule(pcc_rule)
