from django.shortcuts import render
import requests
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from .models import *
from django.contrib.auth.models import User
from decimal import Decimal
from currency_converter import CurrencyConverter
import re
import math
import time
#################### index#######################################


def index(request):
    return render(request, 'main/index.html', {'title': 'index'})


################ login forms###################################################


def Login(request):
    if request.method == 'POST':

        # AuthenticationForm_can_also_be_used__

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            form = login(request, user)
            messages.success(request, f' welcome {username} !!')
            return redirect('index')
        else:
            messages.info(request, f'account done not exit plz sign in')
    form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form, 'title': 'log in'})


def Overview(request):
    total = 0
    value = 0
    labelPieChart1 = []  # PieChart1 is the piechart with overview value of all items
    datalPieChart1 = []
    labelLineChart1 = []  # LineChart1 is the linechart for historical inventory value
    dataLineChart1 = []
    Investment_array = []
    other_items_total = 0
    items = Investment.objects.filter(owner_id=request.user.id)


    for item in items:
        Investment_array.append((item.name, item.current_value()))
        

        total += item.calculate_profit()
        value += item.current_value()
        
    
    sorted_investments = sorted(Investment_array, key=lambda x: x[1], reverse=True)
    
    if len(items) > 5:
        top_5_items = sorted_investments[:5]
        other_items = sorted_investments[5:]
        print(top_5_items)
        print(" ")
        for i in range(0, len(other_items)):
            other_items_total += other_items[i][1]
        
        for i in range(0, len(top_5_items)):
            labelPieChart1.append(top_5_items[i][0])
            datalPieChart1.append(top_5_items[i][1])
        
        labelPieChart1.append("Other")
        datalPieChart1.append(other_items_total)
    else:
        for i in range(0, len(sorted_investments)):
            labelPieChart1.append(sorted_investments[i][0])
            datalPieChart1.append(sorted_investments[i][1])

    if (CurrentValue.objects.filter(name_id=request.user.id)).exists():
        current_v = (CurrentValue.objects.filter(name_id=request.user.id))[0]
        current_v.cvalue = value
        current_v.save()
        valueHistory = UserValueHistory.objects.filter(
            owner_id=request.user.id)
        for i in valueHistory:
            test = str(i.snapshot)
            test2 = str(i.value)
           
            labelLineChart1.append(test)
            dataLineChart1.append(test2)

    else:
        current_v = CurrentValue.objects.create(
            name=request.user, cvalue=value)

    value = round(value, 2)
    return render(request, "main/overview.html", {"items": items, "total": round(total, 2), "value": value, "labelPieChart1": labelPieChart1, "datalPieChart1": datalPieChart1, "labelLineChart1": labelLineChart1, "dataLineChart1": dataLineChart1})


def Market(request):

    return render(request, "main/market.html")


def profile(request):
    u_id = request.user.id
    user_object = (User.objects.get(id=u_id))
    if (user_object.userstats_set.filter(name=request.user.id)).exists():
        stats = (user_object.userstats_set.filter(
            name=request.user.id))[0]
    else:
        stats = UserStats.objects.create(name=request.user, total_gain=0, total_volume_sold=0, total_volume_sold_value=0, total_volume_bought=0,
                                         total_volume_bought_value=0, total_trades=0, average_profit_per_trade=0, biggest_winner_name=0, biggest_winner=0, biggest_loser_name=0, biggest_loser=0)

    return render(request, "main/profile.html", {"stats": stats})
########### register here #####################################


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            messages.success(
                request, f'Your account has been created ! You are now able to log in')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form, 'title': 'register here'})


def purchase(request):
    form = BuyForm(request.POST)
    submitted = False
    if request.method == "POST":
        form = BuyForm(request.POST)
        if form.is_valid():

            form_name = form["name"].value()

            u_id = request.user.id
            user_object = (User.objects.get(id=u_id))

            if user_object.investment_set.filter(name=form_name).exists():
                stats = (user_object.userstats_set.filter(
                    name=request.user.id))[0]
                item = (user_object.investment_set.filter(name=form_name))[0]
                old_quantity = item.quantity
                old_pp = item.purchase_price
                form_quantity = int(form["quantity"].value())
                form_pp = float(form["purchase_price"].value())

                new_quantity = old_quantity + form_quantity

                new_pp = (float(form_quantity * form_pp) +
                          float(old_quantity * old_pp)) / new_quantity

                item.quantity = new_quantity
                item.purchase_price = new_pp

                stats.total_volume_bought += form_quantity
                stats.total_volume_bought_value += Decimal.from_float(
                    form_quantity * form_pp)
                stats.total_trades += 1
                stats.save()
                item.save()
                submitted = True

            else:
                obj = form.save(commit=False)
                obj.owner = User.objects.get(id=request.user.id)
                obj.save()
                submitted = True

        else:
            form = BuyForm
            if "submitted" in request.GET:
                submitted = True
    return render(request, "main/purchase.html", {"form": form, "submitted": submitted})


