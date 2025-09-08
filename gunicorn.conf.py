from multiprocessing import cpu_count

bind = "0.0.0.0:8000"  # фиксируем внутренний порт
worker_class = "uvicorn.workers.UvicornWorker"
workers = max(2, min(4, cpu_count() // 2))

timeout = 120
keepalive = 5
graceful_timeout = 30

loglevel = "info"
accesslog = "-"
errorlog = "-"

preload_app = True
max_requests = 1000
max_requests_jitter = 100
lifespan = "on"
