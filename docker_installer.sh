#!/bin/bash

# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install necessary dependencies for Docker
sudo apt install -y apt-transport-https ca-certificates software-properties-common

# Add Docker GPG key and set up Docker repository
curl -fsSL https://download.docker.com/linux/raspbian/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/raspbian $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package lists again
sudo apt update

# Upgrade installed packages again
sudo apt upgrade -y

# Install Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add the current user to the docker group
sudo usermod -aG docker $USER

# Print a message indicating completion
echo "Docker installation completed. Please restart your system or re-login for the changes to take effect."
