import undetected_chromedriver as uc

options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--blink-settings=imagesEnabled=false')


driver = uc.Chrome(
    options=options
)
