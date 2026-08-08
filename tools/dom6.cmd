@echo off
rem ---------------------------------------------------------------------------
rem  dom6 - open the Dominions 6 battle analyst in this project.
rem
rem    dom6                          start an interactive session
rem    dom6 "why did I lose in Trackless Woods?"
rem    dom6 "summarise turn 9 for Bandar Log"
rem
rem  The analyst skill is project-scoped, so this only needs to run Claude Code
rem  with the repository as the working directory.
rem
rem  Override the location with:  set DOM6_PROJECT=<path to your checkout>
rem  Install with:               py scripts\install_dom6_command.py
rem ---------------------------------------------------------------------------
setlocal

if not defined DOM6_PROJECT set "DOM6_PROJECT=C:\Users\Alex\DominionsSaveParser"

if not exist "%DOM6_PROJECT%\.claude\skills\dominions6-analyst\SKILL.md" (
    echo dom6: analyst skill not found under "%DOM6_PROJECT%".
    echo       Set DOM6_PROJECT to your DominionsSaveParser checkout.
    exit /b 1
)

cd /d "%DOM6_PROJECT%" || exit /b 1
claude %*
