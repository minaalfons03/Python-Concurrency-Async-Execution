import asyncio
import time
import threading


# =============================================================================
# Task 1: Pure Synchronous Execution
# =============================================================================
def sync_task(name, delay):
    print(f"{name} started")
    time.sleep(delay)
    print(f"{name} finished")


def run_sync_tasks():
    start = time.time()

    for i in range(1, 9):
        sync_task(f"t{i}", 1)

    print("total time ", time.time() - start)  # 8 secs


# =============================================================================
# Task 2: Async Sequential (Without gather)
# =============================================================================
async def async_task(name, delay):
    print(f"{name} started")
    await asyncio.sleep(delay)
    print(f"{name} finished")


async def main_sequential():
    start = time.time()

    for i in range(1, 9):
        await async_task(f"t{i}", 1)  # wait for each one -> same as sync

    print("total time ", time.time() - start)  # 8 secs


# =============================================================================
# Task 3: Async Concurrent Using gather()
# =============================================================================
async def main_gather():
    start = time.time()

    tasks = []
    for i in range(1, 9):
        tasks.append(async_task(f"t{i}", 1))

    await asyncio.gather(*tasks)  # all start together

    print("total time ", time.time() - start)  # 1 sec


# =============================================================================
# Task 4: Blocking CPU Inside Event Loop
# =============================================================================
def heavy_cpu_function():
    total = 0
    for i in range(30_000_000):
        total += i * i
    return total


async def light_task():
    for i in range(6):
        print("light task tick", i)
        await asyncio.sleep(0.5)


async def cpu_inside_loop():
    print("heavy cpu started")
    heavy_cpu_function()  # no await -> blocks the event loop
    print("heavy cpu finished")


async def main_blocking():
    start = time.time()

    await asyncio.gather(light_task(), cpu_inside_loop())
    # the ticks stop while the heavy function is running

    print("total time ", time.time() - start)


# =============================================================================
# Task 5: Yielding Inside Single Thread
# =============================================================================
async def heavy_cpu_with_yield():
    print("heavy cpu started")
    total = 0
    for i in range(30_000_000):
        total += i * i
        if i % 1_000_000 == 0:
            await asyncio.sleep(0)  # give the event loop a chance to switch
    print("heavy cpu finished")
    return total


async def main_yield():
    start = time.time()

    await asyncio.gather(light_task(), heavy_cpu_with_yield())
    # light task can run between the yields

    print("total time ", time.time() - start)


# =============================================================================
# Task 6: Using asyncio.to_thread()
# =============================================================================
async def cpu_in_thread():
    print("heavy cpu started")
    await asyncio.to_thread(heavy_cpu_function)  # runs in another thread
    print("heavy cpu finished")


async def main_to_thread():
    start = time.time()

    await asyncio.gather(light_task(), cpu_in_thread())
    # light task keeps running smoothly

    print("total time ", time.time() - start)


# =============================================================================
# Task 7: Race Condition Simulation
# =============================================================================
counter = 0


def increase_without_lock():
    global counter
    for _ in range(20000):
        temp = counter
        time.sleep(0)  # let another thread jump in (makes the race easy to see)
        counter = temp + 1


lock = threading.Lock()


def increase_with_lock():
    global counter
    for _ in range(20000):
        with lock:
            temp = counter
            time.sleep(0)
            counter = temp + 1


def run_race_condition():
    global counter

    # without lock
    counter = 0
    threads = []
    for i in range(5):
        t = threading.Thread(target=increase_without_lock)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("without lock ", counter, "expected 100000")

    # with lock
    counter = 0
    threads = []
    for i in range(5):
        t = threading.Thread(target=increase_with_lock)
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("with lock ", counter, "expected 100000")


# =============================================================================
# Task 8: Async + Thread Synchronization Hybrid
# =============================================================================
shared_counter = 0
shared_lock = threading.Lock()


def cpu_work(name):
    global shared_counter
    for i in range(20000):
        with shared_lock:
            shared_counter += 1


async def hybrid_task(name):
    print(f"{name} asked for cpu work")
    await asyncio.to_thread(cpu_work, name)  # cpu work runs in a thread
    print(f"{name} got the result")


async def main_hybrid():
    start = time.time()

    await asyncio.gather(
        hybrid_task("t1"),
        hybrid_task("t2"),
        hybrid_task("t3"),
        hybrid_task("t4"),
    )

    print("shared counter ", shared_counter, "expected 80000")
    print("total time ", time.time() - start)


# =============================================================================
# Run everything
# =============================================================================
if __name__ == "__main__":
    print("----- Task 1 -----")
    run_sync_tasks()

    print("----- Task 2 -----")
    asyncio.run(main_sequential())

    print("----- Task 3 -----")
    asyncio.run(main_gather())

    print("----- Task 4 -----")
    asyncio.run(main_blocking())

    print("----- Task 5 -----")
    asyncio.run(main_yield())

    print("----- Task 6 -----")
    asyncio.run(main_to_thread())

    print("----- Task 7 -----")
    run_race_condition()

    print("----- Task 8 -----")
    asyncio.run(main_hybrid())
