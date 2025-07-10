# flake8: noqa: E501
from .constants import MAX_SUBSCRIBER_MSISDN_LEN
from core.constants import (
    UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE,
    SD_LEN, MAX_SESSION_NAME_LEN, SESSION_TYPE_CHOICES, QOS_INDEX_CHOICES,
    MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE, EMPTION_CHOICES
)


MSISDN_SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'string',
        'pattern': '^\\d+$',
        'maxLength': MAX_SUBSCRIBER_MSISDN_LEN,
        'attrs': {
            'placeholder': 'Введите номер MSISDN',
            'class': 'msisdn-input',
        }
    },
    'minItems': 0,
    'maxItems': 2,
    'uniqueItems': True,
    'addButtonText': 'Добавить',
    'deleteButtonText': 'Удалить',
}

SECURITY_SCHEMA = {
    'type': 'object',
    'properties': {
        'k': {
            'type': 'string',
            'title': 'Subscriber Key (K)',
        },
        'amf': {
            'type': 'string',
            'title': 'Authentication Management Field (AMF)',
        },
        'op': {
            'type': 'string',
            'title': 'USIM Type: OP',
        },
        'opc': {
            'type': 'string',
            'title': 'USIM Type: OPc',
        },
    },
    'required': ['k', 'amf']
}

AMBR_SCHEMA = {
    'type': 'object',
    'properties': {
        'downlink': {
            'type': 'object',
            'title': 'UE-AMBR Downlink',
            'properties': {
                'value': {'type': 'string'},
                'unit': {
                    'type': 'string',
                    'enum': [choice[1] for choice in UNIT_CHOICES],
                }
            },
            'required': ['value', 'unit']
        },
        'uplink': {
            'type': 'object',
            'title': 'UE-AMBR Uplink',
            'properties': {
                'value': {'type': 'string'},
                'unit': {
                    'type': 'string',
                    'enum': [choice[1] for choice in UNIT_CHOICES],
                }
            },
            'required': ['value', 'unit']
        }
    },
    'required': ['downlink', 'uplink']
}

