from agents.group4.utils import *


class BiddingStrategy:
    """
        Bidding Strategy
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    my_offers: dict                         # Generated offers
    received_offers: list                   # Received offers

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress
        self.my_offers = dict()
        self.received_offers = []

    def receive_bid(self, bid: Bid, **kwargs):
        """
            This method will be called when a bid received.
        @param bid: Received bid.
        @param kwargs:
        @return: None
        """
        if bid is not None:
            self.received_offers.append(bid)

    def generate(self, last_generated_bid, **kwargs) -> Bid:
        """
            Generate a bid.
        @return: Bid will be offered.
        """
        # Time
        time = get_time(self.progress)
        opponent_model = kwargs["opponent_model"]

        if time < 0.3:
            # Target utility decreases linearly.
            target_utility = (-2/3) * time + 0.9
            # target_utility = 1. - time
            # Get the closest bid to Target Utility
            bid = get_bid_greater_than(self.profile, target_utility, opponent_model, self.my_offers)
            # print(time, target_utility, bid, get_utility(self.profile, bid))

        elif 0.3 <= time < 0.6:
            target_utility = 0.7
            opponent_model = kwargs["opponent_model"]
            bid = get_bid_greater_than(self.profile, target_utility, opponent_model, self.my_offers)
            # print(time, target_utility, bid, get_utility(self.profile, bid))

        else:
            target_utility = -0.75 * time + 1.15
            opponent_model = kwargs["opponent_model"]
            bid = get_bid_greater_than(self.profile, target_utility, opponent_model, self.my_offers)
            # print(time, target_utility, bid, get_utility(self.profile, bid))

        bid_util = get_utility(self.profile, bid)

        if len(self.received_offers) > 7:
            if time < 0.7 and random.random() < 0.5:
                mean_received_utility = 0
                for received_bid in self.received_offers[-3:]:
                    received_utility = get_utility(self.profile, received_bid)
                    mean_received_utility += received_utility

                mean_received_utility /= 3
                behavior_dependent_util = 1 - mean_received_utility
                behavior_bid = get_bid_greater_than(self.profile, behavior_dependent_util, opponent_model, self.my_offers)
                if behavior_dependent_util > bid_util:
                    bid = behavior_bid

            elif time >= 0.7:
                if random.random() < (2/3):
                    mean_received_utility = 0
                    for received_bid in self.received_offers[-3:]:
                        received_utility = get_utility(self.profile, received_bid)
                        mean_received_utility += received_utility

                    mean_received_utility /= 3
                    behavior_dependent_util = 1 - mean_received_utility
                    behavior_bid = get_bid_greater_than(self.profile, behavior_dependent_util, opponent_model,
                                                        self.my_offers)
                    if behavior_dependent_util > bid_util:
                        bid = behavior_bid
                else:
                    target_utility = 0.625
                    opponent_model = kwargs["opponent_model"]
                    bid = get_bid_greater_than(self.profile, target_utility, opponent_model, self.my_offers)

        if not bid in self.my_offers:
            self.my_offers[bid] = 1
        else:
            self.my_offers[bid] += 1

        return bid
