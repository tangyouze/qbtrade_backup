from qbtrade import quote, Contract, util, MockAccount

from datetime import datetime

start_time = datetime(2016, 1, 1, tzinfo=util.gmtp8)
end_time = datetime(2016, 12, 1, tzinfo=util.gmtp8)


def get_average_price(tks):
    avg = 0
    for key, value in tks.items():
        avg += value
    return avg / len(tks)


class BankArb:
    def __init__(self):
        self.cons = [Contract.get_by_symbol('000001:exchange.cn.sze'),
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
        self.first_ticker = True
        self.first_group = True
        self.investment = 1000000
        self.cur_tks = {}
        self.pre_tks = {}
        self.cash = self.investment
        self.profit = 0
        self.amount = {}
        self.pre_average_price = 0
        self.averge_price = 0

        self.account = MockAccount()
        for c in self.cons:
            # TODO TODO_PRICE need to be the last price of each contract, but we don't know the last price in init
            # need to refactor it somehow
            self.account.place_order(c, TODO_PRICE, 'b', 1000, None)

    def cb(self, tk):
        # global first_ticker, first_group
        # global cur_time
        # global cur_tks, pre_tks
        # global average_price, pre_average_price
        # global cash, investment, profit
        # global amount, cons
        global cash
        if self.first_ticker:
            cur_time = tk.tm
            first_ticker = False
        if (tk.tm == cur_time):  # still the same group of tickets
            self.cur_tks[tk.contract] = tk.price
        else:
            for contract, price in self.cur_tks.items():
                if (contract not in self.amount) and (price != 0):
                    self.amount[contract] = int(self.investment / len(self.cons) / price)
                    cash = cash - self.amount[contract] * price
            if self.first_group:  # this is the first group of tks
                average_price = get_average_price(self.cur_tks)
                first_group = False
            else:
                pre_average_price = self.average_price
                average_price = get_average_price(self.cur_tks)
                if pre_average_price != 0:
                    average_diff = (average_price - pre_average_price) / pre_average_price
                    if average_diff != 0:
                        tks_diff = {}
                        for contract, price in self.cur_tks.items():
                            if (contract in self.pre_tks) and (self.pre_tks[contract] != 0):
                                tks_diff[contract] = (price - self.pre_tks[contract]) / self.pre_tks[contract]
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
                                if trade_amount_percentage < 0:
                                    trade_amount_percentage = -0.1
                                else:
                                    trade_amount_percentage = 0.1
                            trade_amount = int(trade_amount_percentage * self.amount[contract])
                            # print(str(contract) +
                            #       "  price_diff = " + str(price_diff) +
                            #       "  trade_amount_percentage = " + str(trade_amount_percentage) +
                            #       "  amount = " + str(amount[contract]) +
                            #       "  trade_amount = " + str(trade_amount))
                            if self.amount[contract] - trade_amount >= 0:
                                cash = cash - trade_amount * self.cur_tks[contract]
                                self.amount[contract] -= trade_amount
                            else:
                                cash = cash - self.amount[contract] * self.cur_tks[contract]
                                self.amount[contract] = 0
                        # print("amount = " + str(amount))
                        # print("cash = %10.2f"% cash)
                        profit = cash
                        for contract, quantity in self.amount.items():
                            profit += quantity * self.cur_tks[contract]
                        print("profit = %10.2f" % (profit - self.investment))
            cur_time = tk.tm
            pre_tks = self.cur_tks.copy()
            self.cur_tks[tk.contract] = tk.price


cfg = {
    'start_time': start_time,
    'end_time': end_time
}
strategy = BankArb()
quote.subscribe_history_quote(cons, strategy.cb, cfg)
profit = cash
for contract, quantity in amount.items():
    profit += quantity * cur_tks[contract]
print("profit = %10.2f" % (profit - investment))