SLICE_SCHEMA = {
    'type': 'array',
    'minItems': 1,
    'maxItems': 8,
    'items': {
        'type': 'object',
        'title': 'Slice Configuration',
        'properties': {
            'sst': {
                'type': 'integer',
                'title': 'Slice/Service Type (SST)',
                'minimum': MIN_SST_VALUE,
                'maximum': MAX_SST_VALUE
            },
            'sd': {
                'type': 'string',
                'title': 'Slice Differentiator (SD)',
                'pattern': '^[0-9a-fA-F]+$',
                'maxLength': SD_LEN,
                'minLength': SD_LEN,
            },
            'default_indicator': {
                'type': 'boolean',
                'title': 'Default S-NSSAI',
                'default': False
            },
            'session': {
                'type': 'array',
                'minItems': 1,
                'maxItems': 4,
                'items': {
                    'type': 'object',
                    'title': 'Session Configurations',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'title': 'DNN/APN',
                            'maxLength': MAX_SESSION_NAME_LEN
                        },
                        'type': {
                            'type': 'string',
                            'title': 'Session Type',
                            'enum': [
                                choice[1] for choice in SESSION_TYPE_CHOICES],
                        },
                        'qos': {
                            'type': 'object',
                            'properties': {
                                'index': {
                                    'type': 'integer',
                                    'title': '5QI/QCI',
                                    'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                                },
                                'arp': {
                                    'type': 'object',
                                    'properties': {
                                        'priority_level': {
                                            'type': 'integer',
                                            'title': 'ARP Priority Level',
                                            'minimum': MIN_PRIORITY_LEVEL_VALUE,
                                            'maximum': MAX_PRIORITY_LEVEL_VALUE
                                        },
                                        'pre_emption_capability': {
                                            'type': 'string',
                                            'title': 'Capability',
                                            'enum': [choice[1] for choice in EMPTION_CHOICES],
                                        },
                                        'pre_emption_vulnerability': {
                                            'type': 'string',
                                            'title': 'Vulnerability',
                                            'enum': [choice[1] for choice in EMPTION_CHOICES],
                                        }
                                    },
                                    'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                                },
                                'mbr': {
                                    'type': 'object',
                                    'title': 'Session-AMBR Downlink',
                                    'properties': {
                                        'value': {'type': 'string'},
                                        'unit': {
                                            'type': 'string',
                                            'enum': [choice[1] for choice in UNIT_CHOICES],
                                        }
                                    },
                                    'required': ['value', 'unit']
                                },
                                'gbr': {
                                    'type': 'object',
                                    'title': 'Session-AMBR Uplink',
                                    'properties': {
                                        'value': {'type': 'string'},
                                        'unit': {
                                            'type': 'string',
                                            'enum': [choice[1] for choice in UNIT_CHOICES],
                                        }
                                    },
                                    'required': ['value', 'unit']
                                }
                            },
                            'required': ['index', 'arp', 'mbr', 'gbr']
                        },
                        'pcc_rule': {
                            'type': 'array',
                            'title': 'PCC Rules',
                            'items': {
                                'type': 'object',
                                'title': 'PCC Rule',
                                'minItems': 0,
                                'maxItems': 8,
                                'properties': {
                                    'qos': {
                                        'type': 'object',
                                        'properties': {
                                            'index': {
                                                'type': 'integer',
                                                'title': '5QI/QCI',
                                                'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                                            },
                                            'arp': {
                                                'type': 'object',
                                                'properties': {
                                                    'priority_level': {
                                                        'type': 'integer',
                                                        'title': 'ARP Priority Level',
                                                        'minimum': MIN_PRIORITY_LEVEL_VALUE,
                                                        'maximum': MAX_PRIORITY_LEVEL_VALUE
                                                    },
                                                    'pre_emption_capability': {
                                                        'type': 'string',
                                                        'title': 'Capability',
                                                        'enum': [choice[1] for choice in EMPTION_CHOICES],
                                                    },
                                                    'pre_emption_vulnerability': {
                                                        'type': 'integer',
                                                        'title': 'Vulnerability',
                                                        'enum': [choice[1] for choice in EMPTION_CHOICES],
                                                    }
                                                },
                                                'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                                            },
                                            'mbr': {
                                                'type': 'object',
                                                'properties': {
                                                    'downlink': {
                                                        'type': 'object',
                                                        'title': 'MBR Downlink',
                                                        'properties': {
                                                            'value': {'type': 'string'},
                                                            'unit': {
                                                                'type': 'string',
                                                                'enum': [choice[1] for choice in UNIT_CHOICES],
                                                            }
                                                        },
                                                        'required': ['value', 'unit']
                                                    },
                                                    'uplink': {
                                                        'type': 'object',
                                                        'title': 'MBR Uplink',
                                                        'properties': {
                                                            'value': {'type': 'string'},
                                                            'unit': {
                                                                'type': 'string',
                                                                'enum': [choice[1] for choice in UNIT_CHOICES],
                                                            }
                                                        },
                                                        'required': ['value', 'unit']
                                                    }
                                                },
                                                'required': ['downlink', 'uplink'] 
                                            },
                                            'gbr': {
                                                'type': 'object',
                                                'properties': {
                                                    'downlink': {
                                                        'type': 'object',
                                                        'title': 'GBR Downlink',
                                                        'properties': {
                                                            'value': {'type': 'string'},
                                                            'unit': {
                                                                'type': 'string',
                                                                'enum': [choice[1] for choice in UNIT_CHOICES],
                                                            }
                                                        },
                                                        'required': ['value', 'unit']
                                                    },
                                                    'uplink': {
                                                        'type': 'object',
                                                        'title': 'GBR Uplink',
                                                        'properties': {
                                                            'value': {'type': 'string'},
                                                            'unit': {
                                                                'type': 'string',
                                                                'enum': [choice[1] for choice in UNIT_CHOICES],
                                                            }
                                                        },
                                                        'required': ['value', 'unit']
                                                    }
                                                },
                                                'required': ['downlink', 'uplink'] 
                                            }
                                        },
                                        'required': ['index', 'arp']
                                    },
                                },
                                'required': ['qos']
                            },
                        }
                    },
                    'required': ['name', 'type', 'qos']
                },
            }
        },
        'required': ['sst', 'sd' ,'default_indicator', 'session']
    },
}

