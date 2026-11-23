# Installation

To run the project on your own PC please first install Ollama and then run the following commands in powershell

git clone <https://github.com/BradleyCurtisDev/AI_IntegrationTask>
cd AI_IntegrationTask
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
ollama pull phi3:mini
python main.py