def sell(request):
    form = SellForm(request.POST)
    submitted = False
    if request.method == "POST":
        form = SellForm(request.POST)
        if form.is_valid():

            form_name = form["name"].value()

            u_id = request.user.id
            user_object = (User.objects.get(id=u_id))

            if user_object.investment_set.filter(name=form_name).exists():

                obj = form.save(commit=False)
                obj.owner = User.objects.get(id=request.user.id)
                stats = (user_object.userstats_set.filter(
                    name=request.user.id))[0]
                quantity = obj.quantity
                sell_price = form["sell_price"].value()
                item = (user_object.investment_set.filter(name=form_name))[0]
                if item.quantity < quantity:
                    print("Attempt to sell more than owned")
                elif item.quantity == quantity:
                    print("Exact sell delete")
                    item.delete()
                else:
                    item.quantity = item.quantity - quantity

                    stats.total_volume_sold += quantity
                    stats.total_volume_sold_value += Decimal.from_float(
                        float(quantity) * float(sell_price))
                    stats.total_trades += 1

                    # For difficult calculations regarding stats of a user

                    profit = Decimal.from_float(
                        float(sell_price) - float(item.purchase_price))
                    stats.total_gain += profit
                 
                    if float(sell_price) > float(stats.biggest_winner):
                        stats.biggest_winner = round(float(sell_price))
                        stats.biggest_winner_name = item.name
                    if profit < 0:
                        if float(profit) < stats.biggest_loser:
                          
                            stats.biggest_loser = round(float(profit))
                            stats.biggest_loser_name = item.name

                    stats.average_profit_per_trade = float(stats.total_gain) / float(
                        stats.total_volume_sold)

                    stats.save()
                    item.save()

                submitted = True

            else:

                # submitted = True
                print("item does not exist")

        else:
            form = SellForm
            if "submitted" in request.GET:
                submitted = True
    return render(request, "main/sell.html", {"form": form, "submitted": submitted})


