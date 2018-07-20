
from tungsten_vrouter_api.vrouter_api import TungstenVRouterApi

def interface_register(vm, vmi, iface_name, project=None, vrouter_api=None):
    api = vrouter_api or TungstenVRouterApi()
    mac = vmi.virtual_machine_interface_mac_addresses.mac_address[0]
    if project:
        proj_id = project.uuid
    else:
        proj_id = None
    api.add_port(vm.uuid, vmi.uuid, iface_name, mac, display_name=vm.name,
                 vm_project_id=proj_id)


def interface_unregister(vmi_uuid):
    api = TungstenVRouterApi()
    api.delete_port(vmi_uuid)
