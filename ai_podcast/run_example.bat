@echo off
REM Example run: generate a short podcast episode
REM Prerequisites: .env configured, Ollama running, FFmpeg installed
cd /d "%~dp0"
python main.py "The benefits of meditation" -o example_episode -m 5
echo.
echo Done. Check output/example_episode.mp3
