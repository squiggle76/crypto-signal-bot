class AdaptiveThreshold:
    def __init__(self):
        self.thresholds = {}

    def update(self, pair, value):
        # Простейшее скользящее среднее для демонстрации
        if pair in self.thresholds:
            self.thresholds[pair] = (self.thresholds[pair] * 0.8) + (value * 0.2)
        else:
            self.thresholds[pair] = value

    def get_threshold(self, pair):
        return self.thresholds.get(pair, 0.05)  # по умолчанию 0.05%