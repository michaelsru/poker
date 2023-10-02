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
        return f'{self.rank}{self.suit}'

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

    # Straight Flush & Royal Flush
    if flush_suit and is_straight:
        flush_cards = [card for card in all_cards if card.suit == flush_suit]
        straight_flush_cards = sorted([card for card in flush_cards if RANKS.index(card.rank) >= RANKS.index(last_rank) and RANKS.index(card.rank) <= RANKS.index(last_rank) + 4], key=lambda card: RANKS.index(card.rank), reverse=True)
        
        if straight_flush_cards[0].rank == 'A':
            return ('royal-flush', straight_flush_cards)
        return ('straight-flush', straight_flush_cards[0].rank, straight_flush_cards)

    # Four of a Kind
    for rank, count in rank_counts.items():
        if count == 4:
            cards = [card for card in all_cards if card.rank == rank]
            return ('four-of-a-kind', rank, cards + top_k_cards([rank], 1))

    # Full House
    three_kind = None
    for rank, count in rank_counts.items():
        if count == 3:
            three_kind = rank

    if three_kind:
        pairs = [rank for rank, count in rank_counts.items() if count == 2 or (count == 3 and rank != three_kind)]
        if pairs:
            top_pair = pairs[0]
            three_cards = [card for card in all_cards if card.rank == three_kind][:3]
            pair_cards = [card for card in all_cards if card.rank == top_pair][:2]
            return ('full-house', three_kind, top_pair, three_cards + pair_cards)

    # Flush
    if flush_suit:
        flush_cards = sorted([card for card in all_cards if card.suit == flush_suit], key=lambda card: RANKS.index(card.rank), reverse=True)[:5]
        return ('flush', flush_cards[0].rank, flush_cards)

    # Straight
    if is_straight:
        straight_cards = sorted([card for card in all_cards if RANKS.index(card.rank) >= RANKS.index(last_rank) and RANKS.index(card.rank) <= RANKS.index(last_rank) + 4], key=lambda card: RANKS.index(card.rank), reverse=True)
        return ('straight', straight_cards[0].rank, straight_cards)

    # Three of a Kind
    if three_kind:
        cards = [card for card in all_cards if card.rank == three_kind][:3]
        return ('three-of-a-kind', three_kind, cards + top_k_cards([three_kind], 2))

    # Two Pair
    pairs = [rank for rank, count in rank_counts.items() if count == 2]
    if len(pairs) == 2:
        top_pair_cards = [card for card in all_cards if card.rank == pairs[0]][:2]
        bottom_pair_cards = [card for card in all_cards if card.rank == pairs[1]][:2]
        return ('two-pair', pairs[0], pairs[1], top_pair_cards + bottom_pair_cards + top_k_cards(pairs, 1))

    # One Pair
    if len(pairs) == 1:
        pair_cards = [card for card in all_cards if card.rank == pairs[0]][:2]
        return ('one-pair', pairs[0], pair_cards + top_k_cards(pairs, 3))

    # High Card
    return ('high-card', all_cards[-1].rank, top_k_cards([], 5))

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

        def hand_ranking_value(hand_ranking):
            hand_order = ['high-card', 'one-pair', 'two-pair', 'three-of-a-kind', 'straight', 'flush', 'full-house', 'four-of-a-kind', 'straight-flush', 'royal-flush']
            return hand_order.index(hand_ranking[0])

        correct = False
        if hand_ranking_value(p1_eval) == hand_ranking_value(p2_eval) and answer == 't':
            correct = True
        elif hand_ranking_value(p1_eval) > hand_ranking_value(p2_eval) and answer == '1':
            correct = True
        elif hand_ranking_value(p1_eval) < hand_ranking_value(p2_eval) and answer == '2':
            correct = True

        if correct:
            if answer == '1':
                print(f"Correct! Player 1's winning hand is: {' '.join(map(str, p1_eval[-1]))}")
            elif answer == '2':
                print(f"Correct! Player 2's winning hand is: {' '.join(map(str, p2_eval[-1]))}")
            else:
                print("Correct! It's a tie!")
            print(f"Time taken: {end_time - start_time:.2f} seconds")
        else:
            print("Wrong! Try again.")

        play_again = input("Play again? (y/n): ")
        if play_again.lower() == 'n':
            break

if __name__ == "__main__":
    main()
