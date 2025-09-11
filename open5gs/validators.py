import ipaddress
from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .constants import (
    EMPTION_CHOICES,
    MAX_PRIORITY_LEVEL_VALUE,
    MAX_SESSION_NAME_LEN,
    MIN_PRIORITY_LEVEL_VALUE,
    SESSION_TYPE_CHOICES,
    UNIT_CHOICES
)

hexadecimal_validator = RegexValidator(
    regex=r'^[0-9A-Fa-f]+$',
    message='Разрешены только шестнадцатеричные цифры.'
)

digits_validator = RegexValidator(
    regex=r'^\d+$',
    message='Разрешены только цифры.'
)


def is_valid_objectid(oid: str) -> bool:
    try:
        ObjectId(str(oid))
        return True
    except (InvalidId, TypeError):
        return False


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


def validate_ip_config(ip_config: dict, field_name: str):
    if not isinstance(ip_config, dict):
        raise ValidationError(f'{field_name} должен быть объектом (dict)')

    ipv4 = ip_config.get('ipv4')
    if ipv4:
        try:
            ipaddress.IPv4Address(ipv4)
        except ipaddress.AddressValueError:
            raise ValidationError(
                f'{field_name}: поле "ipv4" содержит невалидный IPv4-адрес: '
                f'{ipv4}'
            )

    ipv6 = ip_config.get('ipv6')
    if ipv6:
        try:
            ipaddress.IPv6Address(ipv6)
        except ipaddress.AddressValueError:
            raise ValidationError(
                f'{field_name}: поле "ipv6" содержит невалидный IPv6-адрес: '
                f'{ipv6}'
            )


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

    if is_pcc_rule:
        validate_br(qos_data['mbr'], 'PCC Rules MBR')
        validate_br(qos_data['gbr'], 'PCC Rules GBR')


def validate_pcc_rule(pcc_rule_data: dict):
    if 'qos' not in pcc_rule_data:
        raise ValidationError('PCC Rules должен содержать "QOS Parameters"')

    validate_qos(pcc_rule_data['qos'], is_pcc_rule=True)


def validate_br(br: dict, br_name: str):
    required_fields = ['downlink', 'uplink']
    required_sub_fields = ['value', 'unit']
    available_units: list[int] = [value for value, _ in UNIT_CHOICES]

    for field in required_fields:
        if field not in br or not isinstance(br[field], dict):
            raise ValidationError(
                f'{br_name} должен содержать {field} как объект')

        for sub_field in required_sub_fields:
            val = br[field].get(sub_field, None)

            if val is None:
                raise ValidationError(
                    f'{br_name} ({field}) должен содержать {sub_field} '
                    '(не None)'
                )

            if sub_field == 'value':
                if not isinstance(val, int) or val < 0:
                    raise ValidationError(
                        f'{br_name} ({field}) - value должен быть целым '
                        'числом >= 0'
                    )
            elif sub_field == 'unit':
                if not isinstance(val, int) or val not in available_units:
                    raise ValidationError(
                        f'{br_name} ({field}) - unit должен быть одним из: '
                        f'{", ".join(map(str, available_units))}'
                    )


def validate_session(session_data: dict):
    required_fields = ['name', 'type', 'qos', 'ambr', 'ue', 'smf', 'pcc_rule']
    if not all(field in session_data for field in required_fields):
        raise ValidationError(
            'Session должна содержать "DNN/APN", "Type", '
            '"QoS Parameters", "AMBR Parameters", "UE IP Configuration",  '
            '"SMF IP Configuration", "PCC Rules"'
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
    validate_ip_config(session_data['ue'], 'UE IP Configuration')
    validate_ip_config(session_data['smf'], 'SMF IP Configuration')

    for pcc_rule in session_data['pcc_rule']:
        validate_pcc_rule(pcc_rule)
