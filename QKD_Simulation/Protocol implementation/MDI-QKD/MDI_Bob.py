# MDI_Bob.py — Prepares qubits and sends to Charlie with basis tracking

from netsquid.protocols import NodeProtocol
from netsquid.qubits.qubitapi import create_qubits, operate
from netsquid.qubits.operators import H, X
import random

class BobProtocol(NodeProtocol):
    def __init__(self, node, num_bits, perf):
        super().__init__(node)
        self.node = node
        self.num_bits = num_bits
        self.perf = perf
        self.key = ""
        self.bases = []

    def run(self):
        # Stagger Bob by half the round timer so Alice's and Bob's qubits arrive at
        # Charlie at different times — NetSquid only delivers to an active await_port_input.
        yield self.await_timer(100_000)
        for _ in range(self.num_bits):
            bit = random.randint(0, 1)
            basis = random.randint(0, 1)  # 0: Z, 1: X
            self.bases.append(basis)

            q = create_qubits(1)[0]

            if bit == 1:
                operate(q, X)
            if basis == 1:
                operate(q, H)

            self.node.ports["qout"].tx_output(q)
            self.perf.record_epr_sent()
            self.key += str(bit)
            yield self.await_timer(200_000)  # 200 µs per round, covers up to 50 km delay
