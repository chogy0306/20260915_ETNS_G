# ETNS TODO APP

Python Flask로 만든 간단한 할일 관리 웹앱입니다.

## 기능

- 할일 추가
- 할일 완료 체크 / 해제
- 할일 삭제
- 남은 할일 개수 표시

## 기술 스택

- Python / Flask
- SQLite (파일 DB, `todo.db`)
- HTML / CSS (별도 JS 프레임워크 없음)

## 실행 방법

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5000` 접속.

## 폴더 구조

```
ETNS_TODO_APP/
├── app.py                 # Flask 앱 (라우트, DB 처리)
├── requirements.txt       # 의존성 (Flask)
├── templates/
│   └── index.html         # 메인 화면
└── static/
    └── style.css          # 스타일
```
