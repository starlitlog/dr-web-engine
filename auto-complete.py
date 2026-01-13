#!/usr/bin/env python3

import sys
import subprocess
import time
import json
import requests
from datetime import datetime

def log(message):
    print(f"{datetime.now()}: {message}")

def get_vm_id(vm_name, api_key):
    """Get VM ID from VM name"""
    url = "https://infrahub-api.nexgencloud.com/v1/core/virtual-machines"
    headers = {
        "accept": "application/json",
        "api_key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        for instance in data.get("instances", []):
            if instance["name"] == vm_name:
                return instance["id"]

        log(f"VM '{vm_name}' not found!")
        return None

    except requests.RequestException as e:
        log(f"Failed to get VM info: {e}")
        return None

def monitor_remote_process(vm_ip):
    """Monitor remote training process"""
    cmd = f'ssh ubuntu@{vm_ip} "pgrep -f \'lora-model-training.py\'"'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode == 0

def copy_results(vm_ip):
    """Copy results from remote VM"""
    cmd = f"scp -r ubuntu@{vm_ip}:~/Dev/results ~/Dev/remote-results"
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def stop_vm(vm_id, api_key):
    """Stop VM via API"""
    url = f"https://infrahub-api.nexgencloud.com/v1/core/virtual-machines/{vm_id}/stop"
    headers = {
        "accept": "application/json",
        "api_key": api_key
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        log("VM stop command sent via API")
        return True
    except requests.RequestException as e:
        log(f"Failed to stop VM via API: {e}")
        return False

def delete_vm(vm_id, api_key):
    """Delete VM via API"""
    url = f"https://infrahub-api.nexgencloud.com/v1/core/virtual-machines/{vm_id}"
    headers = {
        "accept": "application/json",
        "api_key": api_key
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        log("VM delete command sent via API")
        return True
    except requests.RequestException as e:
        log(f"Failed to delete VM via API: {e}")
        return False

def ssh_shutdown(vm_ip):
    """Backup SSH shutdown"""
    cmd = f'ssh ubuntu@{vm_ip} "sudo shutdown -h now"'
    result = subprocess.run(cmd, shell=True, capture_output=True)
    if result.returncode == 0:
        log("SSH shutdown command sent")
    else:
        log("SSH shutdown failed (VM may already be off)")

def main():
    if len(sys.argv) != 3:
        print("Usage: ./auto_complete.py <vm_name> <vm_ip>")
        print("Example: nohup ./auto_complete.py 'your-vm-name' '69.19.137.227' > monitor.log 2>&1 & ")
        print("Example: ./auto_complete.py my-training-vm 69.19.137.227")
        sys.exit(1)

    vm_name = sys.argv[1]
    vm_ip = sys.argv[2]
    api_key = "2d6ac29b-eb66-4f19-b056-1008d03db28e"

    log("Starting auto-monitor script...")
    log(f"Looking up VM: {vm_name}")

    # Get VM ID
    vm_id = get_vm_id(vm_name, api_key)
    if not vm_id:
        sys.exit(1)

    log(f"Found VM ID: {vm_id}, IP: {vm_ip}")
    log(f"Monitoring remote process: lora-model-training.py on {vm_ip}")

    # Monitor training process
    while monitor_remote_process(vm_ip):
        log("Remote training still running... checking again in 60 seconds")
        time.sleep(60)

    log("Remote training completed! Starting file copy...")

    # Copy results
    copy_success = copy_results(vm_ip)

    if copy_success:
        log("File copy successful! Shutting down remote VM...")

        # Stop VM
        stop_vm(vm_id, api_key)
        delete_vm(vm_id, api_key)

        # Wait and backup shutdown
        log("Waiting 60 seconds before backup shutdown...")
        time.sleep(60)
        log("Sending backup shutdown command via SSH...")
        ssh_shutdown(vm_ip)

    else:
        log("File copy failed! Still shutting down VM...")
        log("Sending backup shutdown command via SSH...")
        ssh_shutdown(vm_ip)
        delete_vm(vm_id, api_key)

if __name__ == "__main__":
    main()

