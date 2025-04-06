#!/usr/bin/env python3
"""
 Script to rotate Digital Ocean snapshots
"""

from time import time, sleep
from os import getenv
from pydo import Client

client = Client(token=getenv("DIGITALOCEAN_TOKEN"))

droplet_list = client.droplets.list()
droplets = droplet_list.get("droplets") if 'droplets' in droplet_list else []
print(f"Found {len(droplets)} existing droplets")

snapshots_list = client.snapshots.list(resource_type="droplet")
snapshots = snapshots_list.get(
    "snapshots") if 'snapshots' in snapshots_list else []

print(f"Found {len(snapshots)} existing droplet snapshots")

# Create a snapshot for each droplet
if len(droplets) > 0:
    for droplet in droplets:
        droplet_name = droplet.get('name')
        snapshot_name = f"{droplet_name}-s-{int(time())}"

        result = client.droplet_actions.post(
            droplet_id=droplet.get('id'),
            body={
                "type": "snapshot",
                "name": snapshot_name,
            }
        )

        if result.get('action') is None or result.get('action').get('status') != 'in-progress':
            print(f"Failed to create snapshot for {droplet_name}")
            print(f"Error: {result}")
            continue

        action_id = result.get('action', {}).get('id')
        action_status = result.get('action', {}).get('status')
        print(
            f"Queued snapshot: {action_id}, {action_status}, {snapshot_name}")


if len(snapshots) > 0:
    # Delay for a few to allow snapshots operations to start
    sleep(10)

    print("Deleting previous snapshots")
    for snapshot in snapshots:
        client.snapshots.delete(snapshot.get('id'))

print("Done")
