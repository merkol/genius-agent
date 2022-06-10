from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.DiscreteValueSet import DiscreteValueSet
from geniusweb.issuevalue.Domain import Domain
from geniusweb.issuevalue.Value import Value
from agents.template_agent.utils import *


class OpponentModel:
    """
        Opponent Model
    """
    profile: LinearAdditiveUtilitySpace
    progress: ProgressTime
    offers: list    # Received bids
    domain: Domain  # Agent's domain
    issues: dict    # Issues

    def __init__(self, domain: Domain, profile: LinearAdditiveUtilitySpace, progress: ProgressTime, **kwargs):
        self.domain = domain
        self.profile = profile
        self.progress = progress
        self.offers = []

        self.issues = {issue: Issue(values) for issue, values in domain.getIssuesValues().items()}
        init_weight = 1 / len(self.issues)
        for issue_name, issue_obj in self.issues.items():
            issue_obj.set_weight(init_weight)

        self.n = 0.1

    def normalize_issue_weights(self, total_weight):
        """
        If the total weights of the issues in this domain becomes larger than 1, we subtract the mean of the difference
        from each issue's weight. So, the new weights will sum up to 1.
        :param total_weight:
        :return:
        """
        if total_weight - 1 > 0.001:
            difference_per_issue = (total_weight - 1) / len(self.issues)
            for issue_name, issue_obj in self.issues.items():
                issue_obj.set_weight(issue_obj.get_weight() - difference_per_issue)


    def update(self, bid: Bid, **kwargs):
        """
            This method will be called when a bid received.
        @param bid: Received bid
        @return: None
        """

        # Add into offers list
        if bid is None:
            return

        if len(self.offers) > 0:
            last_offer = self.offers[-1]

            total_weight = 0.0
            for issue_name, issue_obj in self.issues.items():
                weight = issue_obj.get_weight()
                if bid.getValue(issue_name) == last_offer.getValue(issue_name):
                    weight = issue_obj.get_weight() + self.n
                    issue_obj.set_weight(weight)
                total_weight += weight

            self.normalize_issue_weights(total_weight)

        self.offers.append(bid)

        # Call each issue object with corresponding received value.
        for issue_name, issue_obj in self.issues.items():
            issue_obj.update(bid.getValue(issue_name), **kwargs)

        for issue_name, issue_obj in self.issues.items():
            issue_obj.update_value_weights(**kwargs)
            # print("value_weights", issue_obj.value_weights)
            # print("num_occurences", issue_obj.num_occurences)

        # for issue_name, issue_obj in self.issues.items():
        #     print(issue_name, issue_obj)

    def get_utility(self, bid: Bid) -> float:
        """
            This method calculates estimated utility.
        @param bid: The bid will be calculated.
        @return: Estimated Utility
        """
        if bid is None:
            return 0.0

        total = 0.0

        for issue_name, issue_obj in self.issues.items():
            total += issue_obj.get_utility(bid.getValue(issue_name))

        return total

class Issue:
    """
        This class can be used to estimate issue weight and value weights.
    """
    weight: float = 0.0    # Issue Weight
    value_weights: dict    # Value Weights
    num_occurences: dict

    def __init__(self, values: DiscreteValueSet, **kwargs):
        # Initial value weights are zero
        self.value_weights = {value: 0.0 for value in values}
        self.num_occurences = dict()
        self.max_occurences = -1

    def get_weight(self):
        return self.weight

    def set_weight(self, weight):
        """
        Setter of the issue object's weight.
        :param weight:
        :return:
        """
        self.weight = weight

    def update_value_weights(self, **kwargs):
        for value, occurences in self.num_occurences.items():
            self.value_weights[value] = occurences / self.max_occurences

    def update(self, value: Value, **kwargs):
        """
            This method will be called when a bid received.
        @param value: Received bid
        @return: None
        """
        if value is None:
            return

        if not value in self.num_occurences:
            self.num_occurences[value] = 1
        else:
            self.num_occurences[value] += 1

        if self.max_occurences < self.num_occurences[value]:
            self.max_occurences = self.num_occurences[value]

    def get_utility(self, value: Value) -> float:
        """
            Calculate estimated utility of the issue with value
        @param value: Value of Issue
        @return: Estimated Utility
        """
        if value is None:
            return 0.0

        return self.weight * self.value_weights[value]

    def __repr__(self):
        return f"weight: {self.weight}\nvalue_weights: {self.value_weights}"
