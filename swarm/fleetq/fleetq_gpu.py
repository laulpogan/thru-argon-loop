"""fleetq: enable Cycles GPU (OPTIX, then CUDA) when present; returns 'GPU' or 'CPU'."""
import bpy
def enable():
    try:
        p=bpy.context.preferences.addons['cycles'].preferences
        for t in ('OPTIX','CUDA'):
            try:p.compute_device_type=t
            except TypeError:continue
            (p.refresh_devices if hasattr(p,'refresh_devices') else p.get_devices)()
            devs=[d for d in p.devices if d.type==t]
            if devs:
                for d in p.devices:d.use=(d.type==t)
                print('FLEETQ_GPU',t,[d.name for d in devs],flush=True);return 'GPU'
    except Exception as e:print('FLEETQ_GPU_FAIL',type(e).__name__,e,flush=True)
    return 'CPU'
