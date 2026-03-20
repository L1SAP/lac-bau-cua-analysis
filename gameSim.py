"""Vietnamese Lunar New Year game called Lac Bau Cua.
Simulate rounds being played, store and track results, and export data to a CSV for analysis.
"""
import random
import os
import csv


logo = r""" /$$                                 /$$
| $$                                | $$
| $$        /$$$$$$   /$$$$$$$      | $$$$$$$   /$$$$$$  /$$   /$$        /$$$$$$$ /$$   /$$  /$$$$$$
| $$       |____  $$ /$$_____/      | $$__  $$ |____  $$| $$  | $$       /$$_____/| $$  | $$ |____  $$
| $$        /$$$$$$$| $$            | $$  \ $$  /$$$$$$$| $$  | $$      | $$      | $$  | $$  /$$$$$$$
| $$       /$$__  $$| $$            | $$  | $$ /$$__  $$| $$  | $$      | $$      | $$  | $$ /$$__  $$
| $$$$$$$$|  $$$$$$$|  $$$$$$$      | $$$$$$$/|  $$$$$$$|  $$$$$$/      |  $$$$$$$|  $$$$$$/|  $$$$$$$
|________/ \_______/ \_______/      |_______/  \_______/ \______/        \_______/ \______/  \_______/
"""


symbols = [
    ["DEER", "GOURD", "ROOSTER"],
    ["FISH", "CRAB", "SHRIMP"]
]


valid_choice = {"DEER", "GOURD", "ROOSTER", "FISH", "CRAB", "SHRIMP"}


def instructions():
    print("\nA traditional Vietnamese betting game\n")
    print("Three six-sided dice are rolled each round. Each die contains one of six symbols:")
    print("Gourd (Bầu), Crab (Cua), Shrimp (Tôm), Fish (Cá), Rooster (Gà), Deer (Nai)\n")
    print("These symbols are represented on a 2 x 3 game board:")
    gameboard()
    print("\nPlace bets on one or more symbols. Winnings depend on how many dice match each symbol you bet on.")
    print("""
    Payouts:
    One Match: bet returns +1x profit
    Two Matches: bet returns +2x profit
    Three Matches: bet returns +3x profit
    No Match: lose that bet\n""")


def gameboard():
    """Display the gameboard symbol names."""
    for label in symbols:
        print(label)


def die():
    """Return one random symbol from the board."""
    row = random.randint(0, 1)
    col = random.randint(0, 2)
    return symbols[row][col]


def three_dice():
    """Return results of rolling three dice."""
    return [die(), die(), die()]


def money_prompt(prompt):
    """Prompt until the user enters a positive dollar amount."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Amount must be greater than 0.00.")
                continue
            return value
        except ValueError:
            print("Please enter a number.")


def round_prompt(prompt):
    """Prompt until the user enters a positive whole number."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value <= 0:
                print("Enter a whole number greater than 0.")
                continue
            return value
        except ValueError:
            print("Enter a whole number.")


def mode_prompt(prompt, valid_modes):
    """Prompt until the user enters one of the valid options."""
    while True:
        mode = input(prompt).strip().upper()
        if mode in valid_modes:
            return mode
        print(f"Enter one of these: {', '.join(valid_modes)}.")


def payout(bets, dice_results, print_detail=True):
    """Calculate total profit for one round based on the dice results."""
    total_return = 0.0
    total_profit = 0.0

    for choice, bet in bets.items():
        matches = dice_results.count(choice)

        if matches == 0:
            profit = -bet
            return_val = 0.0
            if print_detail:
                print(f"{choice}: bet ${bet:.2f} - 0 matches LOSE")
        else:
            profit = bet * matches
            return_val = bet + profit
            if print_detail:
                print(f"{choice}: bet ${bet:.2f} - {matches} matches (payout {matches}x) return ${return_val:.2f}")

        total_profit += profit
        total_return += return_val

    if print_detail:
        print(f"\nTOTAL RETURN: ${total_return:.2f}")
        print(f"TOTAL PROFIT: ${total_profit:.2f}\n")

    return round(total_profit, 2)


