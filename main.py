from ny_times_scrapper import ScrapperNYTimes


def main():
    scrapper = ScrapperNYTimes("config.ini", "logs/logs.log")
    try:
        scrapper.run()
    finally:
        scrapper.finish()


if __name__ == "__main__":
    main()
