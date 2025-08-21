#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Sofa.Core
from Sofa.constants import *


class PneuNetsController(Sofa.Core.Controller):
    """
    This Controller simply takes the cableActuator's value
    and increases / decreases it depending on the pressed key ('+' or '-')
    """
    def __init__(self, *a, **kw):
        """
        In the ctor, we want to first call the constructor for the parent class (trampoline)
        We then store the node we want to retrieve the actuator from in the class
        (Sofa.Core.Base.getContext() could also have been used here instead,
        or a link between aCableActuator and the controller could have been used too)
        """
        Sofa.Core.Controller.__init__(self, *a, **kw)
        self.node = kw["node"]
        return

    def onKeypressedEvent(self,e):
        """
        Events methods are named after the actual event names (Event::GetClassName() in C++),
        with a prepended "on" prefix. Thus, this Event is the KeypressedEvent class in C++
        The onXXXEvent method takes a dictionary as a parameter, containing the useful
        values stored in the event class, e.g. here, the pressed key
        """
        spcValue = self.node.cavity.SPC.value
        caValue = self.node.cable.CA.value

        if((e["key"] == Sofa.constants.Key.KP_1) or (e["key"] == Sofa.constants.Key.KP_3)):
            if e["key"] == Sofa.constants.Key.KP_1:
                cableDisplacement = caValue.value[0] + 1.0
            elif e["key"] == Sofa.constants.Key.KP_3:
                cableDisplacement = caValue.value[0] - 1.0
            caValue.value = [cableDisplacement]

        if((e["key"] == Sofa.constants.Key.KP_4) or (e["key"] == Sofa.constants.Key.KP_6)):
            if e["key"] == Sofa.constants.Key.KP_4:
                volumeFinal = spcValue.value[0] + 1000
            elif e["key"] == Sofa.constants.Key.KP_6:
                volumeFinal = spcValue.value[0] - 1000
                if volumeFinal < 0:
                    volumeFinal = 0
            spcValue.value = [volumeFinal]

        return
