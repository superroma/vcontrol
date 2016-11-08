# -*- coding: utf-8 -*-
import inspect

class Device(object):
    def __init__(self, api):
        def on_command(cmd):
            self.__on_command(cmd)

        self.__api = api
        self.__api.on_command = on_command
        self.__variables = {}
        self.__diag = {}

    def __on_command(self, cmd):
        actual_var_values = {}
        for varName, value in cmd.items():
            variable = self.__variables.get(varName, {})
            handler = variable.get('bind', None)
            if not callable(handler):
                continue
            actual = handler(value)
            if actual is None:
                continue

            actual = bool(value) \
                if variable.get('type', None) == 'bool' \
                else value
            actual_var_values[varName] = actual
            variable['value'] = actual
        self.__api.publish_data(actual_var_values)

    def declare(self, variables):
        self.__variables = variables
        declarations = [{'name': name, 'type': value['type']}
                        for name, value in variables.items()]
        self.__api.publish_config(declarations)

    def declare_diag(self, diag):
        self.__diag = diag

    def send_data(self):
        for _, varConfig in self.__variables.items():
            bind = varConfig.get('bind', None)
            if hasattr(bind, 'read'):
                varConfig['value'] = bind.read()
            elif callable(bind):
                if inspect.getargspec(bind).args.__len__() == 0:
                    varConfig['value'] = bind()
                else:
                    varConfig['value'] = bind(varConfig['value'])
            else:
                continue

        readings = {varName: varConfig.get('value')
                    for varName, varConfig in self.__variables.items()}

        if len(readings) == 0:
            return
        self.__api.publish_data(readings)

    def send_diag(self):
        readings = {}
        for name, value in self.__diag.items():
            if hasattr(value, 'read'):
                readings[name] = value.read()
            elif callable(value):
                readings[name] = value()
            else:
                continue
        self.__api.publish_diag(readings)
