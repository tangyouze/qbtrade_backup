from qbtrade import quote, Contract, util

from datetime import datetime


start_time = datetime(2016, 1, 1, tzinfo=util.gmtp8)
end_time = datetime(2016, 12, 1, tzinfo=util.gmtp8)
cons = [Contract.get_by_symbol('000001:exchange.cn.sze'),
Contract.get_by_symbol('002142:exchange.cn.sze'),
Contract.get_by_symbol('600000:exchange.cn.sse'),
Contract.get_by_symbol('600015:exchange.cn.sse'),
Contract.get_by_symbol('600016:exchange.cn.sse'),
Contract.get_by_symbol('600036:exchange.cn.sse'),
Contract.get_by_symbol('601009:exchange.cn.sse'),
Contract.get_by_symbol('601166:exchange.cn.sse'),
Contract.get_by_symbol('601169:exchange.cn.sse'),
Contract.get_by_symbol('601288:exchange.cn.sse'),
Contract.get_by_symbol('601328:exchange.cn.sse'),
Contract.get_by_symbol('601398:exchange.cn.sse'),
Contract.get_by_symbol('601818:exchange.cn.sse'),
Contract.get_by_symbol('601939:exchange.cn.sse'),
Contract.get_by_symbol('601988:exchange.cn.sse'),
Contract.get_by_symbol('601998:exchange.cn.sse')]
first_ticker = True
first_group = True
investment = 1000000
cur_tks = {}
pre_tks = {}
cash = investment
profit = 0
amount = {}
pre_average_price = 0
averge_price = 0

def get_average_price(tks):
    avg = 0
    for key, value in tks.items():
        avg += value
    return avg / len(tks)

def cb(tk):
    global first_ticker, first_group
    global cur_time
    global cur_tks, pre_tks
    global average_price, pre_average_price
    global cash, investment, profit
    global amount, cons
    if first_ticker:
        cur_time = tk.tm
        first_ticker = False
    if (tk.tm == cur_time): #still the same group of tickets
        cur_tks[tk.contract] = tk.price
    else:
        for contract, price in cur_tks.items():
            if (contract not in amount) and (price != 0):
                amount[contract] = int(investment/len(cons)/price)
                cash = cash - amount[contract] * price
        if first_group:  #this is the first group of tks
            average_price = get_average_price(cur_tks)
            first_group = False
        else:
            pre_average_price = average_price
            average_price = get_average_price(cur_tks)
            if pre_average_price != 0:
                average_diff = (average_price - pre_average_price) / pre_average_price
                if average_diff != 0:
                    tks_diff = {}
                    for contract, price in cur_tks.items():
                        if (contract in pre_tks) and (pre_tks[contract] != 0):
                            tks_diff[contract] = (price - pre_tks[contract]) / pre_tks[contract]
                    # print("============================================")
                    # print("cur_time = " + str(cur_time))
                    # print("pre_average_price = %10.10f"% pre_average_price)
                    # print("average_price = %10.10f"% average_price)
                    # print("average_diff = %10.10f"% average_diff)
                    # print("cur_tks = " + str(cur_tks))
                    # print("pre_tks = " + str(pre_tks))
                    # print("tks_diff = " + str(tks_diff))
                    for contract, price_diff in tks_diff.items():
                        trade_amount_percentage = (average_diff - price_diff)
                        if abs(trade_amount_percentage) > 0.1:
                            if (trade_amount_percentage < 0):
                                trade_amount_percentage = -0.1
                            else:
                                trade_amount_percentage = 0.1
                        trade_amount = int(trade_amount_percentage * amount[contract])
                        # print(str(contract) +
                        #       "  price_diff = " + str(price_diff) +
                        #       "  trade_amount_percentage = " + str(trade_amount_percentage) +
                        #       "  amount = " + str(amount[contract]) +
                        #       "  trade_amount = " + str(trade_amount))
                        if (amount[contract] - trade_amount >= 0):
                            cash = cash - trade_amount * cur_tks[contract]
                            amount[contract] -= trade_amount
                        else:
                            cash = cash - amount[contract] * cur_tks[contract]
                            amount[contract] = 0
                    # print("amount = " + str(amount))
                    # print("cash = %10.2f"% cash)
                    profit = cash
                    for contract, quantity in amount.items():
                        profit += quantity * cur_tks[contract]
                    print("profit = %10.2f"% (profit - investment))
        cur_time = tk.tm
        pre_tks = cur_tks.copy()
        cur_tks[tk.contract] = tk.price


cfg = {
    'start_time': start_time,
    'end_time': end_time
}
quote.subscribe_history_quote(cons, cb, cfg)
profit = cash
for contract, quantity in amount.items():
    profit += quantity * cur_tks[contract]
print("profit = %10.2f"% (profit - investment))