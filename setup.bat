powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
uv venv
uv lock
uv sync
pause