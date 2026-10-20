"""Экипировка. Новая система, без дюпа."""

SLOTS = ("head", "body", "right_hand", "left_hand", "ring_1", "ring_2")
HANDS = ("right_hand", "left_hand")


class Item:
    def __init__(self, name, slot, power=0, durability=100, level_req=1,
                 two_handed=False):
        self.name = name
        self.slot = slot
        self.power = power
        self.durability = durability
        self.level_req = level_req
        self.two_handed = two_handed

    def __bool__(self):
        return self.durability > 0

    def __repr__(self):
        return f"<{self.name} {self.slot} dur={self.durability}>"


class Player:
    def __init__(self, name, level=1, inventory=None, capacity=20):
        self.name = name
        self.level = level
        self.inventory = list(inventory) if inventory else []
        self.capacity = capacity
        self.slots = {slot: None for slot in SLOTS}

    def __repr__(self):
        return f"<{self.name} lvl={self.level} inv={len(self.inventory)}>"


def other_hand(hand):
    if hand == "right_hand":
        return "left_hand"
    return "right_hand"


def hand_item(player, hand):
    # что реально лежит в руке. двуручное лежит в своей руке, но занимает
    # обе, поэтому если рука пустая, смотрим соседнюю
    item = player.slots[hand]
    if item is not None:
        return item
    other = player.slots[other_hand(hand)]
    if other is not None and other.two_handed:
        return other
    return None


def equip(player, item):
    if item.slot not in SLOTS:
        return False
    if player.level < item.level_req:
        return False
    if item.two_handed and item.slot not in HANDS:
        return False
    if item not in player.inventory:
        return False

    # вещи, которые вернутся из слотов обратно в инвентарь
    back = []
    if item.two_handed:
        for h in HANDS:
            if player.slots[h] is not None:
                back.append(player.slots[h])
    elif item.slot in HANDS:
        cur = hand_item(player, item.slot)
        if cur is not None:
            back.append(cur)
    else:
        if player.slots[item.slot] is not None:
            back.append(player.slots[item.slot])

    # item уйдет из инвентаря, back вернется. если места нет, отказ
    if len(player.inventory) - 1 + len(back) > player.capacity:
        return False

    player.inventory.remove(item)

    # освобождаем слоты
    if item.two_handed:
        for h in HANDS:
            if player.slots[h] is not None:
                player.inventory.append(player.slots[h])
            player.slots[h] = None
    elif item.slot in HANDS:
        cur = hand_item(player, item.slot)
        if cur is not None:
            if cur.two_handed:
                player.slots["right_hand"] = None
                player.slots["left_hand"] = None
            else:
                player.slots[item.slot] = None
            player.inventory.append(cur)
    else:
        if player.slots[item.slot] is not None:
            player.inventory.append(player.slots[item.slot])
            player.slots[item.slot] = None

    player.slots[item.slot] = item
    return True


def unequip(player, slot):
    item = player.slots[slot]
    if item is None:
        return False
    if item.two_handed:
        player.slots["right_hand"] = None
        player.slots["left_hand"] = None
    else:
        player.slots[slot] = None
    player.inventory.append(item)
    return True


def total_power(player):
    total = 0
    for item in player.slots.values():
        if item is not None and item.durability > 0:
            total += item.power
    return total
