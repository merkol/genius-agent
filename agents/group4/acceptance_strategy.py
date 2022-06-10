from agents.template_agent.utils import *


class AcceptanceStrategy:
    """
        Acceptance Strategy
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime

    def __init__(self, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.profile = profile
        self.progress = progress

    def is_accepted(self, received_bid: Bid, generated_bid: Bid, **kwargs) -> bool:
        """
            Decide received_bid will be accepted, or not
        @param received_bid: Received Bid
        @param generated_bid: Generated Bid by Bidding Strategy if the agent will not accept.
        @return: Accepted or not, bool.
        """

        # If there is no received bid, do not accept.
        if received_bid is None:
            return False

        time = get_time(self.progress)

        received_utility = get_utility(self.profile, received_bid)
        generated_utility = get_utility(self.profile, generated_bid)

        # AC_Next

        if received_utility > 0.9:
            return True

        return generated_utility <= received_utility
