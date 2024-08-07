# Elephants Detection 
> Project for the Software Defined Networking course A.Y. 2020/2021 @Polimi

| Author 👨🏼‍💻 | Email 📨 | Version 📐 | Language 🐍 | 
| :--- | :--- | :--- | :--- |
| Dario Crippa| dario2.crippa@mail.polimi.it | `1.0.0` | `Python` |
  
### VM 💿
These scripts rely on the virtual machine provided by Prof. Verticale [here](https://github.com/gverticale/sdn-vm-polimi)
> It was developed with an older version of this VM so unexpected errors might occur

```sh
# Install the VM
git clone https://github.com/gverticale/sdn-vm-polimi

# Install Vagrant (use Homebrew on MacOS)
brew install vagrant 

# Configure the VM
cd VirtualMachineFolder
vagrant up

# Connect to the VM via SSH
vagrant ssh
```

### Software Configuration 💽
```sh
# Install sFlow
bash /vagrant/setup/sflow-setup.sh

# Clone this project inside the VM
git clone https://github.com/AstroWLAN/ElephantFlowsManagement
```

## Run 👾
Open three distinct tabs in your terminal application<br>
  
1️⃣ **sFlow**
```sh
# Execute sFlow
sflow-rt/start.sh
```
2️⃣ **Controller**<br>
```sh
# Launch the RYU controller configuration script
cd controllerFolderPath
ryu-manager --observe-links controller_config.py
```
3️⃣ **Network**
```sh
# Launch the Mininet network configuration script
cd controllerFolderPath
sudo python3 network_config.py
```
### Count Min Sketch 🧠
At controller startup you have to choose between two different operational modes 
| Mode 🕹️ | Description ✏️ | 
| :-- | :-- | 
|Enabled| Enable the CMS algorithm <br>`rules installed locally in the switches`| 
|Disabled| Disable the CMS algorithm <br>`packets will be managed directly by the controller`| 
### Expected Results 📃
With the CMS algorithm enabled the amount of time requested to send all the packets through the network will be very smaller
<p align="center">
<img width="350" height="350" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Repository%20Resources/Performance%20CMS%20Disabled.png">
<img width="350" height="350" src="https://github.com/AstroWLAN/ElephantFlowsManagement/blob/master/Resources/Repository%20Resources/Performance%20CMS%20Enabled.png">

### Troubleshooting 🥵
The best way to solve the biggest amount of problems with the Mininet environment is to perform a complete cleanup
```
sudo mn -c
```
</p>
