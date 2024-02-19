FROM jupyter/base-notebook
WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt && rm Dockerfile requirements.txt
ENV JUPYTER_ENABLE_LAB=yes

CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.password=''"]
