from django.db import models
import json
import steammarket as sm
from django.contrib.auth.models import User
from datetime import datetime, timezone, timedelta
import requests
# Create your models here.


class Investment(models.Model):

    name = models.CharField(max_length=255)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    portfolio = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    def current_value(self):
        current_price = 0
        if (itemPrice.objects.filter(name=self.name)).exists():
            item_price_object = itemPrice.objects.filter(name=self.name)[0]
            time_since = (
                datetime.now(timezone.utc) - item_price_object.last_refresh)
            
            if (time_since.total_seconds()) / 60 >= 10:
                print("Refreshing")
              
                item = sm.get_csgo_item(self.name, currency='GBP')
                current_price = (item["lowest_price"])[1:]
                item_price_object.last_price = current_price
                item_price_object.last_refresh = datetime.now(timezone.utc)
                item_price_object.save()
            else: #0.77 09.36
                
                current_price = item_price_object.last_price
        else:
            new_name = ""
            print(self.name)
            for i in range(0, len(self.name)):
              
                if self.name[i] == " ":
                    new_name += "%20"
                else:
                    new_name += self.name[i]
            print(new_name)
            item = (requests.get(("http://csgobackpack.net/api/GetItemPrice/?full=true&id=" + new_name + "&time=3&icon=1"))).json()  
            
            t = (len(str(len(item))))     
            item_data = (item[round((len(item) / t))]) #So it doesnt actually get the first day price because its highly infalted, so i wrote a calculation to instead of get the 1st day sale price, get like the 50th sale day where it is lowish. This is why the 1st day says a while after first actual day
            first_sp = item_data[1]
            x = item_data[0].split(" ")
            y = x[0] + " " + x[1]  + " " + x[2]
            input_date = datetime.strptime(y, "%b %d %Y")
            first_sd = input_date.strftime("%Y-%m-%d")


            item = sm.get_csgo_item(self.name, currency='GBP')
            current_price = (item["lowest_price"])[1:]
            item_price_object = itemPrice(
                name=self.name, last_refresh=datetime.now(timezone.utc), last_price=(current_price), first_sale_price = first_sp, first_sale_date =first_sd)
            item_price_object.save()

        cv = (float(current_price) * float(self.quantity))
        return cv

    def calculate_profit(self):

        profit = round(float(self.current_value() - float(self.purchase_price * self.quantity)), 2)
        return profit

    def is_profit(self):
        if (self.calculate_profit()) >= 0:
            return "Profit"
        else:
            return "Loss"


class UserValueHistory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    snapshot = models.DateField()
    value = models.DecimalField(decimal_places=1, max_digits=12)


class CurrentValue(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    # current value of inventory
    cvalue = models.DecimalField(decimal_places=1, max_digits=12)


class UserStats(models.Model):
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    # Total gain or loss for an account
    total_gain = models.DecimalField(decimal_places=1, max_digits=12)

    total_volume_sold = models.IntegerField()
    total_volume_sold_value = models.DecimalField(
        decimal_places=1, max_digits=12)
    total_volume_bought = models.IntegerField()
    total_volume_bought_value = models.DecimalField(
        decimal_places=1, max_digits=12)

    total_trades = models.IntegerField()

    average_profit_per_trade = models.DecimalField(
        decimal_places=1, max_digits=12)

    biggest_winner_name = models.CharField(max_length=255)
    biggest_winner = models.DecimalField(
        decimal_places=1, max_digits=12)

    biggest_loser_name = models.CharField(max_length=255)
    biggest_loser = models.DecimalField(
        decimal_places=1, max_digits=12)


class itemPrice(models.Model):
    name = models.CharField(max_length=255)
    last_refresh = models.DateTimeField()
    last_price = models.DecimalField(decimal_places=2, max_digits=10)
    first_sale_price = models.DecimalField(decimal_places=2, max_digits=10)
    first_sale_date = models.DateField()


    def days_since_start(self):
        
        formatted_date = datetime.today()
        formatted_date = formatted_date.date()
        date_difference = formatted_date - self.first_sale_date
        number_of_days = date_difference.days
        return(number_of_days)
        

    

    def __str__(self):
        return self.name

class Portfolio(models.Model):
    name = models.CharField(max_length=255) 
    owner = models.ForeignKey(User, on_delete=models.CASCADE)                               