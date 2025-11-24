import csv


class ValidationError(Exception):
    """Custom exception for invalid inputs."""
    pass


# ---------------------------------------------------------
# RISK MODELS
# ---------------------------------------------------------
class RiskModel:
    def calculate(self, calculator):
        raise NotImplementedError("Subclasses must implement this method.")


class FixedPercentRiskModel(RiskModel):
    def calculate(self, calculator):
        return (calculator.portfolio_value * calculator.risk_percent) / 100


class ATRRiskModel(RiskModel):
    def __init__(self, atr, multiplier=2):
        self.atr = atr
        self.multiplier = multiplier

    def calculate(self, calculator):
        return self.atr * self.multiplier


# ---------------------------------------------------------
# RISK CALCULATOR ENGINE
# ---------------------------------------------------------
class RiskCalculator:
    def __init__(self, entry, stop_loss, portfolio_value, risk_percent, risk_model):
        self.entry = float(entry)
        self.stop_loss = float(stop_loss)
        self.portfolio_value = float(portfolio_value)
        self.risk_percent = float(risk_percent)
        self.risk_model = risk_model

        self.validate()

    def validate(self):
        if self.entry <= 0:
            raise ValidationError("Entry must be positive.")
        if self.stop_loss <= 0:
            raise ValidationError("Stop-loss must be positive.")
        if self.stop_loss >= self.entry:
            raise ValidationError("Stop-loss must be LOWER than entry.")
        if self.portfolio_value <= 0:
            raise ValidationError("Portfolio value must be positive.")
        if not (0 < self.risk_percent <= 100):
            raise ValidationError("Risk% must be between 0–100.")

    def risk_per_share(self):
        return round(self.entry - self.stop_loss, 2)

    def allowed_risk_amount(self):
        return round(self.risk_model.calculate(self), 2)

    def suggested_position_size(self):
        rps = self.risk_per_share()
        if rps <= 0:
            return 0
        return int(self.allowed_risk_amount() // rps)

    def total_position_risk(self, position_size):
        return round(position_size * self.risk_per_share(), 2)

    def portfolio_risk_percent(self, position_size):
        total_risk = self.total_position_risk(position_size)
        return round((total_risk / self.portfolio_value) * 100, 2)

    def compute(self):
        pos = self.suggested_position_size()
        return {
            "Entry Price": self.entry,
            "Stop Loss": self.stop_loss,
            "Risk per Share": self.risk_per_share(),
            "Allowed Risk Amount": self.allowed_risk_amount(),
            "Suggested Position Size": pos,
            "Total Position Risk": self.total_position_risk(pos),
            "Portfolio Risk %": self.portfolio_risk_percent(pos),
        }

    def print_report(self):
        data = self.compute()
        print("\n========== RISK REPORT ==========")
        for k, v in data.items():
            print(f"{k:25}: {v}")
        print("=================================\n")


# ---------------------------------------------------------
# MODE 1 → MANUAL (USER INPUT)
# ---------------------------------------------------------
def manual_mode():
    print("\n=== MANUAL MODE SELECTED ===")
    print("Enter values yourself.\n")

    try:
        entry = float(input("Entry Price: "))
        stop_loss = float(input("Stop Loss: "))
        portfolio = float(input("Portfolio Value: "))
        risk_percent = float(input("Risk % (ex: 1): "))

        print("\nChoose Risk Model:")
        print("1. Fixed % Model")
        print("2. ATR Model")

        model_choice = input("Enter choice (1/2): ")

        if model_choice == "1":
            model = FixedPercentRiskModel()

        elif model_choice == "2":
            atr = float(input("Enter ATR value: "))
            multiplier = float(input("Enter ATR multiplier (default 2): "))
            model = ATRRiskModel(atr=atr, multiplier=multiplier)

        else:
            print("Invalid choice. Using Fixed % model.")
            model = FixedPercentRiskModel()

        calc = RiskCalculator(entry, stop_loss, portfolio, risk_percent, model)
        calc.print_report()

    except Exception as e:
        print("Error:", e)


# ---------------------------------------------------------
# MODE 2 → AUTOMATIC (HARDCODED)
# ---------------------------------------------------------
def automatic_mode():
    print("\n=== AUTOMATIC MODE SELECTED ===")
    print("Using built-in default values...\n")

    try:
        calc = RiskCalculator(
            entry=150,
            stop_loss=145,
            portfolio_value=50000,
            risk_percent=1,
            risk_model=FixedPercentRiskModel()
        )

        calc.print_report()

    except Exception as e:
        print("Error:", e)


# ---------------------------------------------------------
# MAIN MENU
# ---------------------------------------------------------
if __name__ == "__main__":
    print("========== STOCK RISK CALCULATOR ==========")
    print("Select Mode:")
    print("1. Manual Mode (You enter values)")
    print("2. Automatic Mode (Program uses defaults)")

    choice = input("Enter choice (1/2): ")

    if choice == "1":
        manual_mode()
    elif choice == "2":
        automatic_mode()
    else:
        print("Invalid selection. Exiting.")
