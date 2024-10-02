"""
Define class
"""


class Protocol:
    """
    Class to represent a protocol
    """

    def __init__(self, name: str, definition: str) -> None:
        self.name = name
        self.t_awake_l: list[int] = []
        self.t_sleep_l: list[int] = []
        self.definition = definition

    def fill(self, t_awake_l, t_sleep_l) -> None:
        """
        Fill the protocol with t_awake_l and t_sleep_l
        """
        self.t_awake_l = t_awake_l
        self.t_sleep_l = t_sleep_l

    def time_sequence(self) -> list[int]:
        """
        Get time count for sleep-awake status
        """
        # sleep-awake status
        time_elapsed = 0
        time_count = []
        time_count.append(0)
        for i, _ in enumerate(self.t_awake_l):
            # print(i)
            # print(self.t_awake_l[i])
            time_elapsed = time_elapsed + self.t_awake_l[i]
            time_count.append(time_elapsed)
            time_elapsed = time_elapsed + self.t_sleep_l[i]
            time_count.append(time_elapsed)

        return time_count
