from fastapi import HTTPException
from bson import ObjectId


def object_id(value: str):
    if not ObjectId.is_valid(value):
        raise HTTPException(422, 'Invalid resource ID')
    return str(ObjectId(value))
