# Python modules
from mininet.cli import CLI
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

# Escape sequences
ansiWhite = u'\u001b[38;5;231m'
ansiRed = u'\u001b[38;5;197m'
ansiRST = u'\u001b[0m'
ansiBlue = u'\u001b[38;5;39m'
ansiDarkGray = u'\u001b[38;5;247m'
ansiGreen = u"\u001b[38;5;47m"


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


# SUPPORT FUNCTIONS
# Initializes the CLI printing the switch rules
def enableCLI(network):
    userChoice = input(ansiWhite + '\n*** ❗️ Do you want to visualize the switch rules? [y/n]\n> ' + ansiRST).lower()
    while userChoice != 'y' and userChoice != 'n':
        userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '> ' + ansiRST).lower()
    if userChoice == 'y':
        # Launches the CLI for further commands
        print(ansiRed + "\n📚  RULES\n" + ansiWhite + "    Visualizes the switch rules\n" + ansiRST)
        CLI(network, script="/vagrant/projectLocalTest/viewSwitchRules.sh")
    userChoice = input(ansiWhite + '\n*** ❗️ Do you want to use the CLI? [y|n]\n> ' + ansiRST).lower()
    while userChoice != 'y' and userChoice != 'n':
        userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '> ' + ansiRST).lower()
    if userChoice == 'y':
        CLI(network)


# TESTS
# Performs a simple ping test to verify the reachability of all the nodes in the network
def reachabilityTest(network):
    print(ansiRed + "\n🔦️  REACHABILITY\n" + ansiWhite + "    Hosts reachability test" + ansiRST + "\n")
    # Performs at most five pingAll tests
    attemptsCounter = 0
    dropRate = 100.0
    while dropRate != 0.0 and attemptsCounter < 5:
        print(ansiWhite + "🏓  Ping attempt :", attemptsCounter + 1, ansiRST)
        # Performs a pingAll on the network with a timeout
        dropRate = network.pingAll(timeout=1)
        # If the dropRate is not null...
        if dropRate != 0.0:
            print(ansiRed + "❌️  Presence of unreachable or unknown hosts...let's try again"
                  + u"\u001b[0m\n")
            attemptsCounter += 1
        # Otherwise...
        else:
            print(ansiGreen + "✅  All the hosts are reachable!" + ansiRST + "\n")


# Generates traffic through the network
def trafficTest(network):
    print(ansiRed + "🚐  TRAFFIC\n" +
          ansiWhite + "    Sends packets through the network\n    Visualize the traffic at : " +
          ansiBlue + "https://tinyurl.com/3zwb9c2n\n" +
          ansiRST)
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
    mouseServerCommand = 'iperf -s' + ' -p ' + str(mousePort) + ' & '
    # Transmits 100 MB | It's a mouse... very few packets
    mouseClientCommand = 'iperf -c ' + serverMouse.IP() + ' -p ' + str(mousePort) + ' -n ' + '1M'
    mouseClientCommand += ' -w ' + '10M'
    print(ansiWhite + "*** ❗ The mouse is on his way... | 1 MB" + ansiRST)
    serverMouse.cmdPrint(mouseServerCommand)
    clientMouse.cmdPrint(mouseClientCommand)

    elephantServerCommand = 'iperf -s' + ' -p ' + str(elephantPort) + ' & '
    # Transmits 1 GB | It's an elephant...lots of packets!
    elephantClientCommand = 'iperf -c ' + serverElephant.IP() + ' -p ' + str(elephantPort) + ' -n ' + '100M'
    elephantClientCommand += ' -w ' + '10M'
    print(ansiWhite + "\n*** ❗ The elephant is on his way... | 100 MB" + ansiRST)
    serverElephant.cmdPrint(elephantServerCommand)
    clientElephant.cmdPrint(elephantClientCommand)


# MAIN
if __name__ == '__main__':
    # Environment setup
    setLogLevel('info')
    # NETWORK SETUP
    print(
        ansiRed + "\n🌍  NETWORK SETUP\n" + ansiWhite +
        u"    The network is based on a custom topology built around a central ring\n" +
        u"    A graphic representation is available at " +
        ansiBlue + "https://tinyurl.com/5d7wmxxv" +
        ansiRST + "\n")
    # Defines a topology object
    topology = IntrastellarTopology()
    # Creates a Mininet network based on the defined topology
    # autoSetMacs | --mac & autoStaticArp | --arp
    net = Mininet(topology, controller=None, autoSetMacs=True, autoStaticArp=False)
    # Adds a custom remote controller | IP : 127.0.0.1 is the LocalHost while Port : 6633 is the default Ryu port
    net.addController('elephantsWatcher', controller=RemoteController, ip='127.0.0.1', port=6633)
    # Starts the network
    net.start()
    dumpNodeConnections(net.hosts)
    reachabilityTest(net)
    trafficTest(net)
    enableCLI(net)
    # Stops the network
    net.stop()
