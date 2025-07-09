from .constants import MAX_SUBSCRIBER_MSISDN_LEN
from core.constants import (
    UNIT_CHOICES, MIN_SST_VALUE, MAX_SST_VALUE,
    SD_LEN, MAX_SESSION_NAME_LEN, SESSION_TYPE_CHOICES, QOS_INDEX_CHOICES,
    MIN_PRIORITY_LEVEL_VALUE, MAX_PRIORITY_LEVEL_VALUE, EMPTION_CHOICES
)

SLICE_SCHEMA = {
    'type': 'array',
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
            'default_indicator': {
                'type': 'boolean',
                'title': 'Default S-NSSAI',
                'default': False
            },
            'sd': {
                'type': 'string',
                'title': 'Slice Differentiator (SD)',
                'pattern': '^[0-9a-fA-F]+$',
                'maxLength': SD_LEN,
                'minLength': SD_LEN,
                'default': ''
            },
            'session': {
                'type': 'array',
                'title': 'Sessions',
                'items': {
                    'type': 'object',
                    'title': 'Session Configuration',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'title': 'DNN/APN',
                            'maxLength': MAX_SESSION_NAME_LEN
                        },
                        'type': {
                            'type': 'integer',
                            'title': 'Session Type',
                            'enum': [
                                choice[0] for choice in SESSION_TYPE_CHOICES],
                            'enumNames': [
                                choice[1] for choice in SESSION_TYPE_CHOICES]
                        },
                        'qos': {
                            'type': 'object',
                            'title': 'QoS Parameters',
                            'properties': {
                                'index': {
                                    'type': 'integer',
                                    'title': '5QI/QCI',
                                    'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                                    'enumNames': [choice[1] for choice in QOS_INDEX_CHOICES]
                                },
                                'arp': {
                                    'type': 'object',
                                    'title': 'ARP Parameters',
                                    'properties': {
                                        'priority_level': {
                                            'type': 'integer',
                                            'title': 'Priority Level',
                                            'minimum': MIN_PRIORITY_LEVEL_VALUE,
                                            'maximum': MAX_PRIORITY_LEVEL_VALUE
                                        },
                                        'pre_emption_capability': {
                                            'type': 'integer',
                                            'title': 'Pre-emption Capability',
                                            'enum': [choice[0] for choice in EMPTION_CHOICES],
                                            'enumNames': [choice[1] for choice in EMPTION_CHOICES]
                                        },
                                        'pre_emption_vulnerability': {
                                            'type': 'integer',
                                            'title': 'Pre-emption Vulnerability',
                                            'enum': [choice[0] for choice in EMPTION_CHOICES],
                                            'enumNames': [choice[1] for choice in EMPTION_CHOICES]
                                        }
                                    },
                                    'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                                },
                                'mbr': {
                                    'type': 'object',
                                    'title': 'Session-AMBR Downlink',
                                    'properties': {
                                        'value': {'type': 'number', 'minimum': 0},
                                        'unit': {
                                            'type': 'number',
                                            'enum': [choice[0] for choice in UNIT_CHOICES],
                                            'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                        }
                                    },
                                    'required': ['value', 'unit']
                                },
                                'gbr': {
                                    'type': 'object',
                                    'title': 'Session-AMBR Uplink',
                                    'properties': {
                                        'value': {'type': 'number', 'minimum': 0},
                                        'unit': {
                                            'type': 'number',
                                            'enum': [choice[0] for choice in UNIT_CHOICES],
                                            'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                        }
                                    },
                                    'required': ['value', 'unit']
                                }
                            },
                            'required': ['index', 'arp', 'mbr', 'gbr']
                        },
                        'ambr': {
                            'type': 'object',
                            'title': 'AMBR',
                            'properties': {
                                'downlink': {
                                    'type': 'object',
                                    'properties': {
                                        'value': {'type': 'number', 'minimum': 0},
                                        'unit': {
                                            'type': 'number',
                                            'enum': [choice[0] for choice in UNIT_CHOICES],
                                            'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                        }
                                    },
                                    'required': ['value', 'unit']
                                },
                                'uplink': {
                                    'type': 'object',
                                    'properties': {
                                        'value': {'type': 'number', 'minimum': 0},
                                        'unit': {
                                            'type': 'number',
                                            'enum': [choice[0] for choice in UNIT_CHOICES],
                                            'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                        }
                                    },
                                    'required': ['value', 'unit']
                                }
                            },
                            'required': ['downlink', 'uplink']
                        },
                        'pcc_rule': {
                            'type': 'array',
                            'title': 'PCC Rules',
                            'items': {
                                'type': 'object',
                                'title': 'PCC Rule',
                                'properties': {
                                    'qos': {
                                        'type': 'object',
                                        'title': 'QoS Parameters',
                                        'properties': {
                                            'index': {
                                                'type': 'integer',
                                                'title': '5QI/QCI',
                                                'enum': [choice[0] for choice in QOS_INDEX_CHOICES],
                                                'enumNames': [choice[1] for choice in QOS_INDEX_CHOICES]
                                            },
                                            'arp': {
                                                'type': 'object',
                                                'title': 'ARP Parameters',
                                                'properties': {
                                                    'priority_level': {
                                                        'type': 'integer',
                                                        'title': 'Priority Level',
                                                        'minimum': MIN_PRIORITY_LEVEL_VALUE,
                                                        'maximum': MAX_PRIORITY_LEVEL_VALUE
                                                    },
                                                    'pre_emption_capability': {
                                                        'type': 'integer',
                                                        'title': 'Pre-emption Capability',
                                                        'enum': [choice[0] for choice in EMPTION_CHOICES],
                                                        'enumNames': [choice[1] for choice in EMPTION_CHOICES]
                                                    },
                                                    'pre_emption_vulnerability': {
                                                        'type': 'integer',
                                                        'title': 'Pre-emption Vulnerability',
                                                        'enum': [choice[0] for choice in EMPTION_CHOICES],
                                                        'enumNames': [choice[1] for choice in EMPTION_CHOICES]
                                                    }
                                                },
                                                'required': ['priority_level', 'pre_emption_capability', 'pre_emption_vulnerability']
                                            },
                                            'mbr': {
                                                'type': 'object',
                                                'title': 'Session-AMBR Downlink',
                                                'properties': {
                                                    'value': {'type': 'number', 'minimum': 0},
                                                    'unit': {
                                                        'type': 'number',
                                                        'enum': [choice[0] for choice in UNIT_CHOICES],
                                                        'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                                    }
                                                },
                                                'required': ['value', 'unit']
                                            },
                                            'gbr': {
                                                'type': 'object',
                                                'title': 'Session-AMBR Uplink',
                                                'properties': {
                                                    'value': {'type': 'number', 'minimum': 0},
                                                    'unit': {
                                                        'type': 'number',
                                                        'enum': [choice[0] for choice in UNIT_CHOICES],
                                                        'enumNames': [choice[1] for choice in UNIT_CHOICES]
                                                    }
                                                },
                                                'required': ['value', 'unit']
                                            }
                                        },
                                        'required': ['index', 'arp', 'mbr', 'gbr']
                                    },
                                    'flow': {
                                        'type': 'array',
                                        'title': 'Flow Descriptions',
                                        'items': {
                                            'type': 'string'
                                        },
                                        'default': []
                                    }
                                },
                                'required': ['qos']
                            },
                            'default': []
                        }
                    },
                    'required': ['name', 'type', 'qos', 'ambr']
                },
                'default': []
            }
        },
        'required': ['sst']
    },
    'default': []
}


AMBR_SCHEMA = {
    'type': 'object',
    'properties': {
        'downlink': {
            'type': 'object',
            'properties': {
                'value': {'type': 'number', 'minimum': 0},
                'unit': {
                    'type': 'number',
                    'enum': [choice[0] for choice in UNIT_CHOICES],
                    'enumNames': [choice[1] for choice in UNIT_CHOICES]
                }
            },
            'required': ['value', 'unit']
        },
        'uplink': {
            'type': 'object',
            'properties': {
                'value': {'type': 'number', 'minimum': 0},
                'unit': {
                    'type': 'number',
                    'enum': [choice[0] for choice in UNIT_CHOICES],
                    'enumNames': [choice[1] for choice in UNIT_CHOICES]
                }
            },
            'required': ['value', 'unit']
        }
    },
    'required': ['downlink', 'uplink']
}


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
        'sqn': {
            'type': 'number',
            'title': 'Sequence Number',
        }
    },
    'required': ['k', 'amf']
}
