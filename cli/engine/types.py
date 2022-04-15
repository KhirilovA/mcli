import enum
import ipaddress
import uuid
from decimal import Decimal
from typing import Union, Any
from datetime import date, datetime, time, timedelta
from pydantic import Json


types = {
    "INTEGER": 'int',
    "BIGINT": 'int',
    "SMALLINT": 'int',
    "VARCHAR": 'str',
    "CHAR": 'str',
    "TEXT": 'str',
    "NUMERIC": 'float',
    "FLOAT": 'float',
    "REAL": 'float',
    "INET": '''Union[ipaddress.IPv4Network,
                  ipaddress.IPv6Network,
                  ipaddress.IPv4Address,
                  ipaddress.IPv6Address
    ]''',
    "CIDR": '''Union[ipaddress.IPv4Network,
                  ipaddress.IPv6Network,
                  ipaddress.IPv4Address,
                  ipaddress.IPv6Address
    ]''',
    "UUID": 'uuid.UUID',
    "BIT": 'bytes',
    "MACADDR": 'Any',
    "MONEY": 'Decimal',
    "OID": 'Any',
    "REGCLASS": 'Any',
    "DOUBLE_PRECISION": 'float',
    "TIMESTAMP": 'datetime.timestamp',
    "TIME": 'time',
    "DATE": 'date',
    "BYTEA": 'bytearray',
    "BOOLEAN": 'bool',
    "INTERVAL": 'timedelta',
    "ARRAY": 'list',
    "ENUM": 'enum.Enum',
    "HSTORE": 'Any',
    "hstore": 'Any',
    "INT4RANGE": 'Any',
    "INT8RANGE": 'Any',
    "NUMRANGE": 'Any',
    "DATERANGE": 'Any',
    "TSVECTOR": 'Any',
    "TSRANGE": 'Any',
    "TSTZRANGE": 'Any',
    "JSON": 'Json',
    "JSONB": 'Json',

}
