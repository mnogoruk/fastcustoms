from .constants import LDM_PER_SQUARE


def ldm_from_size(length, width, height):
    return (length * width) / LDM_PER_SQUARE
