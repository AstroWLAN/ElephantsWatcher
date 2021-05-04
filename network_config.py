# Python modules
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections


# TOPOLOGY
# Defines the topology
class IntrastellarTopology(Topo):
    # Creates a topology template
    def build(self):
        # Populates the network with switches and hosts
        host1 = self.addHost('h1')
        host2 = self.addHost('h2')
        host3 = self.addHost('h3')
        host4 = self.addHost('h4')
        host5 = self.addHost('h5')
        host6 = self.addHost('h6')
        host7 = self.addHost('h7')
        host8 = self.addHost('h8')
        host9 = self.addHost('h9')
        switchA = self.addSwitch('s1')
        switchB = self.addSwitch('s2')
        switchC = self.addSwitch('s3')
        switchD = self.addSwitch('s4')

        # Adds the links between the nodes
        self.addLink(host1, switchA)
        self.addLink(host2, switchA)
        self.addLink(host7, switchA)
        self.addLink(host2, switchB)
        self.addLink(host3, switchB)
        self.addLink(host4, switchB)
        self.addLink(host4, switchC)
        self.addLink(host5, switchC)
        self.addLink(host6, switchC)
        self.addLink(host6, switchD)
        self.addLink(host7, switchD)
        self.addLink(host8, switchD)
        self.addLink(host9, switchA)
        self.addLink(host9, switchB)
        self.addLink(host9, switchC)
        self.addLink(host9, switchD)

        self.addLink(switchA, switchB)
        self.addLink(switchB, switchC)
        self.addLink(switchC, switchD)
        self.addLink(switchD, switchA)


