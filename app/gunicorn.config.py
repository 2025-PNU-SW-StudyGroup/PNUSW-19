import multiprocessing

workers = 3
worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "app.main:app"
timeout = 180
loglevel = "info"
bind = "0.0.0.0:5455"
max_requests = 100
max_requests_jitter = 100

accesslog = "app/logs/access.log"
errorlog = "app/logs/error.log"