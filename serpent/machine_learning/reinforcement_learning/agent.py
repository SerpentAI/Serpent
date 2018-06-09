from serpent.config import config

from serpent.analytics_client import AnalyticsClient

from serpent.enums import InputControlTypes

from serpent.utilities import SerpentError


class Agent:

    def __init__(self, name, game_inputs=None, callbacks=None):
        self.name = name

        if not isinstance(game_inputs, list):
            raise SerpentError("'game_inputs' should be list...")

        # TODO: Support multiple actions
        self.game_inputs = game_inputs
        self.game_inputs_mappings = self._generate_game_inputs_mappings()

        self.callbacks = callbacks or dict()

        self.current_state = None

        self.current_reward = 0
        self.cumulative_reward = 0

        self.analytics_client = AnalyticsClient(project_key=config["analytics"]["topic"])

    def generate_actions(self, state, **kwargs):
        raise NotImplementedError()

    def observe(self, reward=0, terminal=False, **kwargs):
        if self.callbacks.get("before_observe") is not None:
            self.callbacks["before_observe"]()

        self.current_state = None

        self.current_reward = reward
        self.cumulative_reward += reward

        self.analytics_client.track(event_key="REWARD", data={"reward": self.current_reward, "total_reward": self.cumulative_reward})

        if terminal:
            self.analytics_client.track(event_key="TOTAL_REWARD", data={"reward": self.cumulative_reward})

        if self.callbacks.get("after_observe") is not None:
            self.callbacks["after_observe"]()

    def reset(self, **kwargs):
        self.current_state = None

        self.current_reward = 0
        self.cumulative_reward = 0

    def _generate_game_inputs_mappings(self):
        mappings = list()

        for game_inputs_item in self.game_inputs:
            if game_inputs_item["control_type"] == InputControlTypes.CONTINUOUS:
                mappings.append(None)
                continue

            mapping = dict()

            for index, key in enumerate(game_inputs_item["inputs"]):
                mapping[index] = key

            mappings.append(mapping)

        return mappings
