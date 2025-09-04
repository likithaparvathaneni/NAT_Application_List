from netmiko import ConnectHandler
import threading
import time

def detect(HOST, USERNAME, PASSWORD, semaphore):
    device = {
        "device_type": "autodetect",
        "host": HOST,
        "username": USERNAME,
        "password": PASSWORD,
        "timeout": 20,
        "global_delay_factor": 4
    }

    try:
        net_connect = ConnectHandler(**device)
        time.sleep(2)
        net_connect.send_command("terminal pager 0")
    except:
        k = 2
    finally:
        semaphore.release()  # Release the semaphore when the thread is done

def main():
    start_time = time.time()  # Record the start time

    with open("passwords.txt", "w") as f:
        for i in range(100):
            f.write(f"{i},{i},{i}\n")

    with open("passwords.txt", "r") as f:
        threads = []
        semaphore = threading.Semaphore(15)  # Limit to 4 concurrent threads
        L = list(f.readlines())
        for i in range(len(L)):
            item = L[i]
            h, u, p = item.strip().split(",")
            semaphore.acquire()  # Acquire the semaphore before starting a new thread
            thread = threading.Thread(target=detect, args=(h, u, p, semaphore))
            threads.append(thread)
            thread.start()

    for thread in threads:
        thread.join()

    end_time = time.time()  # Record the end time
    elapsed_time = end_time - start_time  # Calculate the elapsed time
    print(f"All Checked. Time taken: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
