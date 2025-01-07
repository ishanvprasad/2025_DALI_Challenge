# Use a base Python image
FROM python:3.9-slim

# Set environment variable to avoid buffering of stdout/stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt /app/

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project folder into the container, including the 'Data' folder
# Excluding dotfiles and unnecessary files as specified in .dockerignore
COPY . /app/

EXPOSE 8050

# Specify the command to run your application (adjust if needed)
CMD ["python", "GUI.py"]
