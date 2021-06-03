# SDN Final Project A.A. 2020/2021
<p align="center">
<img width="600" height="300" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Repository%20Resources/Project%20Logo.png">
</p>
<p>
  
## Run 👾
In order to run the project you need three different tabs of the terminal<br>
  
❗️**Tab I** : Run sFlow
```
sflow-rt/start.sh
```
If you haven't done it yet install sFlow in the virtual machine
```
bash /vagrant/setup/sflow-setup.sh
``` 
❗️**Tab II** : Launch the controller
```
cd 
ryu-manager --observe-links controller_config.py
```
You have to choose between two different modes of operation
| Mode          | Description                                                                            | 
| :-----------: |:---------------------------------------------------------------------------------------| 
|🎉  CMS Enabled | Enable the CMS algorithm : Rules will be installed locally in the switches            | 
|❌  CMS Disabled| Disable the CMS algorithm : All the packets will be managed directly by the controller| 
  
❗️**Tab III** : Execute the network setup and the tests
```
cd 
sudo python3 network_config.py
```
With the CMS algorithm enabled the amount of time requested to send all the packets through the network will be very smaller
  
<p align="center">
<img width="350" height="350" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Repository%20Resources/Performance%20CMS%20Disabled.png">
<img width="350" height="350" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Repository%20Resources/Performance%20CMS%20Enabled.png">
</p>

## Troubleshooting ⚙️
The best way to solve the biggest amount of problems with the Mininet environment is to perform a complete cleanup
```
sudo mn -c
```
</p>