def analysis(request):
    form = itemAnalysisForm(request.POST)
    submitted = False
    item = 0
    total_change = 0
    labelLineChart1 = []  # LineChart1 is the linechart for quantity sold last 15 days
    dataLineChart1 = []
    labelLineChart2 = []  # LineChart2 is the linechart for sell orders last 15 days
    dataLineChart2 = []
    labelLineChart3 = []  # LineChart3 is the linechart for buy  orders last 15 days
    dataLineChart3 = []
    item_m = 0
    sd_medianprice = 0
    standard_deviation = 0
    sharpe_ratio = 0
    if request.method == "POST":
        form = itemAnalysisForm(request.POST)
        if form.is_valid():

            item_name = form["name"].value()
            convert = CurrencyConverter()
            # This is for all the analysis

            item = (requests.get(
                ("https://api.steamapis.com/market/item/730/" + item_name + "?api_key=aA0zFsVb3Lv1EQGtLOVoHB1IYUs"))).json()
            
            #This is for median price and change/supply table

            item_m = item["median_avg_prices_15days"]
            for i in range(0, 15):
                itemvalue = round(convert.convert(
                    (item_m[i][1]), "USD", "GBP"), 2)
                item_m[i][1] = itemvalue
                sd_medianprice += itemvalue
                labelLineChart1.append(item_m[i][0])
                dataLineChart1.append(item_m[i][2])
                if i == 0:
                    p_change = " "
                    item_m[i].append(False)
                    item_m[i].append(True)
                else:
                    
                    if item_m[i][1] == item_m[i-1][1]:
                        p_change = "0 % Change"
                        item_m[i].append(False)
                        item_m[i].append(True)
                    elif item_m[i][1] < item_m[i-1][1]:
                        p_change = "- " + str(round(((
                            ((item_m[i-1][1]) - (item_m[i][1])) / item_m[i-1][1]) * 100), 2)) + "%"
                        item_m[i].append(False)
                        item_m[i].append(False)
                    else:
                        p_change = "+ " + str(round(((
                            ((item_m[i][1]) - (item_m[i-1][1])) / item_m[i-1][1]) * 100), 2)) + "%"
                        item_m[i].append(True)
                        item_m[i].append(False)
                item_m[i].append(p_change)

            if item_m[0][1] == item_m[14][1]:
                total_change = "0 % Change"
            elif item_m[14][1] < item_m[0][1]:
                total_change = "- " + str(round(((
                    ((item_m[0][1]) - (item_m[14][1])) / item_m[0-1][1]) * 100), 2)) + "%"
            else:
                total_change = "+ " + str(round(((
                    ((item_m[14][1]) - (item_m[0][1])) / item_m[0-1][1]) * 100), 2)) + "%"
           
            

            #This is for the buy order sell order section
            historgrams = item["histogram"]
            sell_order_array = historgrams["sell_order_array"]
            buy_order_array = historgrams["buy_order_array"]
            
            sell_array_p = []
            sell_array_q = []
            buy_array_p = []
            buy_array_q = []
            #For sell orders only as buy orders broken, api call only returning 1st day 
            for i in range(1, len(historgrams["sell_order_graph"])): #If i use commas in the thousands, it messes up when html reading it so need to convert it to dot
                sell_array_q.append(((re.split("sell orders at | or lower", (historgrams["sell_order_graph"][i][2])))[0]).replace(",", "."))
                sell_array_p.append((((re.split("sell orders at | or lower", (historgrams["sell_order_graph"][i][2])))[1])[1:]).replace(",", "."))

            for i in range(1, len(historgrams["buy_order_graph"])): #If i use commas in the thousands, it messes up when html reading it so need to convert it to dot
                buy_array_q.append(((re.split("buy orders at | or lower", (historgrams["buy_order_graph"][i][2])))[0]).replace(",", "."))
                buy_array_p.append((((re.split("buy orders at | or lower", (historgrams["buy_order_graph"][i][2])))[1])[1:]).replace(",", "."))
            dataLineChart2 = sell_array_p
            labelLineChart2 = sell_array_q
            dataLineChart3 = buy_array_p
            labelLineChart3 = buy_array_q
            

            #Risk analysis calculations

            #Standard deviation

            sd_mean_medianprice = sd_medianprice / 15
        
            squared_sum = 0
            for i in range(0, 15):
            
                price_deviation = item_m[i][1] - sd_mean_medianprice
                squared = price_deviation * price_deviation
                squared_sum += squared

            
            variance = squared_sum / 14
            standard_deviation = round((math.sqrt(variance)), 2) #means score deviates from the mean by SD points ona verage
            name = form["name"].value()
            #Sharpe Ratio
            try:
                item = (itemPrice.objects.filter(name=name))[0]

            except:
                new_name = ""
                for i in range(0, len(name)):
                    
                    if name[i] == " ":
                        new_name += "%20"
                    else:
                        new_name += name[i]
            
                item = (requests.get(("http://csgobackpack.net/api/GetItemPrice/?full=true&id=" + new_name + "&time=3&icon=1"))).json()   
                t = (len(str(len(item))))     
                item_data = (item[round((len(item) / t))]) #So it doesnt actually get the first day price because its highly infalted, so i wrote a calculation to instead of get the 1st day sale price, get like the 50th sale day where it is lowish. This is why the 1st day says a while after first actual day
                first_sp = item_data[1]
                x = item_data[0].split(" ")
                y = x[0] + " " + x[1]  + " " + x[2]
                input_date = datetime.strptime(y, "%b %d %Y")
                first_sd = input_date.strftime("%Y-%m-%d")


                item = sm.get_csgo_item(name, currency='GBP')
                current_price = (item["lowest_price"])[1:]
                item_price_object = itemPrice(
                    name=name, last_refresh=datetime.now(timezone.utc), last_price=(current_price), first_sale_price = first_sp, first_sale_date =first_sd)
                item_price_object.save()
                time.sleep(2)

            days_since_start = item.days_since_start()
            total_percent_return = ((item.last_price - item.first_sale_price) / item.first_sale_price) * 100
            avg_daily_return = round((days_since_start / total_percent_return), 2)
         
            submitted = True
            sharpe_ratio = (float(avg_daily_return * 30) / ((standard_deviation / sd_mean_medianprice) * 100))
        else:
            form = itemAnalysisForm
            if "submitted" in request.GET:

                submitted = True

    return render(request, "main/analysis.html", {"form": form, "submitted": submitted, "item": item_m, "total_change": total_change, "labelLineChart1": labelLineChart1, "dataLineChart1": dataLineChart1, "labelLineChart2": labelLineChart2, "dataLineChart2": dataLineChart2, "labelLineChart3": labelLineChart3, "dataLineChart3": dataLineChart3, "standard_deviation": standard_deviation, "sharpe_ratio": sharpe_ratio})

