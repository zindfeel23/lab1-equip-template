import equipment
import valera_equip


def count_items(player):
    # сколько всего вещей у игрока: в инвентаре + в слотах
    ids = set()
    for item in player.inventory:
        ids.add(id(item))
    for item in player.slots.values():
        if item is not None:
            ids.add(id(item))
    return len(ids)


def make_player(**kwargs):
    return equipment.Player("тест", **kwargs)


# базовые вещи

def test_equip_moves_item():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)
    p.inventory.append(sword)

    assert equipment.equip(p, sword) is True
    assert sword not in p.inventory
    assert p.slots["right_hand"] is sword


def test_unequip_returns_item():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)
    p.inventory.append(sword)
    equipment.equip(p, sword)

    assert equipment.unequip(p, "right_hand") is True
    assert p.slots["right_hand"] is None
    assert sword in p.inventory


def test_unequip_empty_slot():
    p = make_player()
    assert equipment.unequip(p, "right_hand") is False


def test_equip_into_occupied_slot():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)
    axe = equipment.Item("топор", "right_hand", power=15)
    p.inventory.extend([sword, axe])
    equipment.equip(p, sword)

    assert equipment.equip(p, axe) is True
    assert p.slots["right_hand"] is axe
    assert sword in p.inventory


def test_level_requirement():
    p = make_player(level=1)
    sword = equipment.Item("меч", "right_hand", power=10, level_req=5)
    p.inventory.append(sword)

    assert equipment.equip(p, sword) is False
    assert sword in p.inventory
    assert p.slots["right_hand"] is None


def test_equip_not_in_inventory():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)

    assert equipment.equip(p, sword) is False
    assert p.slots["right_hand"] is None


# двуручное

def test_two_handed_power_once():
    p = make_player()
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    p.inventory.append(two)
    equipment.equip(p, two)

    assert equipment.total_power(p) == 50


def test_two_handed_frees_both_hands():
    p = make_player()
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    dagger = equipment.Item("кинжал", "right_hand", power=5)
    shield = equipment.Item("щит", "left_hand", power=4)
    p.inventory.extend([two, dagger, shield])
    equipment.equip(p, dagger)
    equipment.equip(p, shield)

    assert equipment.equip(p, two) is True
    assert dagger in p.inventory
    assert shield in p.inventory
    assert p.slots["right_hand"] is two
    assert p.slots["left_hand"] is None


def test_two_handed_unequip():
    p = make_player()
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    p.inventory.append(two)
    equipment.equip(p, two)

    assert equipment.unequip(p, "right_hand") is True
    assert p.slots["right_hand"] is None
    assert p.slots["left_hand"] is None
    assert two in p.inventory


def test_one_handed_into_two_handed():
    p = make_player()
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    dagger = equipment.Item("кинжал", "left_hand", power=5)
    p.inventory.extend([two, dagger])
    equipment.equip(p, two)

    assert equipment.equip(p, dagger) is True
    assert two in p.inventory
    assert p.slots["left_hand"] is dagger
    assert p.slots["right_hand"] is None


# сломанная вещь

def test_broken_item_false_in_bool():
    broken = equipment.Item("сломанный", "right_hand", power=10, durability=0)
    assert bool(broken) is False


def test_broken_item_equips_zero_power():
    p = make_player()
    broken = equipment.Item("сломанный", "right_hand", power=10, durability=0)
    p.inventory.append(broken)

    assert equipment.equip(p, broken) is True
    assert p.slots["right_hand"] is broken
    assert equipment.total_power(p) == 0


def test_broken_item_unequip():
    p = make_player()
    broken = equipment.Item("сломанный", "right_hand", power=10, durability=0)
    p.inventory.append(broken)
    equipment.equip(p, broken)

    assert equipment.unequip(p, "right_hand") is True
    assert p.slots["right_hand"] is None
    assert broken in p.inventory


def test_broken_item_not_lost():
    p = make_player()
    broken = equipment.Item("сломанный", "right_hand", power=10, durability=0)
    new = equipment.Item("новый", "right_hand", power=20)
    p.inventory.extend([broken, new])
    equipment.equip(p, broken)

    assert equipment.equip(p, new) is True
    assert p.slots["right_hand"] is new
    assert broken in p.inventory


# некуда вернуть

def test_full_inventory_refuse():
    p = make_player(capacity=3)
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    dagger = equipment.Item("кинжал", "right_hand", power=5)
    shield = equipment.Item("щит", "left_hand", power=4)
    junk1 = equipment.Item("хлам1", "head")
    junk2 = equipment.Item("хлам2", "body")
    p.inventory.extend([two, junk1, junk2])
    p.slots["right_hand"] = dagger
    p.slots["left_hand"] = shield
    before = count_items(p)

    assert equipment.equip(p, two) is False
    assert count_items(p) == before
    assert p.slots["right_hand"] is dagger
    assert p.slots["left_hand"] is shield
    assert two in p.inventory


def test_two_handed_with_room():
    p = make_player(capacity=4)
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    dagger = equipment.Item("кинжал", "right_hand", power=5)
    shield = equipment.Item("щит", "left_hand", power=4)
    junk1 = equipment.Item("хлам1", "head")
    junk2 = equipment.Item("хлам2", "body")
    p.inventory.extend([two, junk1, junk2])
    p.slots["right_hand"] = dagger
    p.slots["left_hand"] = shield

    assert equipment.equip(p, two) is True
    assert dagger in p.inventory
    assert shield in p.inventory
    assert p.slots["right_hand"] is two


# инвариант: вещи не создаются и не теряются

def test_conservation_invariant():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)
    axe = equipment.Item("топор", "right_hand", power=12)
    two = equipment.Item("двуручник", "right_hand", power=50, two_handed=True)
    dagger = equipment.Item("кинжал", "left_hand", power=5)
    shield = equipment.Item("щит", "left_hand", power=4)
    high = equipment.Item("высокий уровень", "head", level_req=99)
    p.inventory.extend([sword, axe, two, dagger, shield, high])
    start = count_items(p)

    # слот занят
    equipment.equip(p, sword)
    assert count_items(p) == start
    equipment.equip(p, axe)
    assert count_items(p) == start

    # двуручное освобождает обе руки
    equipment.equip(p, dagger)
    equipment.equip(p, shield)
    assert count_items(p) == start
    equipment.equip(p, two)
    assert count_items(p) == start
    equipment.unequip(p, "right_hand")
    assert count_items(p) == start

    # операция не прошла
    stranger = equipment.Item("чужой", "right_hand")
    assert equipment.equip(p, stranger) is False
    assert count_items(p) == start
    assert equipment.unequip(p, "head") is False
    assert count_items(p) == start
    assert equipment.equip(p, high) is False
    assert count_items(p) == start


# дюп валеры

def test_valera_dup():
    p = valera_equip.Player("тест")
    sword = valera_equip.Item("меч", "right_hand")
    p.inventory.append(sword)
    valera_equip.equip(p, sword)

    assert sword in p.inventory
    assert p.slots["right_hand"] is sword


def test_my_equip_no_dup():
    p = make_player()
    sword = equipment.Item("меч", "right_hand", power=10)
    p.inventory.append(sword)
    equipment.equip(p, sword)

    assert sword not in p.inventory
    assert p.slots["right_hand"] is sword
