# flask_web_project

## Project setup

터미널 열기 > command prompt 실행

```python
where python #3.10으로 설정
python -m venv venv
venv/Scripts/activate
pip install -r requirements.txt
python.exe -m pip install --upgrade pip
```

flask_web_project 폴더에서 .env 파일 생성 후 아래 내용 추가

```python
FLASK_APP=apps.app:create_app('local')
FLASK_ENV=development
FLASK_DEBUG=1
```
apps/config.py 시크릿키 추가
```python
class BaseConfig:
    SECRET_KEY = ''
    WTF_CSRF_SECRET_KEY = ''
```
## flask db setting

```python
flask db init
flask db migrate
flask db upgrade
```


## Project run

```python

flask_web_project 폴더에서 flask run 실행

주소창에 http://127.0.0.1:5000/auth/signup 실행
```
