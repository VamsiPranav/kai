# kai

Find a detailed explanation of the project in our team's confluence page [here](https://confluence.oraclecorp.com/confluence/display/DDA/TEAM+4%3A+GenAI+Hackathon+Design+Document).


Please follow these steps mentioned below to run this project in your local.

## Installation
Clone the repository
``` bash
git clone https://github.com/VamsiPranav/kai.git
cd kai
```

Create a Virtual Environment and activate it
``` bash
python3 -m venv .venv
source .venv/bin/activate
```

Install python dependencies
``` bash 
python3 -m pip install -r requirements.txt
```

Install npm dependencies for Front-End
``` bash
npm install
```

Install [Ollama](https://ollama.com/) and run the below script to download llm model
``` bash
ollama pull llama3.1:8b
```


## Execution
Start the Back-End server for langchain via Flask
``` bash
python3 app.py
```

Start the Front-End server in another terminal 
``` bash
python3 -m http.server
```

Open the below link in a browser <br>
[http://localhost:8000](http://localhost:8000)