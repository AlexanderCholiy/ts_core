MAX_SUBSCRIBER_IMSI_LEN = 15
MAX_SUBSCRIBER_MSISDN_LEN = 15
MAX_SUBSCRIBER_HEX_LEN = 32
MAX_SESSION_NAME_LEN = 128
MIN_PRIORITY_LEVEL_VALUE = 1
MAX_PRIORITY_LEVEL_VALUE = 15
MIN_SST_VALUE = 1
MAX_SST_VALUE = 4
SD_LEN = 6

MAX_SUBSCRIBER_PER_PAGE = 16
MAX_MSISDN_COUNT = 2
MAX_SLICE_COUNT = 8
MAX_PCC_RULE_COUNT = 8

OPERATOR_DETERMINED_BARRING_CHOICES = [
    (0, '(0) All Packet Oriented Services Barred'),
    (1, '(1) Roamer Access HPLMN-AP Barred'),
    (2, '(2) Roamer Access to VPLMN-AP Barred'),
    (3, '(3) Barring of all outgoing calls'),
    (4, '(4) Barring of all outgoing international calls'),
    (
        5,
        (
            '(5) Barring of all outgoing international calls except '
            'those directed to the home PLMN country'
        )
    ),
    (6, '(6) Barring of all outgoing inter-zonal calls'),
    (
        7, (
            '(7) Barring of all outgoing inter-zonal calls except '
            'those directed to the home PLMN country'
        )
    ),
    (
        8,
        (
            '(8) Barring of all outgoing international calls except '
            'those directed to the home PLMN country and Barring of '
            'all outgoing inter-zonal calls'
        )
    ),
]
SUBSCRIBER_STATUS_CHOICES = [
    (0, 'SERVICE GRANTED'), (1, 'OPERATOR DETERMINED BARRING'),
]
UNIT_CHOICES = [(0, 'bps'), (1, 'Kbps'), (2, 'Mbps'), (3, 'Gbps'), (4, 'Tbps')]
EMPTION_CHOICES = [(0, 'Disabled'), (1, 'Enabled')]
QOS_INDEX_CHOICES = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 9),
    (65, 65),
    (66, 66),
    (67, 67),
    (69, 69),
    (70, 70),
    (71, 71),
    (72, 72),
    (73, 73),
    (74, 74),
    (75, 75),
    (76, 76),
    (79, 77),
    (80, 80),
    (82, 82),
    (83, 83),
    (84, 84),
    (85, 85),
    (86, 86),
]
SESSION_TYPE_CHOICES = [(1, 'IPv4'), (2, 'IPv6'), (3, 'IPv4v6')]
