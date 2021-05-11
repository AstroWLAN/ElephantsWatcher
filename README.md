# SDN Final Project A.A. 2020/2021
<p align="center">
<img width="610" height="240" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Project%20Logo.png">
</p>
<p>

## Description 📚
The purpose of this project is the identification and management of the TCP connections called "Elephants" (long data streams that bring a lot of bytes)<br>
We had to develop a configuration file for the Ryu controller to manage these entities<br>
You can read the complete project requests here: [Project 1 - Elephant Flows Management](https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Project%20Descriptions.pdf)

## Setup ⚙️
First of all you have to setup your Mininet environment! <br>
I used the Virtual Machine provided by the course professor Giacomo Verticale : [Download](https://github.com/gverticale/sdn-vm-polimi)

Next download and install sFlow (you'll need this in order to visualize the traffic through the network)
```
cd
bash /vagrant/setup/sflow-setup.sh
```

Clone this repository in the virtual machine
```
git clone https://github.com/AstroWLAN/ElephantFlowsManagement
```
You're done! 

## Run 👾
You will need three different terminal tabs<br>

**First terminal tab | sFlow**<br>
In the first terminal launch sFlow typing
```
sflow-rt/start.sh
```
You can reach the Mininet Dashboard at this [link](https://tinyurl.com/3zwb9c2n)<br>

**Second terminal tab | Controller**<br>
Place yourself in the project folder that you have cloned earlier and type
```
sudo python3 controller_config.py
```

**Third terminal tab | Network**<br>
Place yourself in the project folder that you have cloned earlier and type
```
sudo python3 network_config.py
```
## Troubleshooting ⚠️
If you experience problems with the Mininet environment simply type 
```
sudo mn -c
```

</p>
