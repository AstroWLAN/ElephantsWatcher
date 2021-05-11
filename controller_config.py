# Import modules
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls, CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.ofproto import ofproto_v1_3

# GLOBAL VARIABLES
# Escape sequences
ansiWhite = u'\u001b[38;5;231m'
ansiRed = u'\u001b[38;5;197m'
ansiRST = u'\u001b[0m'
ansiBlue = u'\u001b[38;5;39m'
# Handles user preferences
userChoice = input(ansiWhite + '❗️ Do you want to enable the COUNT-MIN SKETCHES algorythm? [y/n]\n>> ').lower()
# Wrong input
while userChoice != 'y' and userChoice != 'n':
    userChoice = input(ansiRed + 'Bad input...retry!\n' + ansiWhite + '>> ').lower()
print(ansiRST)
# FLOWMANAGER url
print(ansiRed + 'FLOWMANAGER' + ansiWhite + ' : ' + ansiBlue + 'http://localhost:8080/home/index.html\n' + ansiRST)

# CMS VARIABLES
# CMS Threshold | Each iperf TCP packet is about 8KB so we set the threshold at 512MB
thresholdCMS = 65536
arrayCMS = None
arrayCMSLength = 10


# CONTROLLER | Elephants Watcher
class ElephantWatcher(app_manager.RyuApp):
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
