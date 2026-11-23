# Installation

To run the project on your own PC please first install Ollama and then run the following commands in powershell

git clone <https://github.com/BradleyCurtisDev/AI_IntegrationTask> <br />
cd AI_IntegrationTask <br />
python -m venv .venv <br />
.\.venv\Scripts\Activate.ps1 <br />
pip install -r requirements.txt <br />
ollama pull phi3:mini <br />
python main.py <br />
