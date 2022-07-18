from urllib.parse import unquote
import os 
import re
from config import files_path, folders_path
##### defining scroll #####

def finder(driver,method):
  xdirs="//div[@id='list']/a"
  pdirs=driver.find_elements_by_xpath(xdirs)
  # ldirs=len(pdirs)
  # print(pdirs)
  xelms="//a[@class='list-group-item-action']"
  pelms=driver.find_elements_by_xpath(xelms)
  # lelms=len(pelms)
  # length=ldirs+lelms
  # print(f"folders: {ldirs}, files: {lelms}")
  if method == 1:
    return len(pdirs)+len(pelms)
  elif method == 2:
    return pdirs, pelms

def file_writer(driver, lock, q):
  dirs, files = finder(driver, 2)
  with lock:
    with open(files_path, 'a') as fl:
      for i in files:
        x = i.get_attribute('href')
        x = x.replace("?a=view", '')
        url = unquote(x)
        # y = url.replace("https://goc:goc@goc.goc2.workers.dev/7:/", "")
        reg = r"https://(\w+:\w+@)?([\w.-]+)(/\d:)/"
        y = re.sub(reg,"", url)
        flpath = os.path.dirname(y)
        cwd = os.getcwd()
        outpath = os.path.join(cwd, flpath)
        fl.write(x)
        fl.write("\n")
        fl.write(f"  dir={outpath}\n")

    with open(folders_path, "a") as fl:
      for i in dirs:
        x = i.get_attribute('href')
        q.put([x.strip(), 0])
        fl.write(x)
        fl.write("\n")

class is_loaded:
  def __init__(self, locator, driver):
    self.text = """<div class="d-flex justify-content-center"><div class="spinner-border text-light m-5" role="status"><span class="sr-only"></span></div></div>"""
    self.element = driver.find_element_by_id(locator) 

  def __call__(self, driver):
    if self.text != self.element.get_attribute("innerHTML"):
        return self.element
    else:
        return False


class scroll_load:
  def __init__(self, curr_length, driver):
    self.curr_length = curr_length
    self.element = driver.find_element_by_xpath("//*[@id='count']/span")

  def __call__(self, driver):
    length = finder(driver, 1)
    if length > self.curr_length or self.element.text:
      return length
    else:
      return False
