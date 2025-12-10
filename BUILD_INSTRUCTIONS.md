# How to Build MIVES-APP Executable

This guide explains how to repackage the MIVES-APP application into a single executable file (`.exe`) after making changes to the code.

## Prerequisites

- **Python 3.10+** installed.
- **Virtual Environment** set up at `.venv` (this should already be there if you've been working on the project).

## Build Steps

1. **Open a Terminal** in the project root directory (`d:\Git\MIVES-APP`).

2. **Activate the Virtual Environment**:
   - **PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Command Prompt (cmd)**:
     ```cmd
     .venv\Scripts\activate.bat
     ```

3. **Run the Build Command**:
   Execute the following command to build the executable using the existing configuration file (`MIVES_Tool.spec`):
   ```powershell
   pyinstaller --clean --noconfirm MIVES_Tool.spec
   ```

4. **Locate the Executable**:
   Once the process completes successfully, the new executable will be located at:
   `dist\MIVES_Tool.exe`

## Troubleshooting

- **Build Fails**: If the build fails, try deleting the `build` and `dist` folders and running the command again.
- **Missing Dependencies**: If you added new libraries to `requirements.txt`, make sure to install them in the virtual environment first (`pip install -r requirements.txt`) and check if they need to be added to `hiddenimports` in `MIVES_Tool.spec`.
