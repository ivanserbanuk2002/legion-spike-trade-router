from uuid import UUID, uuid4


def generate_id() -> UUID:
    return uuid4()
