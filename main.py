#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import render_template
from pymodbus.client.sync import ModbusTcpClient as ModbusClient

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

#从机号
UNIT = 0x1

class MiMachine2Client(object):
    _client = None

    def __init__(self):
        self._server = '127.0.0.1'
        self._port   = 502

    def SureConnect(self):
        if self.IsConnect():
            return
        # from pymodbus.transaction import ModbusRtuFramer
        # client = ModbusClient('localhost', port=5020, framer=ModbusRtuFramer)
        # client = ModbusClient(method='binary', port='/dev/ptyp0', timeout=1)
        # client = ModbusClient(method='ascii', port='/dev/ptyp0', timeout=1)
        # client = ModbusClient(method='rtu', port='/dev/ptyp0', timeout=1,
        #                       baudrate=9600)
        _client = ModbusClient(self._server, self._port)
        if not _client.connect():
            msg = "Connect {server}:{port}is failed.".format(server=self._server, port=self._port)
            raise Exception(msg)

    def IsConnect(self):
        if self._client == None:
            return False
        rr = self._client.read_coil(1, 1, unit=UNIT)
        if rr.isError():
            return False
        if rr.bits[0] != 1:
            return False
        return True

    def close(self):
        if self._client == None:
            return
        self._client.close()

    def write(self):
        if self._client == None:
            return
        self._client.write_coil(1, True)

    def read(self):
        if self._client == None:
            return
        result = self._client.read_coil(1, 1, unit=UNIT)
        print(result.bits[0])

    def ReadCoils(self):
        if self._client == None:
            return
        rq = self._client.write_coils(0, True, unit=UNIT)
        rr = self._client.read_coils(0, 1, unit=UNIT)
        #rq.isError()
        #rr.bits[0] == True
        rq = self._client.write_coils(1, [True]*8, unit=UNIT)
        rr = self._client.read_coils(1, 21, unit=UNIT)
        # rr.reqisters == [True]*21


    def WriteHoldingRegister(self):
        if self._client == None:
            return
        rq = self._client.write_register(1, 10, unit=UNIT)
        #rq.isError()
        rr = self._client.read_holding_registers(1, 1, unit=UNIT)
        #rr.registers[0] == 10

    def WriteHoldingRegisters(self):
        if self._client == None:
            return
        rq = self._client.write_registers(1, [10]*8, unit=UNIT)
        #rq.isError()
        rr = self._client.read_holding_registers(1, 8, unit=UNIT)
        #rr.registers == [10]*8

    def ReadInputRegisters(self):
        if self._client == None:
            return
        rr = self._client.input_registers(1, 8, unit=UNIT)


    def ReadWriteRegisters(self):
        if self._client == None:
            return
        arguments = {
            'read_address': 1,
            'read_count': 8,
            'write_address': 1,
            'write_registers': [20]*8,
        }
        rq = self._client.readwrite_registers(unit=UNIT, **arguments)
        rr = self._client.read_holding_registers(1, 8, unit=UNIT)
        #rq.registers == [20]*8
        #rr.registers == [20]*8


import json
class ApiResponse(object):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def json(self):
        return json.dumps(self.__dict__, sort_keys=True)

    def __str__(self):
        return json.dumps(self.__dict__, sort_keys=True)


modbus_client = MiMachine2Client()
app = Flask(__name__)

@app.route("/")
def index():
    return '''
<html>
<body>
<p><H1>MiMachine2API</H1></p>
<li>/api/v1/start_work/id</li>
<li>/api/v1/stop_work</li>
<li>/api/v1/abort_work</li>
</body>
</html>
    '''
    # apis = [
    #     "/api/v1/start_work/<style>",
    #     "/api/v1/stop_work",
    #     "/api/v1/abort_work"
    # ]
    #return render_template("hello.html", name='zhouyi')

@app.route("/api/v1/start_work/<style>")
def start_work(style):
    try:
        modbus_client.SureConnect()
        modbus_client.write()
        return ApiResponse(0,"start_work({style}) is ok".format(style=style)).json()
    except Exception as err:
        err_msg = "start_work({style}) is error: {err}".format(style=style, err=err.message)
        log.error(err_msg)
        return ApiResponse(-1, err_msg).json()


@app.route("/api/v1/stop_work")
def stop_work():
    try:
        modbus_client.SureConnect()
        modbus_client.write()
        return ApiResponse(0, "stop_work is ok").json()
    except Exception as err:
        err_msg = "stop_work: error: {err}".format(err=err.message)
        log.error(err_msg)
        return ApiResponse(-1, err_msg).json()


@app.route("/api/v1/abort_work")
def abort_work():
    try:
        modbus_client.SureConnect()
        modbus_client.write()
        return ApiResponse(0, "abort_work is ok").json()
    except Exception as err:
        err_msg = "abort_work: error: {err}".format(err=err.message)
        log.error(err_msg)
        return ApiResponse(-1, err_msg).json()


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)