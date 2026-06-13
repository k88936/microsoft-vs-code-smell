class Money:
    def __init__(self, dollars):
        self.dollars = dollars

    def get_cents(self):
        return int(self.dollars * 100 % 100)


def main():
    money = Money(28.27)
    cents = money.get_cents()
    print(cents)
if __name__ == "__main__":
    main()
