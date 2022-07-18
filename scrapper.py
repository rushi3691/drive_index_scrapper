from selenium import webdriver
from error import MyError
from utils import *
from selenium.webdriver.support.ui import WebDriverWait
from config import *
from logger import obj_processed
options = webdriver.ChromeOptions()
options.add_argument('-headless')
options.add_argument('-no-sandbox')
options.add_argument('-disable-dev-shm-usage')
options.add_argument('-incognito')

if USER and PASS:
    user_pass = f"{USER}:{PASS}@"
else:
    user_pass = ""
    
def scrapper(q, lock):
    global obj_processed

    while not q.empty():
        url, tries = q.get()
        if url is None:
            break

        tries_check = None
        try:
            if tries > 4:
                raise MyError(f"Tried five times {url}")
            tries_check = False
        except MyError as e:
            print(f"At tries_check - {e.msg} - {url}")
            tries_check = True
            continue
        finally:
            if tries_check == True:
                q.task_done()

        # t1 = time.time()

        driver_check = None
        try:
            driver = webdriver.Chrome(options=options)
            driver_check = False
        except Exception as e:
            print(f"At driver_check - {e} - {url}")
            q.put([url, tries])
            driver_check = True
            continue
        finally:
            if driver_check == True:
                q.task_done()

        get_check = None
        try:
            if user_pass in url:
                driver.get(url)
            else:
                url = url.replace("https://", f"https://{user_pass}")
                driver.get(url)
            get_check = False
        except Exception as e:
            driver.close()
            driver.quit()
            print(f"At get_check - {e} - {url}")
            q.put([url, tries])
            get_check = True
            continue
        finally:
            if get_check == True:
                q.task_done()

        if "exception" not in driver.title:
            load_check = None
            try:
                # ts = time.time()
                innerHTML = WebDriverWait(driver, 10).until(
                    is_loaded('list', driver))
                # print(innerHTML.get_attribute("innerHTML")[16:30])
                # print(f"{threading.currentThread().getName()} - time to load page ", time.time() - ts)
                load_check = False
            except Exception as e:
                driver.close()
                driver.quit()
                print(f"At load_check - {e} - {url}")
                q.put([url, tries+1])
                load_check = True
                continue
            finally:
                if load_check == True:
                    q.task_done()

                # driver.save_screenshot("file.png")
            total_length = finder(driver, 1)

            try:
                total_elements = driver.find_element_by_xpath(
                    "//*[@id='count']/span").text
                # if total_elements:
                #   print(f"{threading.currentThread().getName()} - found")
            except:
                total_elements = ""

            while not total_elements:
                screen_height = driver.execute_script(
                    "return document.body.scrollHeight;")   # get the screen height of the web
                driver.execute_script(f"window.scrollTo(0, {screen_height});")

                length = False
                try:
                    length = WebDriverWait(driver, 10).until(
                        scroll_load(total_length, driver))
                except Exception as e:
                    print(f"{e} - {url}")

                    # length = WebDriverWait(driver, 5).until(
                    #     scroll_load(total_length, driver))

                if length:
                    total_length = length

                try:
                    total_elements = driver.find_element_by_xpath(
                        "//*[@id='count']/span").text
                except:
                    total_elements = ""

            # print(f"total elements found: {total_elements} in {threading.currentThread().getName()}")
            # print(f"{threading.currentThread().getName()} - Time taken for function: {time.time()-t1}")
            file_writer(driver, lock, q)

            # driver.save_screenshot("file.png")
        else:
            print(f"{url} - {driver.title}")

        driver.close()
        driver.quit()
        with lock:
            obj_processed += 1
            print(f"total folders processed: {obj_processed}")
        # print(f"{threading.currentThread().getName()} - ending")
        q.task_done()