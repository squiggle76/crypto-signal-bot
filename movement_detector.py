from adaptive_threshold import AdaptiveThreshold

# создаём локальный экземпляр (или импортируй тот же, что в bot.py)
threshold_model = AdaptiveThreshold()

def is_sharp_movement(pair: str, price_changes: list[float]) -> bool:
    """
    Проверяет, превышает ли текущее изменение цены адаптивный порог.
    """
    if not price_changes or len(price_changes) < 3:
        return False

    current_speed = price_changes[-1]
    threshold_model.update(pair, price_changes[-2])
    threshold = threshold_model.get_threshold(pair)

    return current_speed > threshold
