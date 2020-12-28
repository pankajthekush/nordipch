from ipvanish import change_ip



def docker_runner():
    while True:
        try:
            change_ip()
        except Exception:
            pass

if __name__ == "__main__":
    docker_runner()