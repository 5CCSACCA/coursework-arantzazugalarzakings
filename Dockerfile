FROM python:3.10-slim 
WORKDIR /coursework-arantzazugalarzakings 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 
COPY . . 
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port"", "8000"]
