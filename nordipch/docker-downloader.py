from ipvProxy import IProxy


if __name__ == "__main__":
    npx = IProxy(production=False)
    npx.download_ovpn_files()
