import depthai as dai
from depthai_sdk import PipelineManager, PreviewManager, Previews

previews = [Previews.color.name, Previews.depth.name]
selectedPreview = Previews.color.name

pm = PipelineManager()
pm.createColorCam(previewSize=(480, 480), xout=True)
pm.createLeftCam(res=dai.MonoCameraProperties.SensorResolution.THE_480_P)
pm.createRightCam(res=dai.MonoCameraProperties.SensorResolution.THE_480_P)
pm.createDepth(useDepth=True)
pm.nodes.stereo.setRuntimeModeSwitch(True)

with dai.Device(pm.pipeline) as device:
    pm.createDefaultQueues(device)
    pv = PreviewManager(display=previews, depthConfig=dai.StereoDepthConfig(), createWindows=False)
    pv.createQueues(device)