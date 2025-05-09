import logging

# SQLAlchemy 로그 핸들러 설정
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
sqlalchemy_logger.setLevel(logging.INFO)

for handler in sqlalchemy_logger.handlers[:]:
    sqlalchemy_logger.removeHandler(handler)

# 파일 핸들러 추가
file_handler = logging.FileHandler("app/logs/sqlalchemy.log")
file_handler.setLevel(logging.INFO)

# 로그 포맷 설정
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
file_handler.setFormatter(formatter)

# 핸들러 등록
sqlalchemy_logger.addHandler(file_handler)

sqlalchemy_logger.propagate = False