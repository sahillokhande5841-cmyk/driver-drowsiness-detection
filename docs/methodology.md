# Methodology

This document explains how the system decides whether a driver is drowsy — the detection logic itself, not how the code is organized around it. If you're looking for the system design, see `ARCHITECTURE.md`.

## Camera capture

Everything starts with a plain webcam feed, read frame by frame with OpenCV. There's no special camera requirement — any standard webcam works, since the detection relies entirely on facial geometry rather than depth or infrared data. Each frame is just a regular BGR image at whatever resolution the camera provides.

## Face detection and MediaPipe Face Mesh

Before anything can be measured, the system needs to know where the face is and where its features are. This is handled by MediaPipe's Face Mesh, which takes a raw frame and returns 468 facial landmark points — a dense mesh covering the eyes, eyebrows, nose, mouth, and jawline, each given as a normalized (x, y) position within the frame.

Face Mesh does the face detection step internally, so there's no separate face-detection stage before it. If a face isn't found in a given frame, that frame is simply skipped and the loop moves on to the next one.

Only a small, fixed subset of those 468 points is actually used downstream — six points per eye, a handful around the mouth, and six more for head pose. The rest of the mesh isn't needed for this system, but MediaPipe returns the whole thing anyway.

## Landmark extraction

Once a face is found, the relevant landmark points are pulled out for the frame: the eye contours, the mouth contour, and a small set of points used for head orientation (nose tip, both eye corners, both mouth corners, and the chin). These are just coordinates — the actual meaning gets computed in the next steps.

## Calibration

Not everyone's eyes look the same when fully open — it depends on the person, the camera angle, and how close they are to the lens. A fixed "eyes closed" threshold that works for one person can be wrong for another. To deal with this, the system runs a short calibration phase right after starting: for the first five seconds, it just watches how open the driver's eyes normally are and averages that out. The actual closed-eye threshold is then set as a fraction of that baseline (75% of the average), so it adapts to the individual instead of assuming everyone's eyes behave the same way. Nothing is flagged as drowsy during this window — it's purely establishing a baseline.

## Eye Aspect Ratio (EAR)

Eye closure is measured with the Eye Aspect Ratio, a standard technique for turning eye landmarks into a single number that tracks how open or closed an eye is. The idea is simple: an open eye is tall relative to its width, and a closing eye gets flatter. By comparing the vertical distance between the top and bottom eyelid landmarks to the horizontal distance across the eye, you get a ratio that drops sharply when the eye closes and stays fairly stable while it's open.

This is calculated separately for each eye using six landmark points per eye, then averaged into a single EAR value per frame. When that value drops below the calibrated threshold for a sustained number of frames — not just a single blink — the eye is considered closed for fatigue purposes. A single blink shouldn't trigger anything; the system is specifically watching for eyes staying closed longer than a normal blink would.

## Mouth Aspect Ratio (MAR)

Yawning is detected the same way, applied to the mouth instead of the eyes. The Mouth Aspect Ratio compares how open the mouth is vertically to its width. During normal talking or resting, this stays low; during a yawn, it spikes and stays elevated for a stretch of frames rather than a quick flicker.

A yawn is only counted once the mouth has stayed open past a minimum frame count — this filters out talking, brief mouth movements, or a single wide frame from being misread as a yawn.

## Head pose estimation

Beyond eyes and mouth, the system also watches head position, since a drooping or nodding head is one of the clearest signs someone is falling asleep. This uses a handful of landmarks — the nose tip, eye corners, mouth corners, and chin — matched against a generic 3D face model to estimate how the head is oriented in space, expressed as pitch, yaw, and roll angles.

Pitch is what matters most here: it captures the up/down tilt of the head. When pitch drops past a threshold and stays there for a sustained number of frames, the head is considered "down" — the kind of slow forward droop that happens when someone's nodding off, as opposed to a quick glance downward.

## Fatigue score

None of these signals — closed eyes, a yawn, a dropped head — is reliable enough on its own to call someone drowsy. People blink, look down, and yawn normally all the time. So instead of reacting to any single signal, the system accumulates a fatigue score over time.

The score goes up a little for each frame the eyes are closed, goes up more when the head is down, and jumps by a larger amount each time a yawn completes — yawning being a stronger indicator than a moment of eye closure. When none of those things are happening, the score decays slowly back down. This means a driver who blinks a bit more than usual for a few seconds won't trip anything, but someone whose eyes stay closed, head stays down, or who's yawning repeatedly will see the score climb and stay elevated. The score is capped at both ends so it can't run away in either direction.

## Driver status

The fatigue score by itself isn't very readable, so it's translated into three plain states: Normal, Tired, and Drowsy, based on where the score currently sits. Normal means everything is within an expected range. Tired is a middle zone — the score has climbed enough to suggest early signs of fatigue, but not enough to be an emergency. Drowsy is the top band, reserved for a score high enough that the driver is very likely nodding off.

This status is what actually gets shown to the user and drives the alarm — the raw score is more of an internal signal that feeds into it.

## Alarm generation

When the status crosses into Drowsy, the system plays a looping audio alarm to get the driver's attention immediately. The alarm keeps playing continuously — not just once — for as long as the status stays at Drowsy, since a single sound is easy to sleep through. As soon as the score comes back down and the status drops out of Drowsy, the alarm stops on its own.

The alarm is deliberately tied to the status, not the raw score or any single frame's readings — this avoids the alarm firing and stopping repeatedly on borderline frames, since the score only moves into Drowsy after sustained evidence of fatigue rather than a momentary blip.