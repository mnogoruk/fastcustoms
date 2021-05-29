def boxes_summary(boxes):
    volume = 0
    ldm = 0
    mass = 0
    for box in boxes:
        volume += box.volume
        ldm += box.ldm
        mass += box.mass
    return volume, ldm, mass


