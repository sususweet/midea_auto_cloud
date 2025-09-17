from abc import ABC
from enum import IntEnum


class MessageLenError(Exception):
    pass


class MessageBodyError(Exception):
    pass


class MessageCheckSumError(Exception):
    pass


class MessageType(IntEnum):
    set = 0x02,
    query = 0x03,
    notify1 = 0x04,
    notify2 = 0x05,
    exception = 0x06,
    querySN = 0x07,
    exception2 = 0x0A,
    querySubtype = 0xA0


class MessageBase(ABC):
    HEADER_LENGTH = 10

    def __init__(self):
        self._device_type = 0x00
        self._message_type = 0x00
        self._body_type = 0x00
        self._device_protocol_version = 0

    @staticmethod
    def checksum(data):
        return (~ sum(data) + 1) & 0xff

    @property
    def header(self):
        raise NotImplementedError

    @property
    def body(self):
        raise NotImplementedError

    @property
    def message_type(self):
        return self._message_type

    @message_type.setter
    def message_type(self, value):
        self._message_type = value

    @property
    def device_type(self):
        return self._device_type

    @device_type.setter
    def device_type(self, value):
        self._device_type = value

    @property
    def body_type(self):
        return self._body_type

    @body_type.setter
    def body_type(self, value):
        self._body_type = value

    @property
    def device_protocol_version(self):
        return self._device_protocol_version

    @device_protocol_version.setter
    def device_protocol_version(self, value):
        self._device_protocol_version = value

    def __str__(self) -> str:
        output = {
            "header": self.header.hex(),
            "body": self.body.hex(),
            "message type": "%02x" % self._message_type,
            "body type": ("%02x" % self._body_type) if self._body_type is not None else "None"
        }
        return str(output)


class MessageRequest(MessageBase):
    def __init__(self, device_protocol_version, device_type, message_type, body_type):
        super().__init__()
        self.device_protocol_version = device_protocol_version
        self.device_type = device_type
        self.message_type = message_type
        self.body_type = body_type

    @property
    def header(self):
        length = self.HEADER_LENGTH + len(self.body)
        return bytearray([
            # flag
            0xAA,
            # length
            length,
            # device type
            self._device_type,
            # frame checksum
            0x00,  # self._device_type ^ length,
            # unused
            0x00, 0x00,
            # frame ID
            0x00,
            # frame protocol version
            0x00,
            # device protocol version
            self._device_protocol_version,
            # frame type
            self._message_type
        ])

    @property
    def _body(self):
        raise NotImplementedError

    @property
    def body(self):
        body = bytearray([])
        if self.body_type is not None:
            body.append(self.body_type)
        if self._body is not None:
            body.extend(self._body)
        return body

    def serialize(self):
        stream = self.header + self.body
        stream.append(MessageBase.checksum(stream[1:]))
        return stream


class MessageQuestCustom(MessageRequest):
    def __init__(self, device_type, cmd_type, cmd_body):
        super().__init__(
            device_protocol_version=0,
            device_type=device_type,
            message_type=cmd_type,
            body_type=None)
        self._cmd_body = cmd_body

    @property
    def _body(self):
        return bytearray([])

    @property
    def body(self):
        return self._cmd_body

