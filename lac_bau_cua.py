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
    print("Each round uses three dice. Each die has one of these six symbols:")
    print("Gourd (Bầu), Crab (Cua), Shrimp (Tôm), Fish (Cá), Rooster (Gà), Deer (Nai)\n")
    print("These symbols are represented on a 2 x 3 game board:")
    for label in symbols:
        print(label)
    print("\nPlace bets on one or more symbols. Winnings depend on how many dice match each symbol you bet on.")
    print("""
    Payouts:
    One Match: bet returns +1x profit
    Two Matches: bet returns +2x profit
    Three Matches: bet returns +3x profit
    No Match: lose that bet\n""")


def three_dice():
    dice_results = []
    for _ in range(3):
        row = random.randint(0, 1)
        col = random.randint(0, 2)
        dice_results.append(symbols[row][col])

    return dice_results


def money_prompt(prompt):
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
    while True:
        mode = input(prompt).strip().upper()
        if mode in valid_modes:
            return mode
        print(f"Enter one of these: {', '.join(valid_modes)}.")


#Calculate total profit for one round based on the dice results.
def payout(bets, dice_results, print_detail=True):
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


#Returns bet choices made with amount betted on
def bet_symbols(usr_bets):
    parts = []
    for choice in sorted(usr_bets):
        parts.append(f"{choice}:{usr_bets[choice]}")

    return "|".join(parts)


#Collect starting bankroll and user bet allocations.
def game_setup():
    print("\nBuild your betting strategy by placing bets on one or more symbols.")
    print("The same strategy will be used for every session in this simulation.\n")

    start_money = money_prompt("Enter your starting money: ")
    remaining_money = start_money
    usr_bets = {}

    while True:
        choice = input("Choose a symbol for your betting strategy (type X when done): ").strip().upper()

        if choice == "X":
            break

        if choice not in valid_choice:
            print(f"Not a valid choice. TRY AGAIN. Choices are: {', '.join(valid_choice)}.")
            continue

        bet = money_prompt(f"Bet amount for {choice}: ")
        if bet > remaining_money:
            print("You don't have enough money left to add more bets.")
            continue

        usr_bets[choice] = usr_bets.get(choice, 0) + bet
        remaining_money = round(remaining_money - bet, 2)

        print("Current bets:", bet_symbols(usr_bets))
        print(f"Money remaining: ${remaining_money:.2f}")

    if not usr_bets:
        print("No bets placed.")
        return None, None

    return start_money, usr_bets


#Run a single round and return updated bankroll, dice results, and profit.
def run_round(bankroll, usr_bets, print_detail=True):
    dice_results = three_dice()
    if print_detail:
        print("Dice Results:", dice_results)
    profit = payout(usr_bets, dice_results, print_detail=print_detail)
    bankroll = round(bankroll + profit, 2)
    return bankroll, dice_results, profit


#Run a session of repeated rounds until max rounds is reached or bankroll is too low to continue.
def run_session(start_money, usr_bets, max_rounds):
    cost_per_round = sum(usr_bets.values())
    bankroll = start_money
    rounds_survived = 0

    for _ in range(max_rounds):
        if bankroll < cost_per_round:
            break
        bankroll, _, _ = run_round(bankroll, usr_bets, print_detail=False)
        rounds_survived += 1

    return rounds_survived, bankroll


#Run multiple simulation sessions and save the results to a CSV file.
def run_sim(start_money, usr_bets):
    cost_per_round = sum(usr_bets.values())
    if cost_per_round <= 0:
        print("No bets placed.\n")
        return

    max_rounds = round_prompt("How many rounds max per session? ")
    sessions = round_prompt("How many sessions to simulate? ")

    strat_name = input("Enter a name for this betting strategy: ").strip()
    if not strat_name:
        strat_name = "simulation"

    filename = f"{strat_name}.csv"
    file_exists = os.path.exists(filename)
    bet_symbol_names = bet_symbols(usr_bets)

    with open(filename, mode="a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "Session",
                "Strategy_Name",
                "Starting_Bankroll",
                "Max_Rounds",
                "Cost_Per_Round",
                "Rounds_Survived",
                "Final_Bankroll",
                "Bet_Sheet"
            ])

        print("\n--- SIMULATION ---")
        print("Saving to:", filename)
        print("Sessions:", sessions)
        print("Max rounds:", max_rounds)
        print(f"Starting bankroll: ${start_money:.2f}")
        print(f"Cost per round: ${cost_per_round:.2f}")
        print("Bet symbols for strategy:", bet_symbol_names)

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

    print(f"\nSaved {sessions} sessions to {filename}\n")


print(logo)
while True:
    mode = mode_prompt("INSTRUCTIONS, SIM, or EXIT: ", {"INSTRUCTIONS", "SIM", "EXIT"})

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