# services.py

from devices.models import (
    Device, 
    Profile, 
    ScreenFlow,
)


def create_device():
    device = Device()
    device.save()
    Profile(device=device).save()
    return device.id


def update_device(device_id, **kwargs):
    device = Device.objects.filter(id=device_id).update(**kwargs)
    return device


def delete_device(device_id):
    device = Device.objects.get(id=device_id)
    device.delete()


def get_device_by_id(device_id):
    try:
        return Device.objects.get(id=device_id)
    except Device.DoesNotExist:
        return None


def list_devices():
    return Device.objects.all()


def toggle_card_status(device_id, new_status):
    device = Device.objects.get(id=device_id)
    device.status = new_status
    device.save()
    return device

# def link_device_to_user(device_id, user_id):
#     device = Device.objects.get(id=device_id)
#     user = User.objects.get(id=user_id)
#     device.user = user
#     device.save()
#     return device

# def unlink_device_from_user(device_id):
#     device = Device.objects.get(id=device_id)
#     device.user = None
#     device.save()
#     return device


def log_screen_flow(device_id, screen_name, button_pressed):
    device = Device.objects.get(id=device_id)
    ScreenFlow.objects.create(
        device=device, screen_name=screen_name, button_pressed=button_pressed)

# def get_screen_flow_stats(screen_name):
#     return ScreenFlow.objects.filter(screen_name=screen_name).values('button_pressed').annotate(total=Count('id'))

# def update_last_access(device_id, timestamp):
#     device = Device.objects.get(id=device_id)
#     device.last_access = timestamp
#     device.save()
#     return device

# def usage_analysis_per_device(device_id):
#     actions = ScreenFlow.objects.filter(device_id=device_id).values('button_pressed').annotate(count=Count('id'))
#     return actions
