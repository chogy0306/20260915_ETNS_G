# ETNS TODO APP

Python Flask로 만든 간단한 할일 관리 웹앱입니다.

## 기능

- 할일 추가
- 할일 완료 체크 / 해제
- 할일 삭제
- 남은 할일 개수 표시

## 기술 스택

- Python / Flask
- PostgreSQL (Supabase)
- HTML / CSS (별도 JS 프레임워크 없음)
- 배포: Vercel

## 실행 방법

`.env.example`을 참고해 `.env` 파일에 Supabase 연결 문자열(`DATABASE_URL`)을 넣어주세요.

```bash
pip install -r requirements.txt
python app.py
```

브라우저에서 `http://127.0.0.1:5000` 접속.

## 폴더 구조

```
ETNS_TODO_APP/
├── app.py                 # Flask 앱 (라우트, DB 처리)
├── requirements.txt       # 의존성 (Flask, psycopg2, python-dotenv)
├── vercel.json             # Vercel 배포 설정
├── .env.example            # 환경변수 예시 (DATABASE_URL)
├── templates/
│   └── index.html         # 메인 화면
└── static/
    └── style.css          # 스타일
```
