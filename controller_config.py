# Python modules
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types, arp, tcp, ipv4
from ryu.topology.api import get_all_host, get_all_link
import networkx
import hashlib
import datetime

# GLOBAL VARIABLES
# Escape sequences
ansiWhite = u'\u001b[38;5;231m'
ansiRed = u'\u001b[38;5;197m'
ansiBlue = u'\u001b[38;5;39m'
ansiRST = u'\u001b[0m'

# Takes user preference
userChoice = input(ansiWhite + '\n❗️️ Do you want to enable the COUNT-MIN SKETCHES algorythm? [y|n]\n> ' +
                   ansiRST).lower()
# Checks input value correctness
while userChoice != 'y' and userChoice != 'n':
    userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '> ' + ansiRST).lower()
# Prints user choice
if userChoice == 'y':
    print(ansiWhite + '\n🎉️️ You have enabled the CMS algorithm! '
                      'Packets will be counted in the first switch of the chain...\n' + ansiRST)
else:
    print(ansiWhite + '\n❌️ You have disabled the CMS algorithm! '
                      'Packets will be managed directly by the controller...\n' + ansiRST)

# CMS variables
thresholdCMS = 4000
arrayCMSLength = 10
# Creates an array of ten elements initialized to zero
arrayCMS = [0 for _ in range(arrayCMSLength)]


