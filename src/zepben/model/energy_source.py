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


from zepben.cim.iec61970 import EnergySource as PBEnergySource
from zepben.model.energy_source_phase import EnergySourcePhase
from zepben.model.terminal import Terminal
from zepben.model.conducting_equipment import ConductingEquipment
from zepben.model.base_voltage import BaseVoltage, UNKNOWN as BV_UNKNOWN
from zepben.model.diagram_layout import DiagramObject
from zepben.model.common import Location
from typing import List
__all__ = ["EnergySource"]



class EnergySource(ConductingEquipment):
    """
    A generic equivalent for an energy supplier on a transmission or distribution voltage level.

    Attributes:
        active_power : High voltage source active injection. Load sign convention is used, i.e. positive sign means flow
                       out from a node. Starting value for steady state solutions
        r : Positive sequence Thevenin resistance.
        x : Positive sequence Thevenin reactance.
        reactive_power : High voltage source reactive injection. Load sign convention is used, i.e. positive sign means
                         flow out from a node. Starting value for steady state solutions.
        voltage_angle : Phase angle of a-phase open circuit.
        voltage_magnitude : Phase-to-phase open circuit voltage magnitude.
        energy_source_phases : An optional list of :class:`EnergySourcePhase`'s describing the phases for this source.
                    The existence of this attribute indicates this is a primary EnergySource and thus will be used as a
                    source point for calculating `Direction`'s.
    """
    def __init__(self, mrid: str, active_power: float = 0.0, r: float = 0.0, x: float = 0.0, base_voltage: BaseVoltage = BV_UNKNOWN,
                 reactive_power: float = 0.0, voltage_angle: float = 0.0, voltage_magnitude: int = 0.0,
                 in_service: bool = True, name: str = "", terminals: List[Terminal] = None, esp: List[EnergySourcePhase] = None,
                 diag_objs: List[DiagramObject] = None, location: Location = None):
        """
        Create an EnergySource
        :param mrid: mRID for this object
        :param active_power: High voltage source active injection. Load sign convention is used, i.e. positive sign
                             means flow out from a node. Starting value for steady state solutions
        :param r: Positive sequence Thevenin resistance.
        :param x: Positive sequence Thevenin reactance.
        :param base_voltage: A :class:`zepben.model.BaseVoltage`.
        :param reactive_power: High voltage source reactive injection. Load sign convention is used, i.e. positive sign
                               means flow out from a node. Starting value for steady state solutions.
        :param voltage_angle: Phase angle of a-phase open circuit.
        :param voltage_magnitude: Phase-to-phase open circuit voltage magnitude.
        :param in_service: If True, the equipment is in service.
        :param name: Any free human readable and possibly non unique text naming the object.
        :param terminals: An ordered list of :class:`zepben.model.Terminal`'s. The order is important and the index of
                          each Terminal should reflect each Terminal's `sequenceNumber`.
        :param esp: An optional list of :class:`EnergySourcePhase`'s describing the phases for this source. The
                    existence of which indicates this is a primary EnergySource and thus will be used as a source point
                    for calculating `Direction`'s.
        :param diag_objs: An ordered list of :class:`zepben.model.DiagramObject`'s.
        :param location: :class:`zepben.model.Location` of this resource.
        """
        self.active_power = active_power
        self.r = r
        self.x = x
        self.reactive_power = reactive_power
        self.voltage_angle = voltage_angle
        self.voltage_magnitude = voltage_magnitude
        self.energy_source_phases = esp if esp is not None else []
        super().__init__(mrid=mrid, in_service=in_service, base_voltage=base_voltage, name=name, terminals=terminals, diag_objs=diag_objs, location=location)

    def has_phases(self):
        """
        Check if this source has any associated :class:`EnergySourcePhases`
        :return: True if there is at least one `EnergySourcePhase`, otherwise False
        """
        return True if self.energy_source_phases else False

    def to_pb(self):
        args = self._pb_args()
        return PBEnergySource(**args)

    @staticmethod
    def from_pb(pb_es, network, **kwargs):
        """
        Convert a protobuf EnergySource to a :class:`zepben.model.EnergySource`
        :param pb_es: :class:`zepben.cim.iec61970.base.wires.EnergySource`
        :param network: Network to extract BaseVoltage
        :raises: NoBaseVoltageException when BaseVoltage isn't found in network
        :return: A :class:`zepben.model.EnergySource`
        """
        terms = Terminal.from_pbs(pb_es.terminals, network)
        location = Location.from_pb(pb_es.location)
        es_phases = EnergySourcePhase.from_pbs(pb_es.energySourcePhases)
        diag_objs = DiagramObject.from_pbs(pb_es.diagramObjects)
        base_voltage = network.get_base_voltage(pb_es.baseVoltageMRID) if pb_es.baseVoltageMRID else None
        return EnergySource(mrid=pb_es.mRID,
                            name=pb_es.name,
                            active_power=pb_es.activePower,
                            r=pb_es.r,
                            x=pb_es.x,
                            base_voltage=base_voltage,
                            reactive_power=pb_es.reactivePower,
                            voltage_angle=pb_es.voltageAngle,
                            voltage_magnitude=pb_es.voltageMagnitude,
                            in_service=pb_es.inService,
                            terminals=terms,
                            esp=es_phases,
                            diag_objs=diag_objs,
                            location=location)


