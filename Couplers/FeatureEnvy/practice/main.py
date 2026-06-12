from car import Car
from driver import Driver

def main() -> None:
    car = Car(5)
    driver = Driver(car)
    driver.drive_to("Belgrade")

if __name__ == "__main__":
    main()
