"""
Copyright 2019 Zeppelin Bend Pty Ltd
This file is part of cimbend.

cimbend is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cimbend is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with cimbend.  If not, see <https://www.gnu.org/licenses/>.
"""
from zepben.model.asset_info import AssetInfo
from zepben.model.exceptions import NoEquipmentException
from zepben.model.identified_object import IdentifiedObject
from zepben.model.diagram_layout import DiagramObject
from zepben.model.common import Location
from zepben.model.base_voltage import BaseVoltage
from typing import List
from abc import ABCMeta


class PowerSystemResource(IdentifiedObject, metaclass=ABCMeta):
    """
    Abstract class, should only be used through subclasses.
    A power system resource can be an item of equipment such as a switch, an equipment container containing many individual
    items of equipment such as a substation, or an organisational entity such as sub-control area. Power system resources
    can have measurements associated.

    Attributes:
        - location : A :class:`zepben.model.Location` for this resource.
        - asset_info : A subclass of :class:`zepben.model.AssetInfo` providing information about the asset associated
                       with this PowerSystemResource.
    """
    def __init__(self, mrid: str, name: str = "", asset_info: AssetInfo = None, diag_objs: List[DiagramObject] = None,
                 location: Location = None):
        """
        Create a PowerSystemResource
        :param mrid: mRID for this object
        :param name: Any free human readable and possibly non unique text naming the object.
        :param diag_objs: An ordered list of :class:`zepben.model.DiagramObject`'s.
        :param location: :class:`zepben.model.Location` of this resource.
        :param asset_info: A subclass of :class:`zepben.model.AssetInfo` providing information about the asset associated
                           with this PowerSystemResource.
        """
        self.location = location
        self.asset_info = asset_info
        super().__init__(mrid=mrid, name=name, diagram_objects=diag_objs)


class Equipment(PowerSystemResource, metaclass=ABCMeta):
    """
    Abstract class, should only be used through subclasses.
    Any part of a power system that is a physical device, electronic or mechanical.
    Attributes:
        - in_service : If True, the equipment is in service.
        - normally_in_service : If True, the equipment is _normally_ in service.
    """
    def __init__(self, mrid: str, in_service: bool, normally_in_service: bool, name: str = "",
                 asset_info: AssetInfo = None, diag_objs: List[DiagramObject] = None, location: Location = None):
        """
        :param mrid: mRID for this object
        :param in_service: If True, the equipment is in service.
        :param normally_in_service: If True, the equipment is _normally_ in service.
        :param name: Any free human readable and possibly non unique text naming the object.
        :param asset_info: A subclass of :class:`zepben.model.AssetInfo` providing information about the asset associated
                           with this PowerSystemResource.
        :param diag_objs: An ordered list of :class:`zepben.model.DiagramObject`'s.
        :param location: :class:`zepben.model.Location` of this resource.
        """
        self.in_service = in_service
        self.normally_in_service = normally_in_service
        super().__init__(mrid=mrid, name=name, asset_info=asset_info, diag_objs=diag_objs, location=location)


class ConductingEquipment(Equipment, metaclass=ABCMeta):
    """
    Abstract class, should only be used through subclasses.
    The parts of the AC power system that are designed to carry current or that are conductively connected through
    terminals.

    Attributes:
        - base_voltage : A :class:`zepben.model.BaseVoltage`.
        - terminals : Conducting equipment have terminals that may be connected to other conducting equipment terminals
                      via connectivity nodes or topological nodes.
    """
    def __init__(self, mrid: str, base_voltage: BaseVoltage, terminals: List, in_service: bool = True,
                 normally_in_service: bool = True, name: str = "", diag_objs: List[DiagramObject] = None,
                 location: Location = None, asset_info: AssetInfo = None):
        """
        Create a ConductingEquipment
        :param mrid: mRID for this object
        :param in_service: If True, the equipment is in service.
        :param base_voltage: A :class:`zepben.model.BaseVoltage`.
        :param normally_in_service: If True, the equipment is _normally_ in service.
        :param name: Any free human readable and possibly non unique text naming the object.
        :param terminals: An ordered list of :class:`zepben.model.Terminal`'s. The order is important and the index of
                          each Terminal should reflect each Terminal's `sequenceNumber`.
        :param diag_objs: An ordered list of :class:`zepben.model.DiagramObject`'s.
        :param location: :class:`zepben.model.Location` of this resource.
        :param asset_info: A subclass of :class:`zepben.model.AssetInfo` providing information about the asset associated
                           with this PowerSystemResource.
        """
        self.base_voltage = base_voltage
        if terminals is None:
            self.terminals = list()
        else:
            self.terminals = terminals

        # We set a reference for each terminal back to its equipment to make iteration over a network easier
        for term in self.terminals:
            term.equipment = self
        super().__init__(mrid=mrid, in_service=in_service, normally_in_service=normally_in_service, name=name,
                         asset_info=asset_info, diag_objs=diag_objs, location=location)

    def __str__(self):
        return f"{super().__str__()} in_serv: {self.in_service}, lnglat: {self.location} terms: {self.terminals}"

    def __repr__(self):
        return f"{super().__repr__()} in_serv: {self.in_service}, lnglat: {self.location} terms: {self.terminals}"

    @property
    def nominal_voltage(self):
        return self.base_voltage.nominal_voltage

    def connected(self):
        return self.in_service

    def add_terminal(self, terminal):
        self.terminals.append(terminal)

    def get_diag_objs(self):
        return self.diagram_objects

    def pos_point(self, sequence_number):
        try:
            return self.location.position_points[sequence_number]
        except IndexError:
            return None

    def has_points(self):
        return len(self.location.position_points) > 0

    def terminal_sequence_number(self, terminal):
        """
        Sequence number for terminals is stored as the index of the terminal in `self.terminals`
        :param terminal: The terminal to retrieve the sequence number for
        :return:
        """
        for i, term in enumerate(self.terminals):
            if term is terminal:
                return i
        raise NoEquipmentException("Terminal does not exist in this equipment")

    def get_terminal_for_node(self, node):
        for t in self.terminals:
            if t.connectivity_node.mrid == node.mrid:
                return t
        raise NoEquipmentException(f"Equipment {self.mrid} is not connected to node {node.mrid}")

    def get_terminal(self, seq_num):
        try:
            return self.terminals[seq_num]
        except (KeyError, IndexError):
            raise NoEquipmentException(f"Equipment {self.mrid} does not have a terminal {seq_num}")

    def get_nominal_voltage(self, terminal=None):
        """
        Get the nominal voltage for this piece of equipment.
        In cases where this equipment has multiple nominal voltages (i.e, transformers),
        this method should be overridden so providing a terminal will provide the voltage corresponding to that terminal

        :param terminal: Terminal to fetch voltage for
        """
        return self.nominal_voltage

    def get_cons(self):
        return [term.connectivity_node for term in self.terminals]

    def _pb_args(self, exclude=None):
        args = super()._pb_args()
        if self.base_voltage is not None:
            args['baseVoltageMRID'] = self.base_voltage.mrid
            del args['baseVoltage']
        return args
