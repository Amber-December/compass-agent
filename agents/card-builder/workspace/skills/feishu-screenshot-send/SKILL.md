---
name: feishu-screenshot-send
description: Capture screenshots on this Windows machine and send them directly to Lu in Feishu. Use when the user asks to 截图, 截个屏, screen capture, screenshot current screen, or send a screenshot/image to the current Feishu chat. This skill is specifically for: (1) Windows screenshot capture via Python Pillow ImageGrab, (2) saving images into OpenClaw media allowlist directories, and (3) sending local images to Feishu with `openclaw message send --channel feishu --media`.
---

# Feishu Screenshot Send

Use the existing Windows screenshot pipeline on this machine.

## Default paths

- Screenshot script: `C:\Users\Administrator\.openclaw\workspace\scripts\take_screenshot.py`
- Media output dir: `C:\Users\Administrator\.openclaw\media`
- Example target user (Lu): `ou_84d759d8c85d265c91c1b18650c9b9e7`
- Default Feishu account: `main`

## Workflow

1. Capture the screenshot with Python Pillow, not PowerShell Forms.
2. Save the file under `C:\Users\Administrator\.openclaw\media` or another OpenClaw allowlisted media root.
3. Send the image with explicit Feishu CLI messaging.
4. Confirm success using the returned JSON payload.

## Capture screenshot

Run:

```powershell
python C:\Users\Administrator\.openclaw\workspace\scripts\take_screenshot.py current-screen.png
```

If the user wants a timestamped screenshot, omit the filename:

```powershell
python C:\Users\Administrator\.openclaw\workspace\scripts\take_screenshot.py
```

## Send image to Feishu

Run:

```powershell
openclaw message send --channel feishu --account main --target ou_84d759d8c85d265c91c1b18650c9b9e7 --media C:\Users\Administrator\.openclaw\media\current-screen.png --json
```

## Important rules

- Prefer `C:\Users\Administrator\.openclaw\media` for screenshots that will be sent to Feishu.
- Do not rely on generic reply attachments when the user explicitly wants the image sent in the Feishu window.
- Prefer explicit CLI send for Feishu media.
- If the send fails, check that the file lives under an allowlisted local media root.
- If Pillow import fails, repair Python/Pillow before attempting alternative screenshot methods.

## One-shot combined flow

1. Capture:
   - `python C:\Users\Administrator\.openclaw\workspace\scripts\take_screenshot.py current-screen.png`
2. Send:
   - `openclaw message send --channel feishu --account main --target ou_84d759d8c85d265c91c1b18650c9b9e7 --media C:\Users\Administrator\.openclaw\media\current-screen.png --json`

## Related local knowledge

For environment-specific details, see:
- `C:\Users\Administrator\.openclaw\workspace\TOOLS.md`
