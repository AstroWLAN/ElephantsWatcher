# Python modules
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
# Utility modules
import random

# Compiles and execute sFlow helper script
exec(open('/home/vagrant/sflow-rt/extras/sflow.py').read())

# Assignable ports
portMinValue = 1025
portMaxValue = 65536


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
        self.addLink(host1, switchA, bw=100)
        self.addLink(host2, switchA, bw=100)
        self.addLink(host7, switchA, bw=100)
        self.addLink(host2, switchB, bw=100)
        self.addLink(host3, switchB, bw=100)
        self.addLink(host4, switchB, bw=100)
        self.addLink(host4, switchC, bw=100)
        self.addLink(host5, switchC, bw=100)
        self.addLink(host6, switchC, bw=100)
        self.addLink(host6, switchD, bw=100)
        self.addLink(host7, switchD, bw=100)
        self.addLink(host8, switchD, bw=100)
        self.addLink(host9, switchA, bw=100)
        self.addLink(host9, switchB, bw=100)
        self.addLink(host9, switchC, bw=100)
        self.addLink(host9, switchD, bw=100)

        self.addLink(switchA, switchB, bw=100)
        self.addLink(switchB, switchC, bw=100)
        self.addLink(switchC, switchD, bw=100)
        self.addLink(switchD, switchA, bw=100)


# TESTS
# Performs a simple ping test to verify the reachability of all the nodes in the network
def reachabilityTest(network):
    print(u"\u001b[38;5;197m\n⚙️   TEST" + u"\u001b[38;5;231m : Hosts reachability" + u"\u001b[0m\n")
    # Performs at most five pingAll tests
    attemptsCounter = 0
    dropRate = 100.0
    while dropRate != 0.0 and attemptsCounter < 5:
        print(u"\u001b[38;5;231m🏓  Ping attempt :", attemptsCounter + 1, u"\u001b[0m")
        # Performs a pingAll on the network with a timeout
        dropRate = network.pingAll(timeout=1)
        # If the dropRate is not null...
        if dropRate != 0.0:
            print(u"\u001b[38;5;197m❗️  Presence of unreachable or unknown hosts...let's try again"
                  + u"\u001b[0m\n")
            attemptsCounter += 1
        # Otherwise...
        else:
            print(u"\u001b[38;5;47m✅  All the hosts are reachable!"
                  + u"\u001b[0m\n")


# Generates traffic through the network
def trafficTest(network):
    print(u"\u001b[38;5;197m\n🚐  TRAFFIC" +
          u"\u001b[38;5;231m : Generates traffic through the network\n    Dashboard : " +
          u"\u001b[38;5;39mhttps://tinyurl.com/3zwb9c2n\n" +
          u"\u001b[38;5;231m    Flowmanager : " +
          u"\u001b[38;5;39mhttp://localhost:8080/home/index.html" +
          u"\u001b[0m\n")
    # TRAFFIC
    portList = list(range(portMinValue, portMaxValue))
    # Gets the nodes
    serverElephant = network.get('h3')
    clientElephant = network.get('h1')
    serverMouse = network.get('h7')
    clientMouse = network.get('h8')
    # Ports choice
    elephantPort = random.choice(portList)
    portList.remove(elephantPort)
    mousePort = random.choice(portList)
    portList.remove(mousePort)
    # Configures the nodes
    elephantServerCommand = 'iperf -s' + ' -p ' + str(elephantPort) + ' & '
    # Transmits 10 GB | It's an elephant...lots of packets!
    elephantClientCommand = 'iperf -c ' + serverElephant.IP() + ' -p ' + str(elephantPort) + ' -n ' + '1G'
    # Edits the TCP Window Size
    elephantClientCommand += ' -w ' + '100M'
    print(u"\u001b[38;5;231m*** The elephant is on his way... | 1 GByte" + u"\u001b[0m")
    serverElephant.cmdPrint(elephantServerCommand)
    clientElephant.cmdPrint(elephantClientCommand)

    mouseServerCommand = 'iperf -s' + ' -p ' + str(mousePort) + ' & '
    # Transmits 1 MB | It's a mouse... very few packets
    mouseClientCommand = 'iperf -c ' + serverMouse.IP() + ' -p ' + str(mousePort) + ' -n ' + '10M'
    # Edits the TCP Window Size
    mouseClientCommand += ' -w ' + '1M'
    print(u"\u001b[38;5;231m\n*** The mouse is on his way... | 10 MByte" + u"\u001b[0m\n")
    serverMouse.cmdPrint(mouseServerCommand)
    clientMouse.cmdPrint(mouseClientCommand)


# MAIN
if __name__ == '__main__':
    # Environment setup
    setLogLevel('info')
    # NETWORK SETUP
    print(
        u"\u001b[38;5;197m\n🌍  NETWORK SETUP" + u"\u001b[38;5;231m :\n" +
        u"    The network is based on a custom topology built around a central ring\n" +
        u"    A graphic representation is available at " +
        u"\u001b[38;5;39mhttps://tinyurl.com/5d7wmxxv" +
        u"\u001b[0m\n")
    # Defines a topology object
    topology = IntrastellarTopology()
    # Creates a Mininet network based on the defined topology
    # autoSetMacs | --mac & autoStaticArp | --arp
    net = Mininet(topology, controller=None, autoSetMacs=True, autoStaticArp=False, link=TCLink)
    # Adds a custom remote controller | IP : 127.0.0.1 is the LocalHost while Port : 6633 is the default Ryu port
    net.addController('elephantsWatcher', controller=RemoteController, ip='127.0.0.1', port=6633)
    # Starts the network
    net.start()
    dumpNodeConnections(net.hosts)
    reachabilityTest(net)
    trafficTest(net)
    # Launches the CLI for further commands
    CLI(net)
