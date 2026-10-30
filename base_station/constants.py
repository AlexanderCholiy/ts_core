from enum import Enum
from ipaddress import IPv4Address
from typing import Annotated, Literal

from pydantic import HttpUrl, StringConstraints, TypeAdapter

SOAP_NAMESPACE = 'http://schemas.xmlsoap.org/soap/envelope/'

NS_MAP = {
    '': '',
    'soap-env': SOAP_NAMESPACE,
    'cwmp': 'urn:dslforum-org:cwmp-1-0',
}


class BaseStationParameter(str, Enum):
    HARDWARE_VERSION = 'InternetGatewayDevice.DeviceInfo.HardwareVersion'
    MANUFACTURER_OUI = 'InternetGatewayDevice.DeviceInfo.ManufacturerOUI'
    SERIAL_NUMBER = 'InternetGatewayDevice.DeviceInfo.SerialNumber'
    SOFTWARE_VERSION = 'InternetGatewayDevice.DeviceInfo.SoftwareVersion'
    IP_ADDRESS = 'InternetGatewayDevice.DeviceInfo.X_BAICELLS_COM_IpAddr'
    STATION_RUN_TIME = 'InternetGatewayDevice.DeviceInfo.X_BAICELLS_COM_STATION_RUN_Time'  # noqa: E501
    STATION_RUN_TIME_REAL = 'InternetGatewayDevice.DeviceInfo.X_BAICELLS_COM_STATION_RUN_Time_real'  # noqa: E501
    RADIO_ENABLE = 'InternetGatewayDevice.DeviceInfo.boardconf.sas.sasConfig.RadioEnable'  # noqa: E501
    CONNECTION_REQUEST_URL = 'InternetGatewayDevice.ManagementServer.ConnectionRequestURL'  # noqa: E501
    HNB_NAME = 'InternetGatewayDevice.Services.FAPService.1.AccessMgmt.LTE.HNBName'  # noqa: E501
    ACTIVE_UE = 'InternetGatewayDevice.Services.FAPService.1.CellConfig.LTE.X_QUALCOMM_LTE_STATS.L2RlcStats.NumOfActiveUE'  # noqa: E501
    OP_STATE = 'InternetGatewayDevice.Services.FAPService.1.FAPControl.LTE.OpState'  # noqa: E501
    IMSI = 'InternetGatewayDevice.Usim.IMSI_value'
    HALOB_ENABLE_STATE = 'boardconf.HaloB.HaloBEnableState'
    HALOB_MODE = 'boardconf.HaloB.HaloBMode'


class BaseStationParameterType(Enum):
    STRING = TypeAdapter(str)
    IPV4 = TypeAdapter(IPv4Address)

    DURATION = TypeAdapter(
        Annotated[
            str,
            StringConstraints(pattern=r'^\d+d \d+h \d+m \d+s$'),
        ]
    )

    BOOLEAN = TypeAdapter(Literal['true', 'false'])

    INTEGER = TypeAdapter(
        Annotated[
            str,
            StringConstraints(pattern=r'^\d+$'),
        ]
    )

    URL = TypeAdapter(HttpUrl)

    OPTIONAL = None


PARAMETER_TYPES = {
    BaseStationParameter.HARDWARE_VERSION: BaseStationParameterType.STRING,
    BaseStationParameter.MANUFACTURER_OUI: BaseStationParameterType.STRING,
    BaseStationParameter.SERIAL_NUMBER: BaseStationParameterType.STRING,
    BaseStationParameter.SOFTWARE_VERSION: BaseStationParameterType.STRING,
    BaseStationParameter.IP_ADDRESS: BaseStationParameterType.IPV4,
    BaseStationParameter.STATION_RUN_TIME: BaseStationParameterType.DURATION,
    BaseStationParameter.STATION_RUN_TIME_REAL: BaseStationParameterType.DURATION,  # noqa: E501
    BaseStationParameter.RADIO_ENABLE: BaseStationParameterType.BOOLEAN,
    BaseStationParameter.CONNECTION_REQUEST_URL: BaseStationParameterType.URL,
    BaseStationParameter.HNB_NAME: BaseStationParameterType.STRING,
    BaseStationParameter.ACTIVE_UE: BaseStationParameterType.INTEGER,
    BaseStationParameter.OP_STATE: BaseStationParameterType.BOOLEAN,
    BaseStationParameter.IMSI: BaseStationParameterType.OPTIONAL,
    BaseStationParameter.HALOB_ENABLE_STATE: BaseStationParameterType.BOOLEAN,
    BaseStationParameter.HALOB_MODE: BaseStationParameterType.INTEGER,
}
