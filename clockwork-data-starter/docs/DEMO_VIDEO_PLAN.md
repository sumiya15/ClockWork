# Provisional ClockWork video plan

This is a plan for recording AFTER the application implements and verifies the actions. It is not evidence that the current server can do them.

No official video duration/format rule was supplied here. The Word blueprint contains a five-minute full walkthrough, which is an internal plan, not a verified submission rule. Keep that full rehearsal; provisionally create a three-minute screening highlight if the college/portal accepts it. Verify the actual limit before recording the final submission.

## One coherent fictional scenario

Use DEMO-APP-001 and its institution, stage obligation, pause interval and lease-validity obligation. The dataset's starting history is labelled synthetic. Its EVC processing clock has three completed paused days, while its expired lease has only a pending renewal. After the engine and authorized actions work, show the EVC escalation and human action, followed by saved history. Reset rehearsals using a new database filename, not by erasing existing work.

| Time | Screen and action | Exact provisional narration |
|---|---|---|
| 0:00-0:15 | Title plus Today view. Show `Student prototype`, `Synthetic data` and the fixed demo clock. | "ClockWork helps AICTE officials track approval and compliance actions. This demonstration uses fictional records and configurable example timelines." |
| 0:15-0:45 | Open DEMO-APP-001. Expand its EVC deadline explanation and pause history. | "This EVC task originally fell due on 24 October. Our example return rule paused processing for three days. ClockWork shows the supporting interval, the applied rule and the adjusted 27 October deadline. The responsible owner remains visible." |
| 0:45-1:15 | Open the same application's expired lease. Show pending renewal; an authorized officer verifies or rejects the actual uploaded synthetic evidence. | "The same application has an expired lease. A processing pause does not extend document validity. Uploading renewal evidence also does not verify it. The designated officer must inspect the evidence and record a decision." |
| 1:15-1:55 | Use an authorized, clearly labelled demo control to advance time across the EVC due and escalation thresholds. Open the actual recorded in-app notice and its reason. | "I am advancing simulated time, not changing the computer clock. We can now inspect the overdue action and the escalation reason. Each recorded notice identifies the obligation, recipient and rule. Repeating the same evaluation should not create another copy." |
| 1:55-2:25 | Sign in as the authorized task owner using an actual session. Record completion of the fictional EVC action with a required remark. | "The system supports the officer's work. In this fictional example, the authorized owner records the completed action. ClockWork does not conduct an inspection or grant approval automatically." |
| 2:25-2:45 | Reload, then reopen the case and timeline; use a verified restart if it fits. Show a missing-owner example held for correction. | "The saved action remains after reload. The timeline records who acted and what changed. When required information is missing, the system asks for correction rather than guessing an owner or deadline." |
| 2:45-3:00 | Limitations card containing only accurate current status. | "This is a student prototype with synthetic data. AICTE integration and external message delivery are mocked or pending unless separately demonstrated. Our next step is to validate rule settings with the applicable handbook and authorized users." |

Only say the narration if the corresponding feature actually works. If an item is still planned, remove that recorded segment or label it clearly as planned. Do not use a generated concept video, mock dashboard or static screenshot as proof of functioning code. Do not claim restart persistence from a simple page refresh.

## Free recording workflow

Use an installed screen recorder such as OBS Studio (https://obsproject.com/) or the recording function available on your computer. The official OBS guides were inspected: https://obsproject.com/kb/quick-start-guide and https://obsproject.com/kb/standard-recording-output-guide. Shotcut's official site identifies it as free and open source: https://shotcut.org/. This is not a claim that a particular installed version/export option was tested here.

1. Set the app to a readable desktop window and zoom until labels can be read at 1080p. Hide personal tabs, notifications and credentials. Keep the synthetic/demo-time labels visible.
2. In OBS, create a scene, add a Window Capture source for the browser, and add an Audio Input Capture for the microphone. Check the meter by speaking. Run a ten-second test and play it back before the full take.
3. Record to MKV so an interrupted recording is less likely to lose the whole take. Use OBS's remux function to produce MP4 if required. Verify the current installed options and the submission's codec/size rules before exporting.
4. Use an installed free editor such as Shotcut (https://shotcut.org/) to trim mistakes and add short, large text captions. Editing out waiting time is acceptable when it does not misrepresent how a feature works. Label role/session changes and simulated time jumps.
5. Keep narration louder than incidental system audio. Prefer no background music. Export a provisional 1920x1080 MP4 with readable text if no other format is required, then watch the exported file end to end.

## Rehearsal and backup

- Verify the exact submission duration, format, file size and link-access requirements with the coordinator.
- Rehearse the complete five-minute Word-document journey before selecting highlights.
- Use a fresh rehearsal database with the same deterministic data and rules. Preserve a stopped-server backup separately.
- Verify role boundaries, every recorded button, visible next owner, rule explanation and pending-versus-verified evidence.
- Verify at least one failure case and no duplicate notice after repeated evaluation.
- Confirm reload and separate-process persistence using actual checks; keep evidence.
- Prepare a local offline copy of the app and data, a clean exported video, a second video copy and a short actual-screen recording as backup.
- Keep screenshots of implemented screens. A concept diagram may explain future architecture, but label it as proposed.
