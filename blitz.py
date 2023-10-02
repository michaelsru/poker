#! /usr/bin/env python3

import random
import time

SUITS = ['♠', '♣', '♦', '♥']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __str__(self):
        if self.suit in ['♦', '♥']:
            return f'\033[91m{self.rank}{self.suit}\033[0m'  # Red color for diamonds and hearts
        return f'{self.rank}{self.suit}'

    def __lt__(self, other):
        return RANKS.index(self.rank) < RANKS.index(other.rank)

    def __gt__(self, other):
        return RANKS.index(self.rank) > RANKS.index(other.rank)

def deal_cards():
    deck = [Card(rank, suit) for rank in RANKS for suit in SUITS]
    random.shuffle(deck)

    player1_hand = [deck.pop(), deck.pop()]
    player2_hand = [deck.pop(), deck.pop()]
    community_cards = [deck.pop() for _ in range(5)]

    return player1_hand, player2_hand, community_cards

def evaluate_hand(hand, community_cards):
    all_cards = sorted(hand + community_cards, key=lambda card: (RANKS.index(card.rank), card.suit))
    rank_counts = {rank: 0 for rank in RANKS}
    
    for card in all_cards:
        rank_counts[card.rank] += 1

    def top_k_cards(excluded_ranks, k):
        return sorted([card for card in all_cards if card.rank not in excluded_ranks], key=lambda card: RANKS.index(card.rank), reverse=True)[:k]

    # Check for a flush
    suits = [card.suit for card in all_cards]
    flush_suit = None
    for suit in SUITS:
        if suits.count(suit) >= 5:
            flush_suit = suit
            break

    # Check for a straight
    consecutive = 0
    last_rank = None
    for rank in RANKS[::-1]:  # Start from Ace
        if rank_counts[rank] > 0:
            if last_rank and RANKS.index(last_rank) - RANKS.index(rank) == 1:
                consecutive += 1
            else:
                consecutive = 1
            last_rank = rank

        if consecutive == 5:
            break

    is_straight = consecutive >= 5

    # Assigning numerical values to hand ranks for easy comparison
    hand_rank_values = {
        'royal-flush': 9,
        'straight-flush': 8,
        'four-of-a-kind': 7,
        'full-house': 6,
        'flush': 5,
        'straight': 4,
        'three-of-a-kind': 3,
        'two-pair': 2,
        'one-pair': 1,
        'high-card': 0
    }

    # Adjusting return values for each hand type for tuple comparison
    if flush_suit and is_straight:
        flush_cards = [card for card in all_cards if card.suit == flush_suit]
        straight_flush_cards = sorted([card for card in flush_cards if RANKS.index(card.rank) >= RANKS.index(last_rank) and RANKS.index(card.rank) <= RANKS.index(last_rank) + 4], key=lambda card: RANKS.index(card.rank), reverse=True)
        
        if straight_flush_cards[0].rank == 'A':
            return (hand_rank_values['royal-flush'], straight_flush_cards)
        return (hand_rank_values['straight-flush'], RANKS.index(straight_flush_cards[0].rank), straight_flush_cards)

    for rank, count in rank_counts.items():
        if count == 4:
            cards = [card for card in all_cards if card.rank == rank]
            return (hand_rank_values['four-of-a-kind'], RANKS.index(rank), top_k_cards([rank], 1))

    # Full House
    three_kind = None
    for rank, count in rank_counts.items():
        if count == 3:
            three_kind = rank

    if three_kind:
        threes_cards = [card for card in all_cards if card.rank == three_kind][:3]
        pairs = [rank for rank, count in rank_counts.items() if count == 2]
        pair_cards = [card for card in all_cards if card.rank == pairs][:2]
        if pairs:
            top_pair = pairs[0]
            return (hand_rank_values['full-house'], RANKS.index(three_kind), RANKS.index(top_pair), threes_cards + pair_cards)

    if flush_suit:
        flush_cards = sorted([card for card in all_cards if card.suit == flush_suit], key=lambda card: RANKS.index(card.rank), reverse=True)[:5]
        return (hand_rank_values['flush'], [RANKS.index(card.rank) for card in flush_cards], flush_cards)

    if is_straight:
        straight_cards = sorted([card for card in all_cards if RANKS.index(card.rank) >= RANKS.index(last_rank) and RANKS.index(card.rank) <= RANKS.index(last_rank) + 4], key=lambda card: RANKS.index(card.rank), reverse=True)
        return (hand_rank_values['straight'], RANKS.index(straight_cards[0].rank), straight_cards)

    if three_kind:
        cards = [card for card in all_cards if card.rank == three_kind][:3]
        return (hand_rank_values['three-of-a-kind'], RANKS.index(three_kind), cards + top_k_cards([three_kind], 2))
    
    pairs = sorted([rank for rank, count in rank_counts.items() if count == 2], reverse=True)
    if len(pairs) == 2:
        top_pair_cards = [card for card in all_cards if card.rank == pairs[0]][:2]
        bottom_pair_cards = [card for card in all_cards if card.rank == pairs[1]][:2]
        return (hand_rank_values['two-pair'], RANKS.index(pairs[0]), RANKS.index(pairs[1]), top_pair_cards + bottom_pair_cards + top_k_cards(pairs, 1))

    if len(pairs) == 1:
        pair_cards = [card for card in all_cards if card.rank == pairs[0]][:2]
        return (hand_rank_values['one-pair'], RANKS.index(pairs[0]), pair_cards + top_k_cards(pairs, 3))

    return (hand_rank_values['high-card'], RANKS.index(all_cards[-1].rank), top_k_cards([], 5))

def main():
    while True:
        player1_hand, player2_hand, community_cards = deal_cards()

        print("Community Cards:", ' '.join(map(str, community_cards)))
        print("\nPlayer 1's Hand:", ' '.join(map(str, player1_hand)))
        print("Player 2's Hand:", ' '.join(map(str, player2_hand)))

        start_time = time.time()
        answer = input("Who wins? Enter '1' for Player 1, '2' for Player 2, 't' for tie: ")
        end_time = time.time()

        p1_eval = evaluate_hand(player1_hand, community_cards)
        p2_eval = evaluate_hand(player2_hand, community_cards)

        correct = False
        print(f'p1 eval: {p1_eval}')
        print(f'p2 eval: {p2_eval}')
        if p1_eval == p2_eval and answer == 't':
            correct = True
        elif p1_eval > p2_eval and answer == '1':
            correct = True
        elif p1_eval < p2_eval and answer == '2':
            correct = True

        if correct:
            print("\033[92mCorrect!\033[0m")
        else:
            print("\033[91mWrong!\033[0m")
        
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print(f"Player 1's hand is: {p1_eval[0]} {' '.join(map(str, p1_eval[-1]))}")
        print(f"Player 2's hand is: {p2_eval[0]} {' '.join(map(str, p2_eval[-1]))}")

        play_again = input("Play again? (y/n): ")
        if play_again.lower() == 'n':
            break

if __name__ == "__main__":
    main()
