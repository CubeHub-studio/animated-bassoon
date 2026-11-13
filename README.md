# NOVA DESK

A tiny productivity corner for Windows: a custom animated starfield, a focus timer, and an automatically saved scratchpad.

## Features

- Original dark, space-inspired desktop interface
- Animated starfield header
- Focus timer presets: 5, 25, and 50 minutes
- Start, pause, resume, and reset controls
- Scratchpad that saves locally as you type
- No accounts, network calls, telemetry, or paid services

## Get the Windows app

Open the repository's **Actions** tab, select **Build NOVA DESK for Windows**, and run the workflow with **Run workflow**. When it finishes, download the `NOVA-DESK-Windows-x64` artifact from the workflow run.

The executable is also built automatically when app or build files are changed on the default branch.

## Run from source

Requires Python 3.10 or newer. Tkinter is included with most standard Windows Python installations.

```powershell
python app.py
```

## Build a Cubes Archive (.epa)

NOVA DESK includes a `main.py` EPA entrypoint that launches the existing `app.py`. No additional runtime packages are required for the EPA version; Tkinter and the rest of the app use Python's standard library.

With Cubes Archive installed, run these commands from the repository directory:

```powershell
cubes create . -o ..\NOVA-DESK.epa --name "NOVA DESK" --app-version "1.0.0" --publisher "Cubes, Studio." --description "A focus timer and scratchpad desktop app."
cubes verify ..\NOVA-DESK.epa
cubes inspect ..\NOVA-DESK.epa
cubes run ..\NOVA-DESK.epa
```

The archive includes the project files in this repository. Cubes Archive launches the Python entrypoint using the installed Python interpreter, so the target Windows installation needs Python with Tkinter available. EPA is not a standalone executable and does not bundle Python.

The scratchpad and last timer preset are stored locally in `%USERPROFILE%\.nova_desk.json`.

## Build a standalone Windows executable

This is a separate build path from EPA and requires PyInstaller:

```powershell
python -m pip install -r requirements.txt
pyinstaller --noconfirm --clean --onefile --windowed --name "NOVA-DESK" app.py
```

The executable will be in `dist\NOVA-DESK.exe`.
