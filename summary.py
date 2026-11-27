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


def months(records):
    """収支のある月（"2026-11" の形）を、新しい月から返す"""
    return sorted({r["日付"][:7] for r in records}, reverse=True)


def in_month(records, month):
    """"2026-11" の形の月の行だけを返す。並びは変えない"""
    return [r for r in records if r["日付"][:7] == month]
