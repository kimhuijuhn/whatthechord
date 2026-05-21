import time

start = time.perf_counter()
for i in range(100000):
    i * i
end = time.perf_counter()

print(f"start: {start}")
print(f"end: {end}")
print(f"elapsed: {end - start}")