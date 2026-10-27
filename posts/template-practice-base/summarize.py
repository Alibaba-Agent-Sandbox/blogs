import csv,json
from decimal import Decimal
from pathlib import Path
p=Path(__file__).parent
rows=list(csv.DictReader((p/"expenses.csv").open()))
value={"count":len(rows),"total":format(sum(Decimal(r["amount"]) for r in rows),".2f")}
(p/"summary.json").write_text(json.dumps(value,sort_keys=True)+"\n")
print(json.dumps(value,sort_keys=True))
