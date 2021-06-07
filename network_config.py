# MODULES | Python Modules
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.util import dumpNodeConnections
import random
import sys
import time

# PATHS | File paths | Update these paths for your machine
sflowPath = '/home/vagrant/sflow-rt/extras/sflow.py'
scriptPath = '/vagrant/elephantsDetection/viewSwitchRules.sh'

# Reads the sFlow helper script
exec(open(sflowPath).read())

# Assignable ports
portMinValue = 1025
portMaxValue = 65536

# ANSI escape sequences
ansiWhite = u'\u001b[38;5;231m'
ansiRed = u'\u001b[38;5;197m'
ansiRST = u'\u001b[0m'
ansiBlue = u'\u001b[38;5;39m'
ansiGreen = u"\u001b[38;5;47m"


# TOPOLOGY
# Topology definition
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
        switch1 = self.addSwitch('s1')
        switch2 = self.addSwitch('s2')
        switch3 = self.addSwitch('s3')
        switch4 = self.addSwitch('s4')

        # Adds the links between the nodes
        self.addLink(host1, switch1)
        self.addLink(host2, switch1)
        self.addLink(host7, switch1)
        self.addLink(host2, switch2)
        self.addLink(host3, switch2)
        self.addLink(host4, switch2)
        self.addLink(host4, switch3)
        self.addLink(host5, switch3)
        self.addLink(host6, switch3)
        self.addLink(host6, switch4)
        self.addLink(host7, switch4)
        self.addLink(host8, switch4)
        self.addLink(host9, switch1)
        self.addLink(host9, switch2)
        self.addLink(host9, switch3)
        self.addLink(host9, switch4)

        self.addLink(switch1, switch2)
        self.addLink(switch2, switch3)
        self.addLink(switch3, switch4)
        self.addLink(switch4, switch1)


# SUPPORT FUNCTIONS
# Prints the rules installed in the switches of the network and initializes the CLI
def enableCLI(network):
    userChoice = input(ansiWhite + '\n*** ❗️ Do you want to visualize the switch rules? [ y|n ]\n> ' + ansiRST).lower()
    while userChoice != 'y' and userChoice != 'n':
        userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '> ' + ansiRST).lower()
    if userChoice == 'y':
        # Visualizes the rules installed in the switches of the network
        print(ansiRed + "\n📚  RULES" + ansiWhite +
              " : Visualizes the rules installed in the switches of the network\n" + ansiRST)
        CLI(network, script=scriptPath)
    userChoice = input(ansiWhite + '\n*** ❗️ Do you want to use the CLI? [ y|n ]\n> ' + ansiRST).lower()
    while userChoice != 'y' and userChoice != 'n':
        userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '> ' + ansiRST).lower()
    if userChoice == 'y':
        # Enables the CLI
        CLI(network)


# TESTS
# Performs a simple ping test to verify the reachability of all the nodes in the network
def reachabilityTest(network):
    print(ansiRed + "\n🔦️  REACHABILITY" + ansiWhite + " : Performs a reachability test" + ansiRST + "\n")
    # Performs at most five pingAll tests
    attemptsCounter = 0
    grantedAttempts = 5
    dropRate = 100.0
    while dropRate != 0.0 and attemptsCounter < grantedAttempts:
        print(ansiWhite + "🏓  Ping attempt :", attemptsCounter + 1, ansiRST)
        # Performs a pingAll test on the network with a timeout
        dropRate = network.pingAll(timeout=1)
        # If the dropRate is not null...
        if dropRate != 0.0:
            print(ansiRed + "❌️  Presence of unreachable or unknown hosts...let's try again!"
                  + u"\u001b[0m\n")
            attemptsCounter += 1
        # Otherwise...
        else:
            print(ansiGreen + "✅  All the hosts are reachable!" + ansiRST + "\n")
    if attemptsCounter == grantedAttempts:
        # Terminates the script if the number of attempts exceeds the chosen limit
        print(ansiWhite + '🔥  Too many ping attempts! Shutting down everything...\n' + ansiRST)
        sys.exit()


# Generates traffic through the network
def trafficTest(network):
    print(ansiRed + "🚐  TRAFFIC" +
          ansiWhite + " : Generates traffic through the network\n              Graphic representation available at : " +
          ansiBlue + "https://tinyurl.com/rw7w5kr4\n" +
          ansiRST)
    # TRAFFIC
    portList = list(range(portMinValue, portMaxValue))
    # Retrieves the nodes
    serverElephant = network.get('h3')
    clientElephant = network.get('h1')
    serverMouse = network.get('h7')
    clientMouse = network.get('h8')
    # Randomized ports choice
    elephantPort = random.choice(portList)
    portList.remove(elephantPort)
    mousePort = random.choice(portList)
    portList.remove(mousePort)
    # Configures the nodes
    mouseServerCommand = 'iperf -s' + ' -p ' + str(mousePort) + ' & '
    # Transmits 1 MB | It's a mouse...
    mouseClientCommand = 'iperf -c ' + serverMouse.IP() + ' -p ' + str(mousePort) + ' -n ' + '1M'
    mouseClientCommand += ' -w ' + '10M'
    print(ansiWhite + "*** ❗ The mouse is on its way... | 1 MB | C : h8 --> S : h7 | s4" + ansiRST)
    serverMouse.cmdPrint(mouseServerCommand)
    clientMouse.cmdPrint(mouseClientCommand)

    elephantServerCommand = 'iperf -s' + ' -p ' + str(elephantPort) + ' & '
    # Transmits 150 MB | It's an elephant...
    elephantClientCommand = 'iperf -c ' + serverElephant.IP() + ' -p ' + str(elephantPort) + ' -n ' + '150M'
    elephantClientCommand += ' -w ' + '10M'
    print(ansiWhite + "\n*** ❗ The elephant is on its way... | 150 MB | C : h1 --> S : h3 | s1 s2 " + ansiRST)
    serverElephant.cmdPrint(elephantServerCommand)
    clientElephant.cmdPrint(elephantClientCommand)


# MAIN
if __name__ == '__main__':
    # Environment setup
    setLogLevel('info')
    # NETWORK SETUP
    print(
        ansiRed + "\n🌍  NETWORK SETUP" + ansiWhite +
        u" : The network is based on a custom topology built around a central ring\n" +
        u"                    Graphic representation available at : " +
        ansiBlue + "https://tinyurl.com/9pyh5s6t" +
        ansiRST + "\n")
    # Defines a topology object
    topology = IntrastellarTopology()
    # Creates a Mininet network based on the defined topology
    # autoSetMacs | --mac : TRUE & autoStaticArp | --arp : FALSE
    net = Mininet(topology, controller=None, autoSetMacs=True, autoStaticArp=False)
    # Adds a custom remote controller | IP : 127.0.0.1 is the LocalHost while Port : 6633 is the default RYU port
    net.addController('elephantsWatcher', controller=RemoteController, ip='127.0.0.1', port=6633)
    # Starts the network
    net.start()
    dumpNodeConnections(net.hosts)
    # Performs the reachability test
    reachabilityTest(net)
    # Performs the traffic test
    trafficTest(net)
    enableCLI(net)
    print(ansiWhite + '\nShutting down the network...' + ansiRST)
    # Waits 10 secs before shut down the network
    time.sleep(10)
    # Stops the network
    net.stop()
