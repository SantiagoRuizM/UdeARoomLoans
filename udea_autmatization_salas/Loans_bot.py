import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def first():

    driver = webdriver.Chrome("storage/chromedriver.exe")

    driver.get("https://biblioteca.udea.edu.co/turnosudea/#/")
    search_box = driver.find_element(By.ID, "usuario")
    search_box.send_keys("usuario")
    search_box = driver.find_element(By.ID, "clave")
    search_box.send_keys("contraeña")
    search_box.send_keys(Keys.RETURN)

    driver.get("https://biblioteca.udea.edu.co/turnosudea/#/sala/34/equipo/Sala%201")

    time.sleep(100)
