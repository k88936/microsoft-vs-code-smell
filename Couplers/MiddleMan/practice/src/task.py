class DataProvider:
    def fetch_data(self) -> str:
        return "Data from the server"


class Client:
    def process_data(self) -> str:
        data_provider = DataProvider()
        return data_provider.fetch_data()

def main() -> None:
    client = Client()
    print(client.process_data())


if __name__ == "__main__":
    main()
