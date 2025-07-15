# flake8: noqa: E501
from .constants import (
    UNIT_CHOICES,
    MIN_SST_VALUE,
    MAX_SST_VALUE,
    MAX_SUBSCRIBER_HEX_LEN,
    SD_LEN,
    MAX_SESSION_NAME_LEN,
    SESSION_TYPE_CHOICES,
    QOS_INDEX_CHOICES,
    MIN_PRIORITY_LEVEL_VALUE,
    MAX_PRIORITY_LEVEL_VALUE,
    EMPTION_CHOICES,
    MAX_SLICE_COUNT,
    MAX_PCC_RULE_COUNT,
    MAX_SUBSCRIBER_MSISDN_LEN,
    MAX_MSISDN_COUNT,
)
from .utils import generate_hex_key


MSISDN_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'string',
        'pattern': '^\\d+$',
        'maxLength': MAX_SUBSCRIBER_MSISDN_LEN,
    },
    'minItems': 0,
    'maxItems': MAX_MSISDN_COUNT,
    'uniqueItems': True,
    'default': [],
}

SECURITY_SCHEMA = {
    'type': 'object',
    'properties': {
        'k': {
            'type': 'string',
            'pattern': '^[0-9a-fA-F]+$',
            'title': 'Subscriber Key (K)',
            'default': generate_hex_key(MAX_SUBSCRIBER_HEX_LEN),
            'maxLength': MAX_SUBSCRIBER_HEX_LEN,
        },
        'amf': {
            'type': 'string',
            'title': 'Authentication Management Field (AMF)',
            'pattern': '^\\d+$',
            'default': '8000',
            'maxLength': MAX_SUBSCRIBER_HEX_LEN,
        },
        'op': {
            'type': 'string',
            'pattern': '^[0-9a-fA-F]+$',
            'title': 'USIM Type: OP',
            'default': None,
            'maxLength': MAX_SUBSCRIBER_HEX_LEN,
        },
        'opc': {
            'type': 'string',
            'pattern': '^[0-9a-fA-F]+$',
            'title': 'USIM Type: OPc',
            'default': generate_hex_key(MAX_SUBSCRIBER_HEX_LEN),
            'maxLength': MAX_SUBSCRIBER_HEX_LEN,
        },
    },
    'required': ['k', 'amf']
}

AMBR_SCHEMA = {
    'type': 'object',
    'properties': {
        'downlink': {
            'type': 'object',
            'title': 'Downlink',
            'properties': {
                'value': {
                    'type': 'integer',
                    'title': 'Value',
                    'minimum': 0
                },
                'unit': {
                    'type': 'integer',
                    'title': 'Unit',
                    'enum': [choice[0] for choice in UNIT_CHOICES],
                    'default': UNIT_CHOICES[3][0],
                },
            },
            'required': ['value', 'unit']
        },
        'uplink': {
            'type': 'object',
            'title': 'Uplink',
            'properties': {
                'value': {
                    'type': 'integer',
                    'title': 'Value',
                    'minimum': 0
                },
                'unit': {
                    'type': 'integer',
                    'title': 'Unit',
                    'enum': [choice[0] for choice in UNIT_CHOICES],
                    'default': UNIT_CHOICES[3][0],
                }
            },
            'required': ['value', 'unit']
        }
    },
    'required': ['downlink', 'uplink']
}

SESSION_SCHEMA = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'title': 'DNN/APN',
            'maxLength': MAX_SESSION_NAME_LEN,
            'default': 'internet'
        },
        'type': {
            'type': 'integer',
            'title': 'Type',
            'enum': [choice[0] for choice in SESSION_TYPE_CHOICES],
            'default': SESSION_TYPE_CHOICES[2][0]
        },
        'qos': {
            'type': 'object',
            'title': '5QI/QCI',
            'properties': {
                'index': {
                    'type': 'integer',
                    'title': '5QI/QCI',
                    'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                    'default': QOS_INDEX_CHOICES[8][0]
                },
                'arp': {
                    'type': 'object',
                    'properties': {
                        'priority_level': {
                            'type': 'integer',
                            'title': 'ARP Priority Level',
                            'minimum': MIN_PRIORITY_LEVEL_VALUE,
                            'maximum': MAX_PRIORITY_LEVEL_VALUE,
                            'default': 8
                        },
                        'pre_emption_capability': {
                            'type': 'integer',
                            'title': 'Capability',
                            'enum': [choice[0] for choice in EMPTION_CHOICES],
                            'default': EMPTION_CHOICES[1][0]
                        },
                        'pre_emption_vulnerability': {
                            'type': 'integer',
                            'title': 'Vulnerability',
                            'enum': [choice[0] for choice in EMPTION_CHOICES],
                            'default': EMPTION_CHOICES[1][0]
                        }
                    },
                    'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                }
            },
            'required': ['index', 'arp']
        },
        'ambr': AMBR_SCHEMA,
        'pcc_rule': {
            'type': 'array',
            'title': 'PCC Rules',
            'items': {
                'type': 'object',
                'title': 'PCC Rule',
                'properties': {
                    'qos': {
                        'type': 'object',
                        'properties': {
                            'index': {
                                'type': 'integer',
                                'title': '5QI/QCI',
                                'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                                'default': QOS_INDEX_CHOICES[0][0]
                            },
                            'arp': {
                                'type': 'object',
                                'properties': {
                                    'priority_level': {
                                        'type': 'integer',
                                        'title': 'ARP Priority Level',
                                        'minimum': MIN_PRIORITY_LEVEL_VALUE,
                                        'maximum': MAX_PRIORITY_LEVEL_VALUE,
                                        'default': MIN_PRIORITY_LEVEL_VALUE + 1,
                                    },
                                    'pre_emption_capability': {
                                        'type': 'integer',
                                        'title': 'Capability',
                                        'enum': [choice[0] for choice in EMPTION_CHOICES],
                                        'default': EMPTION_CHOICES[1][0]
                                    },
                                    'pre_emption_vulnerability': {
                                        'type': 'integer',
                                        'title': 'Vulnerability',
                                        'enum': [choice[0] for choice in EMPTION_CHOICES],
                                        'default': EMPTION_CHOICES[1][0]
                                    }
                                },
                                'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                            },
                            'mbr': AMBR_SCHEMA,
                            'gbr': AMBR_SCHEMA,
                        },
                        'required': ['index', 'arp']
                    }
                }
            },
            'default': [],
            'maxItems': MAX_PCC_RULE_COUNT
        }
    },
    'required': ['name', 'type', 'qos', 'ambr']
}

SLICE_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'title': 'Slice Configurations',
        'properties': {
            'sst': {
                'type': 'integer',
                'title': 'SST',
                'enum': list(range(MIN_SST_VALUE, MAX_SST_VALUE + 1)),
                'default': MIN_SST_VALUE
            },
            'sd': {
                'type': 'string',
                'title': 'SD',
                'pattern': '^[0-9a-fA-F]*$',
                'maxLength': SD_LEN,
                'default': None
            },
            'default_indicator': {
                'type': 'boolean',
                'title': 'Default S-NSSAI',
                'default': False
            },
            'session': {
                'type': 'array',
                'title': 'Session Configurations',
                'items': SESSION_SCHEMA,
                'minItems': 1,
                'maxItems': MAX_SST_VALUE
            }
        },
        'required': ['sst', 'session']
    },
    'minItems': 1,
    'maxItems': MAX_SLICE_COUNT
}