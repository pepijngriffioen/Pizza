# Domino's Promocode Tester

Domino's promocode tester came into existence when I used the website: pizza.insane.software for some promocodes for a large order of pizzas. I came to the idea to test every code and tried to combine them to get the lowest total price for  my pizzas. This was a very repetitive process and when I saw a video of someone building a webscraper for Tinder I thought I could do that too for the pizza codes.

That is where it started. The first idea was to bruteforce all the codes and combine every of them. As it turned out not all codes are able to be combined and combination will not favour the best price, as you will have to choose between discounts. For the best total price you will need to get the largest percentage of discount. For this there are several dutch words selected to find the highest codes.

## How it works

The bot works as follows:
1. A Chrome instance will be started.
2. Get codes from pizza.insane.software .
3. Login on the Domino's website using an address near your store.
4. Add pizzas that are in the attached pizza file.
5. Get the most likely discounts based on the following words: 'Stapel', 'alle', 'gehele'.
6. Try each of the codes in the most likely dataframe. Keep track of the code in a dataframe.
7. Show a dataframe with codes corresponding to the lowest total prices.
8. Show the codes that have the word 'gratis' in them.

## Installation
- Download Chromedriver from http://chromedriver.chromium.org/ move to /usr/local/bin (mac os/linux) for windows move and locate and put in. note: Change the webdriver in the init function according to your OS.
- ```bash
pip install selenium
pip install pandas
```
- Create a secrets.py file with variables:
```python
zipCode = 'your_zipcode'
sNumber = 'your_streetnumber'
chromePath = r"C:\path\to\Chrome"
```
- Setup your pizzas.txt with the pizzas you want to order. It will be read line by line.
```
Pizza veggi
pizza chicken supreme
pizza chicken kebab
```

## Usage
You can run the python script with
```bash
python dominos.py
```

As it is using a automation software it sometimes might fail, so you can run it again. In interactive python (-i) mode you can also re run the commands.