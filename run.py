import numpy as np
import pandas as pd
import argparse

def process_log(log):
    df = pd.read_csv(log)
    for index, row in df.iterrows():
        if row['entry'][:6] == "-- end":
            break
        df.drop(index, inplace=True)
    df = df.reindex(index=df.index[::-1])
    df.reset_index(inplace=True, drop=True)

    stats = {}
    hands_played = {}
    uncleaned_names = set(df[df['entry'].str.contains('player "')]['entry'].str.split('"').str[1].tolist())
    names = []
    for name in uncleaned_names:
        name = name.split('@')[0][:-1]
        stats[name] = {'VPIP': 0, 'PFR': 0, '3BET': 0, '4BET': 0, 'BLINDS': 0}
        hands_played[name] = 0
        names.append(name)

    hand_stacks = df[df['entry'].str.contains('Player stacks:')]['entry'].str.split('"').tolist()
    for hand in hand_stacks:
        for str in hand:
            str = str.split('@')[0][:-1]
            if str in hands_played:
                hands_played[str] += 1

    start_indices = df[df['entry'].str.contains('-- starting')].index
    end_indices = df[df['entry'].str.contains('-- ending')].index
    n_hands = len(start_indices)
    hands = []

    for i in range(len(start_indices)):
        hands.append(df[start_indices[i] + 1:end_indices[i]]['entry'].tolist())

    for hand in hands:
        raised = 0
        d = {}
        for name in names:
            d[name] = False

        for action in hand:
            if 'Flop' in action:
                break

            if 'posts a small' in action or 'posts a big' in action:
                list = action.split('@')

                for str in list:
                    if str[1:-1] in stats:
                        stats[str[1:-1]]['BLINDS'] += 1

            if 'raises' in action:
                raised += 1
                list = action.split('@')

                if raised == 1:
                    for str in list:
                        if str[1:-1] in stats:
                            stats[str[1:-1]]['PFR'] += 1

                if raised == 2:
                    for str in list:
                        if str[1:-1] in stats:
                            stats[str[1:-1]]['3BET'] += 1

                if raised == 3:
                    for str in list:
                        if str[1:-1] in stats:
                            stats[str[1:-1]]['4BET'] += 1

            if 'calls' in action or 'raises' in action:
                list = action.split('@')

                for str in list:
                    if str[1:-1] in stats:
                        if d[str[1:-1]] is False:
                            stats[str[1:-1]]['VPIP'] += 1
                            d[str[1:-1]] = True



    remove = []
    for name in stats.keys():
        if stats[name]['VPIP'] == 0:
            remove.append(name)
    [stats.pop(key) for key in remove]

    for name in stats.keys():
        stats[name]['VPIP'] /= hands_played[name]
        stats[name]['VPIP'] = round(stats[name]['VPIP'], 3)
        stats[name]['PFR'] /= hands_played[name]
        stats[name]['PFR'] = round(stats[name]['PFR'], 3)
        stats[name]['3BET'] /= hands_played[name]
        stats[name]['3BET'] = round(stats[name]['3BET'], 3)
        stats[name]['4BET'] /= hands_played[name]
        stats[name]['4BET'] = round(stats[name]['4BET'], 3)

    return stats

# python run.py ucsb_log1.csv
# Make sure not in the middle of a hand (delete current hand)
def main():
    parser = argparse.ArgumentParser(description='Poker Tracker')
    parser.add_argument('filename', type=str, help='Log Name')
    args = parser.parse_args()

    stats = process_log(args.filename)

    for key, value in stats.items():
        print(key)
        print(f"VPIP: {value['VPIP']}")
        print(f"PFR: {value['PFR']}")
        print(f"3BET: {value['3BET']}")
        print(f"4BET: {value['4BET']}")
        print()


if __name__ == "__main__":
    main()
