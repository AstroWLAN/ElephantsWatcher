# Elephants Detection 
> Project for the Software Defined Networking course A.Y. 2020/2021 @Polimi

| Author 👨🏼‍💻 | Email 📨 | Version 📐 | Language 🐍 | 
| :--- | :--- | :--- | :--- |
| Dario Crippa| dario2.crippa@mail.polimi.it | `1.0.0` | `Python` |
  
## VM 💿
These scripts rely on the virtual machine provided by Prof. Verticale [here](https://github.com/gverticale/sdn-vm-polimi)
> It was developed with an older version of this VM so unexpected errors might occur

## Run 👾
To optimally use the project you need three different terminal tabs<br>
  
❗️**Tab I** : Run sFlow
``` swift
// Install
bash /vagrant/setup/sflow-setup.sh

// Run
sflow-rt/start.sh
``` 
❗️**Tab II** : Launch the controller
```
cd 
ryu-manager --observe-links controller_config.py
```
You have to choose between two different operational modes
| Mode | Description                                                                            | 
| :-- |:--| 
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
