def summarize(records):
    """収入・支出・残高の合計を返す。金額はどれも正の数で、区分で足す先を分ける"""
    income = 0
    expense = 0
    for r in records:
        if r["区分"] == "収入":
            income += r["金額"]
        else:
            expense += r["金額"]
    return income, expense, income - expense
