def boxes_summary(boxes):
    volume = 0
    ldm = 0
    mass = 0
    for box in boxes:
        volume += box.volume * box.amount
        ldm += box.ldm * box.amount
        mass += box.mass * box.amount
    return volume, ldm, mass


