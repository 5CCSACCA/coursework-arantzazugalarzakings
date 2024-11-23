FROM python:3.10-slim 

# Set the working directory inside the container
WORKDIR /coursework-arantzazugalarzakings

# Copy the requirements file to the container
COPY requirements.txt requirements.txt

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application files to the container
COPY . .

# Command to run the FastAPI app with Uvicorn

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

