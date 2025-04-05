FROM python:3.9
EXPOSE 8501
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt

# NLTK 데이터 사전 다운로드
RUN python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

COPY . .

# Command overriden by docker-compose
CMD streamlit run app.py
