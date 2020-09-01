from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secrets import zipCode, sNumber, chromePath
import pandas as pd

class DominoBot():
    def __init__(self, zipCode, sNumber,chromePath):
        # if using mac or linux webdriver.Chrome(executable_path) should be webdriver.Chrome()
        self.driver = webdriver.Chrome(executable_path=chromePath)
        self.df = pd.DataFrame()
        self.dfLikely = pd.DataFrame()
        self.driver.maximize_window()
        self.zipCode = zipCode
        self.sNumber = sNumber

    def login(self):
        #Setup address info and got to order screen
        zipcode = self.zipCode
        sNumber = self.sNumber
        self.driver.get('https://bestellen.dominos.nl/estore/nl/CustomerDetails/Delivery')
        order_now_btn = self.driver.find_element_by_xpath('//*[@id="ordertimebutton"]/label[1]')
        order_now_btn.click()
        pc_input = self.driver.find_element_by_xpath('//*[@id="customer-postcode"]')
        pc_input.send_keys(zipcode)
        h_number = self.driver.find_element_by_xpath('//*[@id="customer-street-no"]')
        ActionChains(self.driver).click(h_number).key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
        h_number.send_keys(sNumber)
        next_btn = self.driver.find_element_by_xpath('//*[@id="order-time-button"]')
        self.closeCookie()
        next_btn.click()
        
        addr_btn = self.driver.find_element_by_xpath('//*[@id="search-items"]/li/a')
        addr_btn.click()

    def closeCookie(self):
        try:
            cookiePopup = self.driver.find_element_by_xpath('//*[@id="customerdetails-page"]/div[1]/div[1]/div/button')
            cookiePopup.click()
        except:
            print("Cookie is already closed.")
    
    def closePromo(self):
        try:
            promoPopup = self.driver.find_element_by_xpath('/html/body/div[10]/div[3]/div[2]/div/button')
            promoPopup.click()
        except:
            print("There was no promo popup, so not closed.")           
    
    def addCoupon(self, couponCode, actionChain):
        #Add move to top of page (otherwise code can not be added.)
        ActionChains(self.driver).send_keys(Keys.HOME).perform()
        addCoupon = False
        try:
            coupon_input = self.driver.find_element_by_xpath('//*[@id="voucher_code"]')
        except:
            addCoupon = True
            print("Add Coupon not found")
        if (addCoupon == False):
            actionChain.click(on_element=coupon_input)
            actionChain.send_keys(couponCode)
            coupon_btn = self.driver.find_element_by_xpath('//*[@id="apply_voucher"]')
            actionChain.click(coupon_btn)
    
    def removeCoupon(self, actionChain):
        ActionChains(self.driver).send_keys(Keys.HOME).perform()
        class_name = "btn.remove-voucher"
        pizzaError = False
        try:
            discount_rmv_btn = self.driver.find_element_by_class_name(class_name)
        except:
            pizzaError = True
            print("Rmv coupon not found")
        if (pizzaError == False):
            actionChain.move_to_element(discount_rmv_btn)
            actionChain.click(discount_rmv_btn)


    def getTotalPrice(self):
        return self.driver.find_element_by_xpath('//*[@id="spnFormattedAmount"]').text

    def getDiscount(self):
        return self.driver.find_element_by_xpath('//*[@id="basket_rows"]/div[4]/span[2]').text
    
    def getPizzaCodes(self):
        self.driver.get('https://pizza.insane.software/')
        self.df = pd.read_html(self.driver.page_source, converters={'Code' : str})[0]
    
    def getMostLikelyCodes(self):
        #These codes are based on some words that are most likely giving the highest discount in the Netherlands
        arr = ['Stapel', 'alle', 'gehele']
        self.dfLikely = pd.DataFrame({'Code':'', 'Korting:':''}, index=[])
        
        if self.df.empty:
            self.getCodes()
        
        for word in arr:
            self.dfLikely = self.dfLikely.append(self.df[self.df['Korting:'].str.contains(word)])
    
    def getCodes(self):
        self.getPizzaCodes()
        self.getMostLikelyCodes()
    
    def getPizzaAbbr(self, name):
        name = name.title()
        name = name.replace("Bbq", "BBQ")
        name = name.replace("BBq", "BBQ")
        xpath_name = "//*[text()='" + name + "']"
        try:
            pizza_element = self.driver.find_element_by_xpath(xpath_name)
            attributes = pizza_element.get_attribute('id').split('-')
            return attributes[-2] + "-" + attributes[-1]
        except:
            return "Pizza not found"
    
    def addPizzaBasket(self, actionChain, nameAbbr):
        pizza_id = "product-menu-pizza-" + nameAbbr
        xpath_name =  "//*[@id='" + pizza_id + "']/div/div/form/div[3]/div/div/button"
        pizzaError = False
        try:
            pizza_add_btn = self.driver.find_element_by_xpath(xpath_name)
            print("Added to chain " + nameAbbr)
        except:
            pizzaError = True
            print("Not Added " + nameAbbr)
        if (pizzaError == False):
            actionChain.move_to_element_with_offset(pizza_add_btn,0,-140)
            actionChain.click(pizza_add_btn)

    def addPizzas(self, fileTxt):
        f = open(fileTxt, "r")
        lines = f.readlines()
        f.close()
        actions = ActionChains(self.driver)

        try:
            #Remove annoying footer for adding pizzas
            self.driver.execute_script("document.getElementsByClassName('fixed-footer')[0].style.visibility='hidden';")
        except:
            pass

        self.closePromo()
        
        numberPizzas = 0
        for x in lines:
            pizzaAbbr = self.getPizzaAbbr(x.strip())
            print("Pizza abb: " + pizzaAbbr)
            numberPizzas += 1
            self.addPizzaBasket(actions, pizzaAbbr)
        actions.perform()
        print("NumbPizzas: " + str(numberPizzas))
    
    def getLikelyDiscounts(self):
        self.dfLikely['TotalPrice'] = float(0.0)
        price = self.getTotalPrice()
        stdPrice = float(price[2:].replace(',','.'))
        for index, row in self.dfLikely.iterrows():
            actions = ActionChains(self.driver)
            print("Code: " +  str(row['Code']))
            self.addCoupon(row['Code'], actions)
            actions.pause(1)
            actions.perform()
            try:
                popup_coupon = self.driver.find_element_by_xpath('//*[@id="validation_apply_voucher"]')
                actions.reset_actions()
                actions.click(popup_coupon)
                actions.pause(1)
                actions.perform()
            except:
                pass

            try:
                popup_error = self.driver.find_element_by_xpath('//*[@id="validation_close_button"]')
                actions.reset_actions()
                actions.click(popup_error)
                actions.pause(1)
                actions.perform()
                self.dfLikely.loc[index, 'TotalPrice'] = stdPrice
            except:
                price = self.getTotalPrice()
                try:
                    totalPrice = float(price[2:].replace(',','.'))
                except:
                    totalPrice = stdPrice
                self.dfLikely.loc[index, 'TotalPrice'] = totalPrice
                #row['TotalPrice'] = totalPrice
                actions = ActionChains(self.driver)
                #Remove coupon werkt nog niet goed! even controleren
                self.removeCoupon(actions)
                actions.pause(1)
                actions.perform()
        print("finished checking discounts.")
        lowest = self.dfLikely['TotalPrice'].min()
        print("The best price you can get is: " + str(lowest))
        print("This prices comes with the following codes: ")
        print(self.dfLikely.loc[self.dfLikely['TotalPrice'] == lowest])

    def getFreeCodes(self):
        dfFree = self.df[self.df['Korting:'].str.contains("Gratis|gratis")]
        print("De following codes give some free stuff, so check it out:")
        print(dfFree)
        print("Still, most of the time if you use a free thing, you will be paying for it, as the pizza will not be added to the discount rate.")

bot = DominoBot(zipCode,sNumber, chromePath)
bot.getCodes()
bot.login()
#bot.addPizzas("pizzas.txt")
#bot.getLikelyDiscounts()
#bot.getFreeCodes()