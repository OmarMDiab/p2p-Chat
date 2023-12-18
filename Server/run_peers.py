'''
program to run multiple peers at the same time in external cmd

Note: you have to run registry.py first
'''

import subprocess
import time

def run_peer_in_cmd(script_path):
    command = f"start cmd /K python {script_path}"
    subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    num_peers=4
    # Replace 'peer_main.py' with the actual path to your script
    peer_path = "peer_main.py"

    for i in range(num_peers):
        # Run peer_main.py in three different cmd windows
        run_peer_in_cmd(peer_path)
        time.sleep(0.5)  # Add a small delay between cmd launches
 