# CONTROLLER | Elephants Watcher
class ElephantsWatcher(app_manager.RyuApp):
    # OpenFlow protocol version
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    # SWITCH FEATURES | Installs the lowest priority rule : packet sent to the controller when there are no matches
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switchFeatures_handler(self, ev):
        # Gets the switchID
        switch = ev.msg.datapath
        # Retrieves the switch OpenFlow version
        ofproto = switch.ofproto
        # Retrives the switch parser
        parser = switch.ofproto_parser

        # Sends to the controller when there are no matches with the rules installed in the switch
        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                [
                    parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                           ofproto.OFPCML_NO_BUFFER)
                ]
            )
        ]
        # FlowMod message composition
        modMessage = parser.OFPFlowMod(
            datapath=switch,
            # We're using the lowest priority | it's the default rule for our switches
            priority=0,
            # Matches everything | Each field is a wildcard
            match=parser.OFPMatch(),
            instructions=instructions
        )
        # Sends the FlowMod message to the switch | installs the rule
        switch.send_msg(modMessage)

    # PACKET-IN | Manages ARP requests, routes the packets and identifies the elephant flows
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # Received message from the switch
        receivedMessage = ev.msg
        # Switch identifier | Datapath
        switch = receivedMessage.datapath
        # OpenFlow protocol used by the switch
        ofproto = switch.ofproto
        # Parser for the switch message
        parser = switch.ofproto_parser
        # Input port of the message
        inputPort = receivedMessage.match['in_port']
        # Empty FlowID
        flowID = ' '

        # Creating a packet object passing the received message data
        receivedPacket = packet.Packet(data=receivedMessage.data)
        # Gets the packet information at the different layers of the OSI stack
        ethPacket = receivedPacket.get_protocol(ethernet.ethernet)
        tcpPacket = receivedPacket.get_protocol(tcp.tcp)
        ipPacket = receivedPacket.get_protocol(ipv4.ipv4)

        # PACKET ANALYSIS
        # The packet is an ARP REQUEST
        if ethPacket.ethertype == ether_types.ETH_TYPE_ARP:
            self.proxyARP(receivedMessage)
            return
        # We're accepting only IPv4 packets
        elif ethPacket.ethertype != ether_types.ETH_TYPE_IP:
            return
        # If the packet isn't an ARP REQUEST...
        else:
            # Retrieves the destination MAC address
            destinationMAC = ethPacket.dst
            # Retrieves the source MAC address
            sourceMAC = ethPacket.src

            # FLOWID | Creation
            # IPv4 Protocol 6 is TCP
            if userChoice == 'y' and ethPacket.ethertype == ether_types.ETH_TYPE_IP and ipPacket.proto == 6:
                packetSrcPort = tcpPacket.src_port
                packetDstPort = tcpPacket.dst_port
                packetSrcIP = ipPacket.src
                packetDstIP = ipPacket.dst
                protocolNumber = ipPacket.proto
                flowID = str(packetSrcIP) + str(packetDstIP) + str(protocolNumber) + str(packetSrcPort)
                flowID += str(packetDstPort)

            # DESTINATION SWITCH | Analysis
            destinationSwitchID, destinationSwitchPort = self.findDestinationSwitch(destinationMAC)
            # Destination switch doesn't exist
            if destinationSwitchID is None:
                # Host not found
                print(ansiRed + 'ERROR' + ansiWhite + ' : Node not found!' + ansiRST)
                return
            # The current switch is the destination switch | the host is directly connected
            elif destinationSwitchID == switch.id:
                outputPort = destinationSwitchPort

                if userChoice == 'y' and ethPacket.ethertype == ether_types.ETH_TYPE_IP and ipPacket.proto == 6:
                    # Checks if the current switch is the first one of the chain
                    if self.isFirstSwitch(sourceMAC, switch.id):
                        # Increase CMS counter
                        updateCountMinSketches(flowID)

                    # Checks if the counter has reached the threshold
                    if checkCounterValue(flowID):
                        # Installs the routing rule
                        generateRoutingRule(parser, ipPacket, tcpPacket, ofproto, outputPort, switch, receivedMessage)
                        resetCounter(flowID)
                        print('*** Resetting the counter...')
            else:
                # If the host isn't directly connected to the current switch
                outputPort = self.findNextHop(switch.id, destinationSwitchID)

                if userChoice == 'y' and ethPacket.ethertype == ether_types.ETH_TYPE_IP and ipPacket.proto == 6:
                    if self.isFirstSwitch(sourceMAC, switch.id):
                        # Increase CMS counter
                        updateCountMinSketches(flowID)

                    # Checks if the counter has reached the threshold
                    if checkCounterValue(flowID):
                        # Installs the routing rule
                        generateRoutingRule(parser, ipPacket, tcpPacket, ofproto, outputPort, switch, receivedMessage)

            # Routes the current packet
            actions = [parser.OFPActionOutput(outputPort)]
            packetOut = parser.OFPPacketOut(
                datapath=switch,
                buffer_id=receivedMessage.buffer_id,
                in_port=inputPort,
                actions=actions,
                data=receivedMessage.data
            )
            switch.send_msg(packetOut)

    # SUPPORT FUNCTIONS
    # This function allows the controller to intercept and respond to the ARP REQUESTs
    def proxyARP(self, message):
        # Gets the switch ID
        switch = message.datapath
        # Retrieves the Openflow protocol and parser
        ofproto = switch.ofproto
        parser = switch.ofproto_parser
        # Gets the input port
        inputPort = message.match['in_port']

        pkt_in = packet.Packet(message.data)
        eth_in = pkt_in.get_protocol(ethernet.ethernet)
        arp_in = pkt_in.get_protocol(arp.arp)

        # Refuses what's not an ARP REQUEST
        if arp_in.opcode != arp.ARP_REQUEST:
            return

        destinationMAC = None

        # Searches the host
        for host in get_all_host(self):
            if arp_in.dst_ip in host.ipv4:
                destinationMAC = host.mac
                break

        # Host not found
        if destinationMAC is None:
            return

        # PACKET OUT message composition
        packetOut = packet.Packet()
        # The incapsulated packet is an ARP packet
        eth_out = ethernet.ethernet(
            dst=eth_in.src,
            src=destinationMAC,
            ethertype=ether_types.ETH_TYPE_ARP
        )
        # Defines the ARP REPLY payload
        arp_out = arp.arp(
            opcode=arp.ARP_REPLY,
            src_mac=destinationMAC,
            src_ip=arp_in.dst_ip,
            dst_mac=arp_in.src_mac,
            dst_ip=arp_in.src_ip
        )
        packetOut.add_protocol(eth_out)
        packetOut.add_protocol(arp_out)
        packetOut.serialize()

        packetOutMessage = parser.OFPPacketOut(
            datapath=switch,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=ofproto.OFPP_CONTROLLER,
            actions=[parser.OFPActionOutput(inputPort)],
            data=packetOut.data
        )
        # Sends the PACKET OUT message
        switch.send_msg(packetOutMessage)
        return

    # Finds the datapath ID of the last switch of the chain and the relative port
    def findDestinationSwitch(self, destinationMAC):
        for host in get_all_host(self):
            if host.mac == destinationMAC:
                return host.port.dpid, host.port.port_no
        return None, None

    # Checks if the current switch is the first one of the chain
    def isFirstSwitch(self, sourceMAC, switchID):
        for host in get_all_host(self):
            if host.mac == sourceMAC:
                if host.port.dpid == switchID:
                    return True
        return False

    # Finds the next hop to which the package will be forwarded
    def findNextHop(self, sourceID, destinationID):
        network = networkx.DiGraph()
        for link in get_all_link(self):
            network.add_edge(link.src.dpid, link.dst.dpid, port=link.src.port_no)
        # Finds the shortest path in the network to connect the source to the destination
        path = networkx.shortest_path(network, sourceID, destinationID)
        # Gets the first of these nodes
        firstLink = network[path[0]][path[1]]
        # Returns the port that put the actual switch in communication with the next one
        return firstLink['port']


