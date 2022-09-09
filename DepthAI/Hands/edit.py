#!/usr/bin/env python3

from HandTrackerRenderer import HandTrackerRenderer
from HandTracker2 import HandTracker

tracker = HandTracker()
renderer = HandTrackerRenderer(tracker=tracker)

while True:
    frame, hands, _ = tracker.next_frame()
    if frame is None: break
    frame = renderer.draw(frame, hands)
    key = renderer.waitKey(delay=1)
    if key == 27 or key == ord('q'):
        break
renderer.exit()
tracker.exit()