def game_setup():
    """Collect starting bankroll and user bet allocations."""
    print("\nBuild your betting strategy by placing bets on one or more symbols.")
    print("This strategy will be used for all sessions in this simulation run.\n")

    start_money = money_prompt("Enter your starting money: ")
    remaining_money = start_money
    usr_bets = {}

    while True:
        choice = input("Choose a symbol for your betting strategy (type X when done): ").strip().upper()

        if choice == "X":
            break

        if choice not in valid_choice:
            print("Not a valid choice. TRY AGAIN. Choices are: (DEER, GOURD, ROOSTER, FISH, CRAB, SHRIMP) ")
            continue

        bet = money_prompt(f"Bet amount for {choice}: ")
        if bet > remaining_money:
            print("You don't have enough money left to add more bets.")
            continue

        usr_bets[choice] = usr_bets.get(choice, 0) + bet
        remaining_money = round(remaining_money - bet, 2)

        print("Current bets:", usr_bets)
        print("Money remaining:", remaining_money)

    if not usr_bets:
        print("No bets placed.")
        return None, None

    return start_money, usr_bets


def run_round(bankroll, usr_bets, print_detail=True):
    """Run a single round and return updated bankroll, dice results, and profit."""
    dice_results = three_dice()
    if print_detail:
        print("Dice Results:", dice_results)
    profit = payout(usr_bets, dice_results, print_detail=print_detail)
    bankroll = round(bankroll + profit, 2)
    return bankroll, dice_results, profit


def run_session(start_money, usr_bets, max_rounds):
    """Run a session of repeated rounds until max rounds is reached or bankroll is too low to continue."""
    cost_per_round = sum(usr_bets.values())
    bankroll = start_money
    rounds_survived = 0

    for _ in range(max_rounds):
        if bankroll < cost_per_round:
            break
        bankroll, _, _ = run_round(bankroll, usr_bets, print_detail=False)
        rounds_survived += 1

    return rounds_survived, bankroll


def bet_symbols(usr_bets):
    """Convert the bet sheet into a string for CSV output."""
    return "|".join(f"{choice}:{usr_bets[choice]}" for choice in sorted(usr_bets.keys()))


def run_sim(start_money, usr_bets):
    """Run multiple simulation sessions and save the results to a CSV file."""
    cost_per_round = sum(usr_bets.values())
    if cost_per_round <= 0:
        print("No bets placed.\n")
        return

    max_rounds = round_prompt("How many rounds max per session? ")
    sessions = round_prompt("How many sessions to simulate? ")

    strat_name = input("Enter a name for this betting strategy: ").strip()
    if not strat_name:
        strat_name = "simulation"

    file_name = f"{strat_name}.csv"
    file_exists = os.path.exists(file_name)
    bet_symbol_names = bet_symbols(usr_bets)

    with open(file_name, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Session",
                "StrategyName",
                "StartingBankroll",
                "MaxRounds",
                "CostPerRound",
                "RoundsSurvived",
                "FinalBankroll",
                "BetSymbols"
            ])

        print(f"\n--- SIMULATION ---")
        print(f"Saving to: {file_name}")
        print(f"Sessions: {sessions}")
        print(f"Max rounds: {max_rounds}")
        print(f"Starting bankroll: ${start_money:.2f}")
        print(f"Cost per round: ${cost_per_round:.2f}")
        print(f"Bet symbols for strategy: {usr_bets}\n")

        for session_num in range(1, sessions + 1):
            rounds_survived, final_bankroll = run_session(start_money, usr_bets, max_rounds)
            writer.writerow([
                session_num,
                strat_name,
                start_money,
                max_rounds,
                cost_per_round,
                rounds_survived,
                round(final_bankroll, 2),
                bet_symbol_names
            ])

    print(f"\nSaved {sessions} sessions to {file_name}\n")


def main():
    print(logo)
    while True:
        mode = mode_prompt("INSTRUCTIONS, PLAY, or EXIT: ", {"INSTRUCTIONS", "PLAY", "EXIT"})

        if mode == "EXIT":
            break

        if mode == "INSTRUCTIONS":
            instructions()
            continue

        start_money, usr_bets = game_setup()
        if start_money is None:
            print("Returning to menu.\n")
            continue

        run_sim(start_money, usr_bets)


if __name__ == "__main__":
    main()