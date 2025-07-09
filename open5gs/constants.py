MAX_SUBSCRIBER_IMSI_LEN = 15
MAX_SUBSCRIBER_MSISDN_LEN = 15

MAX_SUBSCRIBER_PER_PAGE = 16

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