# Update the CMS counter related to the given FlowID
def updateCountMinSketches(identifier):
    global arrayCMS
    # Evaluates the hash value of the identifier
    shaValue = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
    # Gets the array index
    arrayIndex = int(shaValue, base=16) % arrayCMSLength
    # Increases the counter in the cell by 1 unit
    arrayCMS[arrayIndex] += 1


# Reset the CMS counter related to the given FlowID
def resetCounter(identifier):
    global arrayCMS
    # Evaluates the hash value of the identifier
    shaValue = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
    # Gets the array index
    arrayIndex = int(shaValue, base=16) % arrayCMSLength
    # Reset the counter in the given cell of the CMS array
    arrayCMS[arrayIndex] = 0


# Checks the CMS counter related to the given FlowID
def checkCounterValue(identifier):
    # Evaluates the hash value of the identifier
    shaValue = hashlib.sha256(identifier.encode('utf-8')).hexdigest()
    # Gets the array index
    arrayIndex = int(shaValue, base=16) % arrayCMSLength
    if arrayCMS[arrayIndex] == thresholdCMS:
        # TRUE | Threshold reached
        return True
    else:
        # TRUE | Threshold not reached
        return False


# Installs the routing rule for the detected elephant flow
def generateRoutingRule(parser, ipPacket, tcpPacket, ofproto, outputPort, switch, receivedMessage):
    # ROUTING RULE | Composition
    # Match fields
    elephantMatch = parser.OFPMatch(
        # Checks ethertype
        eth_type=ether_types.ETH_TYPE_IP,
        # Checks if the packet belongs to the elephant flow | these fields define the FLOWID
        ipv4_src=ipPacket.src,
        ipv4_dst=ipPacket.dst,
        ip_proto=ipPacket.proto,
        tcp_src=tcpPacket.src_port,
        tcp_dst=tcpPacket.dst_port
    )
    # Instruction set
    instructionSet = [
        parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS,
            [parser.OFPActionOutput(outputPort)]
        )
    ]

    # FLOWMOD MESSAGE | Composition
    modMessage = parser.OFPFlowMod(
        datapath=switch,
        priority=100,
        match=elephantMatch,
        instructions=instructionSet,
        buffer_id=receivedMessage.buffer_id
    )

    # FLOWMOD MESSAGE | Sending
    switch.send_msg(modMessage)
    # Prints a confirm message
    print(ansiWhite + '*** ' + ansiRed + 'Switch [ s' + str(switch.id) + ' ]' + ansiWhite + ' : New rule installed! '
          + ansiRST + str(datetime.datetime.now()))
