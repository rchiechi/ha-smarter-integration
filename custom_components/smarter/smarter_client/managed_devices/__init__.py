"""
Module containing wrappers for specific devices
"""
from smarter_client.domain import Network, Device
from smarter_client.managed_devices.kettle_v3 import SmarterKettleV3
from smarter_client.managed_devices.base import BaseDevice


def load_from_network(network: Network, user_id: str) -> list[Device]:
    """
    Get devices from a given network
    """
    network.fetch()
    return (
        wrapper for wrapper in
        (
            get_device_wrapper(device, user_id)
            for device in network.associated_devices
        )
        if wrapper is not None
    )


def get_device_wrapper(device: Device, user_id: str):
    """
    Get a device wrapper for a specific user by inferring the correct type
    from the device properties
    """
    device.fetch()
    model = device.status.get('device_model')
    match model:
        case 'SMKET01':
            managed = SmarterKettleV3.from_device(device, user_id)
            managed.subscribe_status()
            return managed
        case _:
            print(f'Unknown device model: {model}')
