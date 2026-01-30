from app.tasks.email_tasks import send_test_email
import time

print("Enqueuing task 'send_test_email' to run in 10 seconds...")
# 使用 apply_async 的 countdown 参数
task = send_test_email.apply_async(countdown=10)
print(f"Task ID: {task.id}")
print("Done. Waiting for task to execute in worker...")

# 保持运行几秒钟以便看到控制台输出（如果我们在同一个进程查看1