def portfolio(request):
    items = Investment.objects.filter(owner_id=request.user.id)
    portfolios = Portfolio.objects.filter(owner_id=request.user.id)
    p_array = []
    form = SellForm(request.POST)
    form_buy = BuyForm(request.POST)
    form_portfolio_create = CreatePortfolioForm(request.POST)
    form_portfolio_delete = CreatePortfolioForm(request.POST)
    submitted = False
    i_array = []
   
    for y in range(0, len(portfolios)):
        for x in range(0, len(items)):
        
            if str(items[x].portfolio) == str(portfolios[y].name):
                print(str(items[x].portfolio) + "     " + str(portfolios[y].name))
                i_array.append({"name": items[x].name, "quantity": items[x].quantity, "purchase_price": str(items[x].purchase_price)})
    

        p_array.append({"name": (portfolios[y].name), "investments": i_array})
        i_array = []
    


    print(p_array)

    if request.method == "POST":
        form = SellForm(request.POST)
        if form.is_valid():
            if "sell" in request.POST:
                form_name = form["name"].value()

                u_id = request.user.id
                user_object = (User.objects.get(id=u_id))

                if user_object.investment_set.filter(name=form_name).exists():

                    obj = form.save(commit=False)
                    obj.owner = User.objects.get(id=request.user.id)
                    stats = (user_object.userstats_set.filter(
                        name=request.user.id))[0]
                    quantity = obj.quantity
                    sell_price = form["sell_price"].value()
                    item = (user_object.investment_set.filter(name=form_name))[0]
                    if item.quantity < quantity:
                        print("Attempt to sell more than owned")
                    elif item.quantity == quantity:
                        print("Exact sell delete")
                        item.delete()
                    else:
                        item.quantity = item.quantity - quantity

                        stats.total_volume_sold += quantity
                        stats.total_volume_sold_value += Decimal.from_float(
                            float(quantity) * float(sell_price))
                        stats.total_trades += 1

                        # For difficult calculations regarding stats of a user

                        profit = Decimal.from_float(
                            float(sell_price) - float(item.purchase_price))
                        stats.total_gain += profit
                    
                        if float(sell_price) > float(stats.biggest_winner):
                            stats.biggest_winner = round(float(sell_price))
                            stats.biggest_winner_name = item.name
                        if profit < 0:
                            if float(profit) < stats.biggest_loser:
                            
                                stats.biggest_loser = round(float(profit))
                                stats.biggest_loser_name = item.name

                        stats.average_profit_per_trade = float(stats.total_gain) / float(
                            stats.total_volume_sold)

                        stats.save()
                        item.save()

                    submitted = True
                    return redirect(request.META.get('HTTP_REFERER', 'main/portfolio.html'))
                else:

                    print("item does not exist")
            else:
                print("2222")
                if form_buy.is_valid():
                    print("wdwdw")
                    

        elif form_buy.is_valid():
            form_name = form_buy["name"].value()
            print("wdwdw")
            u_id = request.user.id
            user_object = (User.objects.get(id=u_id))
           
            if user_object.investment_set.filter(name=form_name).exists():
                stats = (user_object.userstats_set.filter(
                    name=request.user.id))[0]
                item = (user_object.investment_set.filter(name=form_name))[0]
                old_quantity = item.quantity
                old_pp = item.purchase_price
                form_quantity = int(form_buy["quantity"].value())
                form_pp = float(form_buy["purchase_price"].value())

                new_quantity = old_quantity + form_quantity

                new_pp = (float(form_quantity * form_pp) +
                    float(old_quantity * old_pp)) / new_quantity

                item.quantity = new_quantity
                item.purchase_price = new_pp

                stats.total_volume_bought += form_quantity
                stats.total_volume_bought_value += Decimal.from_float(
                    form_quantity * form_pp)
                stats.total_trades += 1
                stats.save()
                item.save()
                submitted = True

            else:
                obj = form_buy.save(commit=False)
                obj.owner = User.objects.get(id=request.user.id)
                obj.save()
                submitted = True
                return redirect(request.META.get('HTTP_REFERER', 'main/portfolio.html'))
       
        elif form_portfolio_create.is_valid() or form_portfolio_delete.is_valid():
            if "delete" in request.POST:
                print("deleting")
                obj = form_portfolio_create.save(commit=False)
                
                Portfolio.objects.get(name=obj.name, owner=(User.objects.get(id=request.user.id))).delete()


            else:
                print("not deleting")
                obj = form_portfolio_create.save(commit=False)
                obj.owner = User.objects.get(id=request.user.id)
                obj.save()
                submitted = True
            return redirect(request.META.get('HTTP_REFERER', 'main/portfolio.html'))
       
        

        else:
            form = SellForm
            form_buy = BuyForm
            form_portfolio_create = CreatePortfolioForm
            form_portfolio_delete = CreatePortfolioForm
            if "submitted" in request.GET:
                submitted = True
                


    return render(request, "main/portfolio.html", {"items": items, "form": form, "submitted": submitted, "form_buy": form_buy, "form_portfolio_create" : form_portfolio_create, "portfolios" : portfolios, "form_portfolio_delete":form_portfolio_delete, "p_array":p_array})