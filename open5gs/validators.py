from typing import Optional
from django.core.exceptions import ValidationError

from core.validators import hexadecimal_validator
from core.constants import (
    MAX_SESSION_NAME_LEN, MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE
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
        raise ValidationError(
            f'{name} содержит недопустимые символы: {", ".join(invalid_chars)}'
        )

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

    if not (
        MIN_PRIORITY_LEVEL_VALUE
        <= arp_data['priority_level']
        <= MAX_PRIORITY_LEVEL_VALUE
    ):
        raise ValidationError(
            '"ARP Priority Level" должен быть между '
            f'{MIN_PRIORITY_LEVEL_VALUE} и {MAX_PRIORITY_LEVEL_VALUE}'
        )


def validate_qos(qos_data: dict, is_pcc_rule: bool = False):
    required_qos_fields = ['index', 'arp']
    if is_pcc_rule:
        required_qos_fields.extend(['mbr', 'gbr'])

    if not all(field in qos_data for field in required_qos_fields):
        if is_pcc_rule:
            raise ValidationError(
                'QoS должен содержать "5QI/QCI" и "ARP Parameters"'
            )
        raise ValidationError(
            'QoS должен содержать "5QI/QCI", "ARP Parameters", '
            '"MBR Parameters" и "GBR Parameters"'
        )

    validate_arp(qos_data['arp'])

    for rate_type in ['mbr', 'gbr']:
        if rate_type in qos_data and is_pcc_rule:
            if not all(
                direction in qos_data[rate_type]
                for direction in ['downlink', 'uplink']
            ):
                raise ValidationError(
                    f'{rate_type.upper()} должен содержать downlink и uplink')
            for direction in ['downlink', 'uplink']:
                if (
                    'value' not in qos_data[rate_type][direction]
                    or 'unit' not in qos_data[rate_type][direction]
                ):
                    raise ValidationError(
                        f'{rate_type.upper()} {direction} необходимо указать '
                        'значение и единицу измерения'
                    )
        elif rate_type in qos_data and not is_pcc_rule:
            if (
                'value' not in qos_data[rate_type]
                or 'unit' not in qos_data[rate_type]
            ):
                raise ValidationError(
                    f'{rate_type.upper()} необходимо указать '
                    'значение и единицу измерения'
                )


def validate_pcc_rule(pcc_rule_data: dict):
    if 'qos' not in pcc_rule_data:
        raise ValidationError('PCC Rules должен содержать "QOS Parameters"')

    validate_qos(pcc_rule_data['qos'], is_pcc_rule=True)


def validate_session(session_data: dict):
    required_fields = ['name', 'type', 'qos']
    if not all(field in session_data for field in required_fields):
        raise ValidationError(
            'Session должна содержать "DNN/APN", "Session Type" и '
            '"QoS Parameters"'
        )

    if len(session_data['name']) > MAX_SESSION_NAME_LEN:
        raise ValidationError(
            f'Длина имени сессии не должна превышать {MAX_SESSION_NAME_LEN}')

    validate_qos(session_data['qos'], is_pcc_rule=False)

    if 'pcc_rule' in session_data:
        for pcc_rule in session_data['pcc_rule']:
            validate_pcc_rule(pcc_rule)
